# DevOps Local Testbed – Auth → Entitlement Flow

This repository provides a **reproducible local testbed** demonstrating:
- Multi-service deployment using Docker Compose
- Auth event processing → entitlement decision
- Deterministic smoke test
- Basic observability (logs + metrics)
- Debug bundle zip file generation for troubleshooting

---

## Architecture

**Services:**
- **operator-adapter** – this service simulates operator auth events
- **entitlement-server** – this processes events and stores entitlement state
- **redis** – it is the state storage

**Flow:**

operator-adapter
→ entitlement-server
→ redis


---

## Prerequisites

- Docker Desktop (with WSL2 on Windows)
- Docker Compose v2
- Make
- Git

Tested on:
- Ubuntu (WSL2)
- Works on macOS 

---

## One-Command Workflow

### Start the stack
make up

### Run smoke tests
make smoke

### View logs
make logs

### Stop stack
make down 

## Smoke Test Coverage
The smoke test validates:

Stack health (/healthz)

AUTH_SUCCESS → entitlement becomes ENABLED

AUTH_FAIL → entitlement becomes DISABLED

Same correlation_id appears in:

operator-adapter logs

entitlement-server logs

## Observability

Services emit logs with correlation IDs
Entitlement service exposes a /metrics endpoint in Prometheus format
No Prometheus server is deployed to keep the setup lightweight.

### CI PIPELINE

All trigress would be made to the main branch.
Added start up stack 
Added make smoke test
Added make stack down

### Debug Bundle

Generates a debug bundle for troubleshooting:
make debug-bundle

This produces:
debug-bundle.zip

### Notes

Docker Compose is used to keep the setup laptop-friendly

Flask development servers are used intentionally for simplicity

The goal is clarity and debuggability, not production hardening

### END

