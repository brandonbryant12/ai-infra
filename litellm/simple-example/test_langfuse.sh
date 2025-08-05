#!/bin/bash

# Convenience script to test Langfuse connection
# Usage: ./test_langfuse.sh

echo "Testing Langfuse connection..."
echo ""

# Source the LiteLLM environment variables
if [ -f "/root/ai-infra/stacks/litellm/.env" ]; then
    echo "Loading configuration from /root/ai-infra/stacks/litellm/.env"
    set -a  # automatically export all variables
    source /root/ai-infra/stacks/litellm/.env
    set +a  # turn off automatic export
else
    echo "Warning: /root/ai-infra/stacks/litellm/.env not found"
    echo "Using environment variables if already set"
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install langfuse
fi

# Run the test
python test_langfuse_connection.py