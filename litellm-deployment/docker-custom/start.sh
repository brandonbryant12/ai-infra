#!/bin/bash
set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting LiteLLM deployment setup...${NC}"

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}Error: DATABASE_URL environment variable is not set!${NC}"
    echo -e "${YELLOW}Please set DATABASE_URL before running this script.${NC}"
    echo -e "${YELLOW}Example:${NC}"
    echo -e "${GREEN}export DATABASE_URL=\"postgresql://user:password@host:port/database\"${NC}"
    echo -e "\n${YELLOW}Or run ./setup-db.sh to start a local PostgreSQL database${NC}"
    exit 1
fi

# Check if models.yaml exists
if [ ! -f "models.yaml" ]; then
    echo -e "${RED}Error: models.yaml not found!${NC}"
    echo -e "${YELLOW}Please create a models.yaml file with your model configurations.${NC}"
    echo -e "${YELLOW}See models.yaml for an example.${NC}"
    exit 1
fi

# Default values
LITELLM_MASTER_KEY="${LITELLM_MASTER_KEY:-sk-$(openssl rand -hex 32)}"
USER_HEADER_NAME="${USER_HEADER_NAME:-X-OpenWebUI-User-Email}"
DISABLE_END_USER_COST_TRACKING="${DISABLE_END_USER_COST_TRACKING:-false}"
DISABLE_END_USER_COST_TRACKING_PROMETHEUS_ONLY="${DISABLE_END_USER_COST_TRACKING_PROMETHEUS_ONLY:-false}"

# Export all environment variables for docker run
export LITELLM_MASTER_KEY
export DATABASE_URL
export USER_HEADER_NAME
export DISABLE_END_USER_COST_TRACKING
export DISABLE_END_USER_COST_TRACKING_PROMETHEUS_ONLY

echo -e "${GREEN}Using database: ${DATABASE_URL}${NC}"

# Generate litellm_config.yaml using Docker with j2cli
echo -e "${GREEN}Generating litellm_config.yaml using j2cli...${NC}"

# Parse models.yaml and create JSON data for j2cli
# First, let's use a Python script to parse YAML and convert to JSON
PARSE_SCRIPT=$(mktemp)
cat > "$PARSE_SCRIPT" << 'EOF'
import yaml
import json
import os
import sys

try:
    with open('models.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    models = []
    if config and 'models' in config and config['models']:
        for model in config['models']:
            if isinstance(model, dict) and all(k in model for k in ['name', 'model', 'api_base', 'api_key']):
                # Expand environment variables in api_key
                api_key = model['api_key']
                if api_key.startswith('${') and api_key.endswith('}'):
                    env_var = api_key[2:-1]
                    api_key = os.environ.get(env_var, api_key)
                
                models.append({
                    'name': model['name'],
                    'model': model['model'],
                    'api_base': model['api_base'],
                    'api_key': api_key
                })
    
    if not models:
        print("ERROR: No valid models found in models.yaml", file=sys.stderr)
        sys.exit(1)
    
    # Create JSON data for j2cli
    json_data = {
        'models': models,
        'master_key': os.environ.get('LITELLM_MASTER_KEY', ''),
        'user_header_name': os.environ.get('USER_HEADER_NAME', 'X-OpenWebUI-User-Email'),
        'database_url': os.environ.get('DATABASE_URL', ''),
        'disable_end_user_cost_tracking': os.environ.get('DISABLE_END_USER_COST_TRACKING', 'false').lower() == 'true',
        'disable_end_user_cost_tracking_prometheus_only': os.environ.get('DISABLE_END_USER_COST_TRACKING_PROMETHEUS_ONLY', 'false').lower() == 'true',
        'extra_spend_tag_headers': [os.environ.get('USER_HEADER_NAME', 'X-OpenWebUI-User-Email')]
    }
    
    # Add extra headers if specified
    if 'LITELLM_EXTRA_HEADERS' in os.environ:
        json_data['extra_spend_tag_headers'] = os.environ['LITELLM_EXTRA_HEADERS'].split(',')
    
    print(json.dumps(json_data))
    
except Exception as e:
    print(f"ERROR: Failed to parse models.yaml: {e}", file=sys.stderr)
    sys.exit(1)
EOF

# Run the Python script to generate JSON
JSON_FILE=$(mktemp)
if ! python3 "$PARSE_SCRIPT" > "$JSON_FILE" 2>&1; then
    ERROR_MSG=$(cat "$JSON_FILE")
    echo -e "${RED}Failed to parse models.yaml:${NC}"
    echo -e "${RED}$ERROR_MSG${NC}"
    rm -f "$PARSE_SCRIPT" "$JSON_FILE"
    exit 1
fi

# Clean up parse script
rm -f "$PARSE_SCRIPT"

# Check if we have models
if grep -q '"models": \[\]' "$JSON_FILE"; then
    echo -e "${RED}Error: No models configured in models.yaml!${NC}"
    echo -e "${YELLOW}Please uncomment and configure at least one model in models.yaml${NC}"
    rm -f "$JSON_FILE"
    exit 1
fi

# Ensure cleanup on exit
trap "rm -f $JSON_FILE" EXIT

# Run j2cli to generate the config
docker run --rm \
    -v "$(pwd)/litellm_config.yaml.j2:/template.j2:ro" \
    -v "$JSON_FILE:/data.json:ro" \
    ckaserer/j2cli \
    j2 /template.j2 /data.json > litellm_config.yaml

# Check if config was generated
if [ ! -f "litellm_config.yaml" ] || [ ! -s "litellm_config.yaml" ]; then
    echo -e "${RED}Failed to generate litellm_config.yaml${NC}"
    exit 1
fi

# Create docker-compose override without database service
echo -e "${GREEN}Creating docker-compose.override.yml...${NC}"
cat > docker-compose.override.yml <<EOF
version: '3.8'

services:
  litellm:
    environment:
      - DATABASE_URL=$DATABASE_URL
      - LITELLM_MASTER_KEY=$LITELLM_MASTER_KEY
    depends_on: []
EOF

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
docker-compose up -d litellm

# Wait for services to be ready
echo -e "\n${YELLOW}Waiting for services to start...${NC}"
sleep 5

# Check if services are running
if docker-compose ps litellm | grep -q "Up"; then
    echo -e "\n${GREEN}✓ LiteLLM proxy is running!${NC}"
    echo -e "Access the proxy at: ${YELLOW}http://localhost:4000${NC}"
    echo -e "Master Key: ${YELLOW}$LITELLM_MASTER_KEY${NC}"
    echo -e "\nTo view logs: ${YELLOW}docker-compose logs -f litellm${NC}"
    echo -e "To stop services: ${YELLOW}docker-compose down${NC}"
else
    echo -e "\n${RED}✗ Failed to start services. Check logs with: docker-compose logs litellm${NC}"
    exit 1
fi