OPENWEBUI_DIR=stacks/openwebui
OPENWEBUI_ENV=$(OPENWEBUI_DIR)/.env

# Check if .env file exists and set compose command accordingly
ifeq ($(wildcard $(OPENWEBUI_ENV)),)
    COMPOSE_CMD=docker compose -f $(OPENWEBUI_DIR)/docker-compose.yml
else
    COMPOSE_CMD=docker compose -f $(OPENWEBUI_DIR)/docker-compose.yml --env-file $(OPENWEBUI_ENV)
endif

.PHONY: owui-up owui-down owui-logs owui-ps owui-restart owui-pull

owui-up:
	$(COMPOSE_CMD) up -d

owui-down:
	$(COMPOSE_CMD) down

owui-restart:
	$(COMPOSE_CMD) restart

owui-logs:
	$(COMPOSE_CMD) logs -f

owui-ps:
	$(COMPOSE_CMD) ps

owui-pull:
	$(COMPOSE_CMD) pull