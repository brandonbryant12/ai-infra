#!/bin/bash
set -e

echo "=== LiteLLM Startup ==="

# Set Python path to ensure custom modules can be imported
export PYTHONPATH=/app:$PYTHONPATH

# Install Python dependencies if requirements.txt exists
if [ -f "/app/requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r /app/requirements.txt
fi

# Validate that config exists
if [ ! -f "/app/config.yaml" ]; then
    echo "ERROR: Config file not found at /app/config.yaml!"
    exit 1
fi

echo "Starting LiteLLM..."

# Start LiteLLM with the config
exec litellm --config /app/config.yaml --port 4000 --detailed_debug