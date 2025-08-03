# AI Infrastructure Management Makefile
# Central control for all services in the AI stack

# Configuration
SHELL := /bin/bash
.DEFAULT_GOAL := help

# Service directories
OPENWEBUI_DIR = stacks/openwebui
OPENWEBUI_ENV = $(OPENWEBUI_DIR)/.env
LITELLM_DIR = stacks/litellm
LITELLM_ENV = $(LITELLM_DIR)/.env

# Colors for output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Check if .env file exists and set compose command accordingly
ifeq ($(wildcard $(OPENWEBUI_ENV)),)
    OWUI_COMPOSE_CMD = docker compose -f $(OPENWEBUI_DIR)/docker-compose.yml
else
    OWUI_COMPOSE_CMD = docker compose -f $(OPENWEBUI_DIR)/docker-compose.yml --env-file $(OPENWEBUI_ENV)
endif

ifeq ($(wildcard $(LITELLM_ENV)),)
    LITELLM_COMPOSE_CMD = docker compose -f $(LITELLM_DIR)/docker-compose.yml
else
    LITELLM_COMPOSE_CMD = docker compose -f $(LITELLM_DIR)/docker-compose.yml --env-file $(LITELLM_ENV)
endif

# All services list
SERVICES := openwebui litellm

# Phony targets
.PHONY: help update pull start stop restart status logs rebuild clean
.PHONY: owui-up owui-down owui-logs owui-ps owui-restart owui-pull owui-rebuild
.PHONY: litellm-up litellm-down litellm-logs litellm-ps litellm-restart litellm-pull litellm-rebuild
.PHONY: network-create check-env

## Help Command
help: ## Show this help message
	@echo "$(CYAN)AI Infrastructure Management Commands$(NC)"
	@echo "$(CYAN)=====================================$(NC)"
	@echo ""
	@echo "$(GREEN)Central Commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -v grep | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Service-Specific Commands:$(NC)"
	@echo "  $(YELLOW)owui-*$(NC)          OpenWebUI commands (up, down, logs, etc.)"
	@echo "  $(YELLOW)litellm-*$(NC)       LiteLLM commands (up, down, logs, etc.)"
	@echo ""
	@echo "$(GREEN)Examples:$(NC)"
	@echo "  make update      # Pull latest and restart all services"
	@echo "  make status      # Check status of all services"
	@echo "  make logs        # Stream logs from all services"

## Central Management Commands
update: ## Pull latest code and restart all services
	@echo "$(CYAN)🔄 Updating AI Infrastructure...$(NC)"
	@echo "$(YELLOW)→ Pulling latest from main branch...$(NC)"
	@git pull origin main || (echo "$(RED)❌ Git pull failed$(NC)" && exit 1)
	@echo "$(GREEN)✅ Code updated$(NC)"
	@echo ""
	@$(MAKE) restart
	@echo ""
	@echo "$(GREEN)✅ All services updated and restarted!$(NC)"

pull: ## Pull latest Docker images for all services
	@echo "$(CYAN)🐳 Pulling latest Docker images...$(NC)"
	@echo "$(YELLOW)→ OpenWebUI...$(NC)"
	@$(OWUI_COMPOSE_CMD) pull
	@echo "$(YELLOW)→ LiteLLM...$(NC)"
	@$(LITELLM_COMPOSE_CMD) pull
	@echo "$(GREEN)✅ All images updated$(NC)"

start: network-create ## Start all services
	@echo "$(CYAN)🚀 Starting all services...$(NC)"
	@echo "$(YELLOW)→ Starting LiteLLM...$(NC)"
	@$(MAKE) litellm-up
	@echo "$(YELLOW)→ Starting OpenWebUI...$(NC)"
	@$(MAKE) owui-up
	@echo "$(GREEN)✅ All services started$(NC)"
	@echo ""
	@$(MAKE) status

stop: ## Stop all services
	@echo "$(CYAN)🛑 Stopping all services...$(NC)"
	@echo "$(YELLOW)→ Stopping OpenWebUI...$(NC)"
	@$(MAKE) owui-down
	@echo "$(YELLOW)→ Stopping LiteLLM...$(NC)"
	@$(MAKE) litellm-down
	@echo "$(GREEN)✅ All services stopped$(NC)"

restart: ## Restart all services
	@echo "$(CYAN)🔄 Restarting all services...$(NC)"
	@$(MAKE) stop
	@echo ""
	@$(MAKE) start

