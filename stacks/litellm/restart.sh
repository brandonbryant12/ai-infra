#!/bin/bash

set -e  # Exit on any error

echo "🔄 Restarting LiteLLM services..."

# Create the external network if it doesn't exist
echo "🌐 Checking/creating external network 'llmnet'..."
docker network ls | grep -q llmnet || docker network create llmnet

# Stop all services gracefully
echo "🛑 Stopping existing services..."
docker compose down --timeout 30

# Clean up any orphaned containers (optional, but helpful)
echo "🧹 Cleaning up any orphaned containers..."
docker compose rm -f 2>/dev/null || true

# Start all services
echo "🚀 Starting services..."
docker compose up -d

# Wait a moment for services to start
echo "⏳ Waiting for services to initialize..."
sleep 5

# Check service status
echo "📊 Service status:"
docker compose ps

echo "✅ Restart complete!"
echo "📝 Services available at:"
echo "   - LiteLLM Proxy: http://localhost:4000"
echo "   - PostgreSQL: localhost:5433"