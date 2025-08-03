#!/bin/bash
set -e

echo "=== LiteLLM Startup with OpenRouter Model Sync ==="

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r /app/requirements.txt

# Run model sync
echo "Syncing models from OpenRouter..."
python3 /app/update-models.py

# Validate that config was created
if [ ! -f "/app/config.yaml" ]; then
    echo "ERROR: Config file not found after sync!"
    exit 1
fi

echo "Model sync completed. Starting LiteLLM..."

# Start LiteLLM with the generated config
exec litellm --config /app/config.yaml --port 4000 --detailed_debug