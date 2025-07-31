#!/bin/bash
set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up PostgreSQL database for LiteLLM...${NC}"

# Configuration
CONTAINER_NAME="litellm-postgres"
DB_PORT="${DB_PORT:-5444}"
DB_USER="litellm"
DB_PASSWORD="litellm"
DB_NAME="litellm"

# Check if container already exists
if docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}PostgreSQL container '${CONTAINER_NAME}' already exists.${NC}"
    
    # Check if it's running
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "${GREEN}Container is already running.${NC}"
    else
        echo -e "${YELLOW}Starting existing container...${NC}"
        docker start ${CONTAINER_NAME}
    fi
else
    # Run new PostgreSQL container
    echo -e "${GREEN}Creating new PostgreSQL container...${NC}"
    docker run -d \
        --name ${CONTAINER_NAME} \
        -e POSTGRES_USER=${DB_USER} \
        -e POSTGRES_PASSWORD=${DB_PASSWORD} \
        -e POSTGRES_DB=${DB_NAME} \
        -p ${DB_PORT}:5432 \
        -v litellm-db-data:/var/lib/postgresql/data \
        --restart unless-stopped \
        postgres:16
fi

# Wait for database to be ready
echo -e "${YELLOW}Waiting for database to be ready...${NC}"
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker exec ${CONTAINER_NAME} pg_isready -U ${DB_USER} > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Database is ready!${NC}"
        break
    fi
    attempt=$((attempt + 1))
    echo -e "${YELLOW}Waiting for database... ($attempt/$max_attempts)${NC}"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}✗ Database failed to start within timeout${NC}"
    exit 1
fi

# Export DATABASE_URL
export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@localhost:${DB_PORT}/${DB_NAME}"

echo -e "\n${GREEN}=== Database Setup Complete ===${NC}"
echo -e "Container: ${YELLOW}${CONTAINER_NAME}${NC}"
echo -e "Port: ${YELLOW}${DB_PORT}${NC}"
echo -e "Database URL: ${YELLOW}$DATABASE_URL${NC}"
echo -e "\n${GREEN}To use this database with LiteLLM, run:${NC}"
echo -e "${YELLOW}export DATABASE_URL=\"$DATABASE_URL\"${NC}"
echo -e "${YELLOW}./start.sh${NC}"
echo -e "\n${GREEN}To stop the database:${NC}"
echo -e "${YELLOW}docker stop ${CONTAINER_NAME}${NC}"
echo -e "\n${GREEN}To remove the database:${NC}"
echo -e "${YELLOW}docker rm -f ${CONTAINER_NAME}${NC}"
echo -e "${YELLOW}docker volume rm litellm-db-data${NC} (to also remove data)"