#!/bin/bash

echo "Starting LiteLLM with OpenRouter and Langfuse..."

# Check if environment file exists
if [ ! -f "litellm.env" ]; then
    echo "Error: litellm.env file not found!"
    echo "Please copy litellm.env.example to litellm.env and add your API keys."
    exit 1
fi

# Check if config file exists
if [ ! -f "config.yaml" ]; then
    echo "Error: config.yaml file not found!"
    exit 1
fi

# Start the services
docker-compose up -d

# Check if the service started successfully
if [ $? -eq 0 ]; then
    echo "LiteLLM started successfully!"
    echo "Access the API at: http://localhost:4000"
    echo "Health check: http://localhost:4000/health"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
else
    echo "Failed to start LiteLLM. Check docker-compose logs for details."
    exit 1
fi