status: ## Show status of all services
	@echo "$(CYAN)📊 Service Status$(NC)"
	@echo "$(CYAN)=================$(NC)"
	@echo ""
	@echo "$(GREEN)OpenWebUI:$(NC)"
	@$(OWUI_COMPOSE_CMD) ps || true
	@echo ""
	@echo "$(GREEN)LiteLLM:$(NC)"
	@$(LITELLM_COMPOSE_CMD) ps || true
	@echo ""
	@echo "$(GREEN)Network:$(NC)"
	@docker network ls | grep llmnet || echo "  llmnet network not found"

logs: ## Stream logs from all services
	@echo "$(CYAN)📜 Streaming logs from all services (Ctrl+C to exit)...$(NC)"
	@echo "$(YELLOW)Use 'make owui-logs' or 'make litellm-logs' for individual service logs$(NC)"
	@echo ""
	@docker compose -f $(OPENWEBUI_DIR)/docker-compose.yml -f $(LITELLM_DIR)/docker-compose.yml logs -f

rebuild: clean ## Rebuild all services from scratch
	@echo "$(CYAN)🔨 Rebuilding all services...$(NC)"
	@echo "$(YELLOW)→ Pulling latest images...$(NC)"
	@$(MAKE) pull
	@echo "$(YELLOW)→ Rebuilding containers...$(NC)"
	@$(OWUI_COMPOSE_CMD) up -d --force-recreate --build
	@$(LITELLM_COMPOSE_CMD) up -d --force-recreate --build
	@echo "$(GREEN)✅ All services rebuilt$(NC)"
	@echo ""
	@$(MAKE) status

clean: ## Clean up containers, volumes (preserves data volumes)
	@echo "$(CYAN)🧹 Cleaning up...$(NC)"
	@echo "$(YELLOW)→ Stopping all services...$(NC)"
	@$(MAKE) stop
	@echo "$(YELLOW)→ Removing containers...$(NC)"
	@$(OWUI_COMPOSE_CMD) rm -f || true
	@$(LITELLM_COMPOSE_CMD) rm -f || true
	@echo "$(YELLOW)→ Pruning unused resources...$(NC)"
	@docker system prune -f
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

## Environment Management
check-env: ## Check environment setup
	@echo "$(CYAN)🔍 Checking environment...$(NC)"
	@echo ""
	@echo "$(GREEN)OpenWebUI:$(NC)"
	@if [ -f "$(OPENWEBUI_ENV)" ]; then \
		echo "  ✅ .env file exists"; \
		grep -E "^(OPENWEBUI_BASE_URL|WEBUI_SECRET_KEY)" $(OPENWEBUI_ENV) | sed 's/=.*/=***/' || true; \
	else \
		echo "  ❌ .env file missing - copy from .env.example"; \
	fi
	@echo ""
	@echo "$(GREEN)LiteLLM:$(NC)"
	@if [ -f "$(LITELLM_ENV)" ]; then \
		echo "  ✅ .env file exists"; \
		grep -E "^(OPENROUTER_API_KEY|LITELLM_MASTER_KEY)" $(LITELLM_ENV) | sed 's/=.*/=***/' || true; \
	else \
		echo "  ❌ .env file missing - copy from .env.sample"; \
	fi
	@echo ""
	@echo "$(GREEN)Docker:$(NC)"
	@docker --version || echo "  ❌ Docker not installed"
	@docker compose version || echo "  ❌ Docker Compose not installed"
	@echo ""
	@echo "$(GREEN)Network:$(NC)"
	@docker network ls | grep llmnet > /dev/null && echo "  ✅ llmnet network exists" || echo "  ❌ llmnet network missing"

## Network Management
network-create: ## Create shared Docker network
	@docker network ls | grep llmnet > /dev/null || \
		(echo "$(YELLOW)Creating shared network 'llmnet'...$(NC)" && docker network create llmnet)

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

owui-rebuild: ## Rebuild OpenWebUI container
	@echo "$(CYAN)🔨 Rebuilding OpenWebUI...$(NC)"
	$(OWUI_COMPOSE_CMD) up -d --force-recreate --build

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

litellm-rebuild: ## Rebuild LiteLLM container
	@echo "$(CYAN)🔨 Rebuilding LiteLLM...$(NC)"
	$(LITELLM_COMPOSE_CMD) up -d --force-recreate --build