from flask import Flask, jsonify
import requests
import uuid
import logging
import os

app = Flask(__name__)

ENTITLEMENT_URL = os.getenv("ENTITLEMENT_URL", "http://entitlement:8080")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

def send_event(event_type):
    correlation_id = str(uuid.uuid4())
    payload = {
        "msisdn": "9999999999",
        "imsi": "001010000000001",
        "event": event_type,
        "operator": "demo-op",
        "correlation_id": correlation_id
    }

    logging.info(f"Sending event {event_type} correlation_id={correlation_id}")

    requests.post(
        f"{ENTITLEMENT_URL}/v1/auth/event",
        json=payload,
        timeout=5
    )

    return correlation_id


@app.route("/simulate/auth-success", methods=["POST"])
def auth_success():
    cid = send_event("AUTH_SUCCESS")
    return jsonify({"status": "sent", "correlation_id": cid})


@app.route("/simulate/auth-fail", methods=["POST"])
def auth_fail():
    cid = send_event("AUTH_FAIL")
    return jsonify({"status": "sent", "correlation_id": cid})


@app.route("/healthz")
def health():
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

