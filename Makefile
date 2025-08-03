OPENWEBUI_DIR=stacks/openwebui
OPENWEBUI_ENV=$(OPENWEBUI_DIR)/.env

owui-up:
	docker compose -f $(OPENWEBUI_DIR)/docker-compose.yml --env-file $(OPENWEBUI_ENV) up -d

owui-down:
	docker compose -f $(OPENWEBUI_DIR)/docker-compose.yml --env-file $(OPENWEBUI_ENV) down

owui-logs:
	docker compose -f $(OPENWEBUI_DIR)/docker-compose.yml --env-file $(OPENWEBUI_ENV) logs -f

owui-ps:
	docker compose -f $(OPENWEBUI_DIR)/docker-compose.yml --env-file $(OPENWEBUI_ENV) ps