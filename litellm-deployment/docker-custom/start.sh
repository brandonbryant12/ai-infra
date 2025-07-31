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

# Generate litellm_config.yaml using Docker with j2cli
echo -e "${GREEN}Generating litellm_config.yaml using j2cli...${NC}"

# Create JSON data for j2cli
JSON_DATA='{'

# Add models
JSON_DATA+='"models":['
MODEL_COUNT=0
for var in $(env | grep "^LITELLM_MODEL_" | sort); do
    MODEL_NAME=$(echo "$var" | cut -d'=' -f1 | sed 's/^LITELLM_MODEL_//' | tr '[:upper:]' '[:lower:]')
    MODEL_CONFIG=$(echo "$var" | cut -d'=' -f2-)
    
    # Parse model configuration
    MODEL=""
    API_BASE=""
    API_KEY=""
    
    IFS=',' read -ra PARAMS <<< "$MODEL_CONFIG"
    for param in "${PARAMS[@]}"; do
        key=$(echo "$param" | cut -d'=' -f1)
        value=$(echo "$param" | cut -d'=' -f2-)
        
        case "$key" in
            "model") MODEL="$value" ;;
            "api_base") API_BASE="$value" ;;
            "api_key") API_KEY="$value" ;;
        esac
    done
    
    if [ -n "$MODEL" ] && [ -n "$API_BASE" ] && [ -n "$API_KEY" ]; then
        if [ $MODEL_COUNT -gt 0 ]; then
            JSON_DATA+=","
        fi
        JSON_DATA+="{\"name\":\"$MODEL_NAME\",\"model\":\"$MODEL\",\"api_base\":\"$API_BASE\",\"api_key\":\"$API_KEY\"}"
        MODEL_COUNT=$((MODEL_COUNT + 1))
    fi
done

# Use default models if none configured
if [ $MODEL_COUNT -eq 0 ]; then
    JSON_DATA+='{"name":"qwen3-32b","model":"openai/qwen3-32b","api_base":"http://localhost:3000/v1","api_key":"sk-local"},'
    JSON_DATA+='{"name":"qwen3-14b","model":"openai/qwen3-14b","api_base":"http://localhost:3000/v1","api_key":"sk-local"}'
fi
JSON_DATA+='],'

# Add other settings
JSON_DATA+='"master_key":"'$LITELLM_MASTER_KEY'",'
JSON_DATA+='"user_header_name":"'$USER_HEADER_NAME'",'
JSON_DATA+='"database_url":"'$DATABASE_URL'",'
JSON_DATA+='"disable_end_user_cost_tracking":'$([ "$DISABLE_END_USER_COST_TRACKING" = "true" ] && echo "true" || echo "false")','
JSON_DATA+='"disable_end_user_cost_tracking_prometheus_only":'$([ "$DISABLE_END_USER_COST_TRACKING_PROMETHEUS_ONLY" = "true" ] && echo "true" || echo "false")','

# Add extra headers
JSON_DATA+='"extra_spend_tag_headers":['
if [ -n "$LITELLM_EXTRA_HEADERS" ]; then
    IFS=',' read -ra HEADERS <<< "$LITELLM_EXTRA_HEADERS"
    for i in "${!HEADERS[@]}"; do
        if [ $i -gt 0 ]; then
            JSON_DATA+=","
        fi
        JSON_DATA+='"'${HEADERS[$i]}'"'
    done
else
    JSON_DATA+='"'$USER_HEADER_NAME'"'
fi
JSON_DATA+=']'

# Close JSON
JSON_DATA+='}'

# Write JSON to temp file
JSON_FILE=$(mktemp)
echo "$JSON_DATA" > "$JSON_FILE"
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