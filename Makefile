COMPOSE=docker compose

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down -v

logs:
	$(COMPOSE) logs -f adapter entitlement

smoke:
	bash tests/smoke.sh

debug-bundle:
	bash scripts/debug-bundle.sh

