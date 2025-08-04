#!/bin/bash
# AI Infrastructure Setup Script
# Quick setup for new deployments

set -e

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}🚀 AI Infrastructure Setup${NC}"
echo -e "${CYAN}=========================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose found${NC}"

# Create network
echo -e "${YELLOW}Creating shared network...${NC}"
docker network create llmnet 2>/dev/null || echo "Network already exists"

# Setup environment files
echo -e "${YELLOW}Setting up environment files...${NC}"

# OpenWebUI
if [ ! -f "stacks/openwebui/.env" ]; then
    echo -e "${YELLOW}Creating OpenWebUI .env file...${NC}"
    cp stacks/openwebui/.env.example stacks/openwebui/.env
    echo -e "${YELLOW}⚠️  Please edit stacks/openwebui/.env and set:${NC}"
    echo "   - WEBUI_SECRET_KEY (generate with: openssl rand -hex 32)"
    echo "   - WEBUI_URL (e.g., https://ai.brandonbryant.io for production or http://localhost:3000 for local dev)"
else
    echo -e "${GREEN}✅ OpenWebUI .env exists${NC}"
fi

# LiteLLM
if [ ! -f "stacks/litellm/.env" ]; then
    echo -e "${YELLOW}Creating LiteLLM .env file...${NC}"
    cp stacks/litellm/.env.sample stacks/litellm/.env
    echo -e "${YELLOW}⚠️  Please edit stacks/litellm/.env and set:${NC}"
    echo "   - OPENROUTER_API_KEY (get from https://openrouter.ai/)"
    echo "   - LITELLM_MASTER_KEY (or keep default for development)"
else
    echo -e "${GREEN}✅ LiteLLM .env exists${NC}"
fi

# Langfuse
if [ ! -f "stacks/langfuse/.env" ]; then
    echo -e "${YELLOW}Creating Langfuse .env file...${NC}"
    cp stacks/langfuse/.env.example stacks/langfuse/.env
    echo -e "${YELLOW}⚠️  Please edit stacks/langfuse/.env and set:${NC}"
    echo "   - POSTGRES_PASSWORD, NEXTAUTH_SECRET, LANGFUSE_SALT (generate secrets)"
    echo "   - (Optional) LANGFUSE_INIT_* to auto-create project + keys on first boot"
    echo "   - Ensure LANGFUSE_URL (e.g., https://langfuse.brandonbryant.io)"
    echo -e "${YELLOW}After Langfuse boots, copy project keys into stacks/litellm/.env:${NC}"
    echo "   - LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST"
else
    echo -e "${GREEN}✅ Langfuse .env exists${NC}"
fi

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo "1. Edit the .env files as indicated above"
echo "2. Run: make start"
echo "3. Access OpenWebUI locally at http://localhost:3000 (dev) or in production at https://ai.brandonbryant.io"
echo "4. LiteLLM API is available at http://localhost:4000 (or https://litellm.brandonbryant.io if nginx configured)"
echo "5. Langfuse UI at http://localhost:3100 (or https://langfuse.brandonbryant.io if nginx configured)"
echo ""
echo -e "${CYAN}Useful commands:${NC}"
echo "  make status    - Check service status"
echo "  make logs      - View logs"
echo "  make update    - Update and restart services"
echo "  make help      - Show all commands"