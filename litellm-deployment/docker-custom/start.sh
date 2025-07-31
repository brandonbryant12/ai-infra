#!/bin/bash
set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting LiteLLM deployment setup...${NC}"

# Default values
LITELLM_MASTER_KEY="${LITELLM_MASTER_KEY:-sk-$(openssl rand -hex 32)}"
DATABASE_URL="${DATABASE_URL:-}"
USER_HEADER_NAME="${USER_HEADER_NAME:-X-OpenWebUI-User-Email}"
DISABLE_END_USER_COST_TRACKING="${DISABLE_END_USER_COST_TRACKING:-false}"
DISABLE_END_USER_COST_TRACKING_PROMETHEUS_ONLY="${DISABLE_END_USER_COST_TRACKING_PROMETHEUS_ONLY:-false}"

# Export all environment variables for docker run
export LITELLM_MASTER_KEY
export DATABASE_URL
export USER_HEADER_NAME
export DISABLE_END_USER_COST_TRACKING
export DISABLE_END_USER_COST_TRACKING_PROMETHEUS_ONLY

# Check if DATABASE_URL is provided
USE_EXTERNAL_DB=false
if [ -n "$DATABASE_URL" ]; then
    USE_EXTERNAL_DB=true
    echo -e "${GREEN}Using external database: ${DATABASE_URL}${NC}"
else
    DATABASE_URL="postgresql://litellm:litellm@db:5432/litellm"
    export DATABASE_URL
    echo -e "${YELLOW}No DATABASE_URL provided. Will use local PostgreSQL container.${NC}"
fi

# Generate litellm_config.yaml using Docker
echo -e "${GREEN}Generating litellm_config.yaml using Docker...${NC}"

# Create a temporary env file for docker run
ENV_FILE=$(mktemp)
trap "rm -f $ENV_FILE" EXIT

# Export all environment variables to the temp file
env | grep -E '^(LITELLM_|DATABASE_URL|USER_HEADER_NAME|DISABLE_)' > $ENV_FILE

# Run Python in Docker to generate the config
docker run --rm \
    -v "$(pwd):/app" \
    -w /app \
    --env-file "$ENV_FILE" \
    python:3.11-slim \
    bash -c "pip install --quiet jinja2 && python render_config.py"

# Check if config was generated
if [ ! -f "litellm_config.yaml" ]; then
    echo -e "${RED}Failed to generate litellm_config.yaml${NC}"
    exit 1
fi

# Create docker-compose override based on database configuration
if [ "$USE_EXTERNAL_DB" = true ]; then
    echo -e "${GREEN}Creating docker-compose.override.yml without database service...${NC}"
    cat > docker-compose.override.yml <<EOF
version: '3.8'

services:
  litellm:
    environment:
      - DATABASE_URL=$DATABASE_URL
      - LITELLM_MASTER_KEY=$LITELLM_MASTER_KEY
    depends_on: []
EOF
else
    echo -e "${GREEN}Using local database service...${NC}"
    # Create override file that ensures the db service is included
    cat > docker-compose.override.yml <<EOF
version: '3.8'

services:
  litellm:
    environment:
      - DATABASE_URL=$DATABASE_URL
      - LITELLM_MASTER_KEY=$LITELLM_MASTER_KEY
EOF
fi

# Display configuration summary
echo -e "\n${GREEN}=== Configuration Summary ===${NC}"
echo -e "Master Key: ${YELLOW}$LITELLM_MASTER_KEY${NC}"
echo -e "Database URL: ${YELLOW}$DATABASE_URL${NC}"

# Parse model count from the generated config
MODEL_COUNT=$(grep -c "model_name:" litellm_config.yaml || echo "0")
echo -e "Models configured: ${YELLOW}$MODEL_COUNT${NC}"
echo -e "User Header: ${YELLOW}$USER_HEADER_NAME${NC}"

# Start the services
echo -e "\n${GREEN}Starting Docker services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "\n${YELLOW}Waiting for services to start...${NC}"
sleep 5

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo -e "\n${GREEN}✓ LiteLLM proxy is running!${NC}"
    echo -e "Access the proxy at: ${YELLOW}http://localhost:4000${NC}"
    echo -e "Master Key: ${YELLOW}$LITELLM_MASTER_KEY${NC}"
    echo -e "\nTo view logs: ${YELLOW}docker-compose logs -f${NC}"
    echo -e "To stop services: ${YELLOW}docker-compose down${NC}"
else
    echo -e "\n${RED}✗ Failed to start services. Check logs with: docker-compose logs${NC}"
    exit 1
fi