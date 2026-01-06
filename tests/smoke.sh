#!/usr/bin/env bash
set -e

ADAPTER_URL="http://localhost:8080"
ENTITLEMENT_URL="http://localhost:8081"
IMSI="001010000000001"

echo "Waiting for entitlement health..."
until curl -sf ${ENTITLEMENT_URL}/healthz > /dev/null; do
  sleep 1
done
echo "Entitlement is healthy"

echo "Trigger AUTH_SUCCESS"
CID_SUCCESS=$(curl -s -X POST ${ADAPTER_URL}/simulate/auth-success | jq -r .correlation_id)

sleep 1

STATE=$(curl -s ${ENTITLEMENT_URL}/v1/entitlement/${IMSI} | jq -r .entitlement)
if [ "$STATE" != "ENABLED" ]; then
  echo "Expected ENABLED, got $STATE"
  exit 1
fi
echo "Entitlement ENABLED confirmed"

echo "Trigger AUTH_FAIL"
CID_FAIL=$(curl -s -X POST ${ADAPTER_URL}/simulate/auth-fail | jq -r .correlation_id)

sleep 1

STATE=$(curl -s ${ENTITLEMENT_URL}/v1/entitlement/${IMSI} | jq -r .entitlement)
if [ "$STATE" != "DISABLED" ]; then
  echo "Expected DISABLED, got $STATE"
  exit 1
fi
echo "Entitlement DISABLED confirmed"

echo "Verifying correlation IDs in logs"

docker compose logs adapter | grep $CID_SUCCESS
docker compose logs entitlement | grep $CID_SUCCESS

docker compose logs adapter | grep $CID_FAIL
docker compose logs entitlement | grep $CID_FAIL

echo "Smoke tests PASSED"

