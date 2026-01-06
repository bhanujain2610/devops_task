from flask import Flask, request, jsonify
import redis
import logging
import os
import time

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = 6379

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# Metrics (simple in-memory counters)
auth_success = 0
auth_fail = 0


@app.route("/v1/auth/event", methods=["POST"])
def auth_event():
    global auth_success, auth_fail

    start = time.time()
    data = request.json

    imsi = data["imsi"]
    event = data["event"]
    correlation_id = data["correlation_id"]

    enabled = event == "AUTH_SUCCESS"

    r.set(f"entitlement:{imsi}", "ENABLED" if enabled else "DISABLED")
    r.lpush(f"events:{imsi}", str(data))
    r.ltrim(f"events:{imsi}", 0, 19)

    if enabled:
        auth_success += 1
    else:
        auth_fail += 1

    logging.info(
        f"Auth event processed imsi={imsi} "
        f"event={event} correlation_id={correlation_id}"
    )

    latency = time.time() - start
    return jsonify({"status": "ok", "latency_ms": int(latency * 1000)})


@app.route("/v1/entitlement/<imsi>")
def get_entitlement(imsi):
    state = r.get(f"entitlement:{imsi}") or "UNKNOWN"
    return jsonify({"imsi": imsi, "entitlement": state})


@app.route("/healthz")
def health():
    try:
        r.ping()
        return "ok", 200
    except Exception:
        return "redis not reachable", 500


@app.route("/metrics")
def metrics():
    return f"""
# HELP auth_events_total Total auth events
# TYPE auth_events_total counter
auth_events_total{{result="success"}} {auth_success}
auth_events_total{{result="fail"}} {auth_fail}
""", 200, {"Content-Type": "text/plain; version=0.0.4"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

