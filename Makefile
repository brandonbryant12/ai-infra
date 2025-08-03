OPENWEBUI_DIR=stacks/openwebui
OPENWEBUI_ENV=$(OPENWEBUI_DIR)/.env
LITELLM_DIR=stacks/litellm
LITELLM_ENV=$(LITELLM_DIR)/.env

# Check if .env file exists and set compose command accordingly
ifeq ($(wildcard $(OPENWEBUI_ENV)),)
    OWUI_COMPOSE_CMD=docker compose -f $(OPENWEBUI_DIR)/docker-compose.yml
else
    OWUI_COMPOSE_CMD=docker compose -f $(OPENWEBUI_DIR)/docker-compose.yml --env-file $(OPENWEBUI_ENV)
endif

ifeq ($(wildcard $(LITELLM_ENV)),)
    LITELLM_COMPOSE_CMD=docker compose -f $(LITELLM_DIR)/docker-compose.yml
else
    LITELLM_COMPOSE_CMD=docker compose -f $(LITELLM_DIR)/docker-compose.yml --env-file $(LITELLM_ENV)
endif

.PHONY: owui-up owui-down owui-logs owui-ps owui-restart owui-pull
.PHONY: litellm-up litellm-down litellm-logs litellm-ps litellm-restart litellm-pull

# OpenWebUI commands
owui-up:
	$(OWUI_COMPOSE_CMD) up -d

owui-down:
	$(OWUI_COMPOSE_CMD) down

owui-restart:
	$(OWUI_COMPOSE_CMD) restart

owui-logs:
	$(OWUI_COMPOSE_CMD) logs -f

owui-ps:
	$(OWUI_COMPOSE_CMD) ps

owui-pull:
	$(OWUI_COMPOSE_CMD) pull

# LiteLLM commands
litellm-up:
	$(LITELLM_COMPOSE_CMD) up -d

litellm-down:
	$(LITELLM_COMPOSE_CMD) down

litellm-restart:
	$(LITELLM_COMPOSE_CMD) restart

litellm-logs:
	$(LITELLM_COMPOSE_CMD) logs -f

litellm-ps:
	$(LITELLM_COMPOSE_CMD) ps

litellm-pull:
	$(LITELLM_COMPOSE_CMD) pull