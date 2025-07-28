# LiteLLM Docker Deployment

Deploy LiteLLM proxy gateway using the official Docker image without database requirements.

## Prerequisites

- Docker installed and running
- Access to your OpenWebUI instance
- Basic understanding of Docker commands

## Quick Start

### Step 1: Create Configuration File

Create `litellm_config.yaml`:

```yaml
model_list:
  - model_name: openwebui-default
    litellm_params:
      model: openai/openwebui-model
      api_base: http://myinstance.com/api
      api_key: your-openwebui-api-token

# See config/litellm_config.yaml for more examples
```

### Step 2: Run with Docker

```bash
docker run \
  -v $(pwd)/litellm_config.yaml:/app/config.yaml \
  -p 4000:4000 \
  ghcr.io/berriai/litellm:main-latest \
  --config /app/config.yaml
```

## Environment Variables

### Create .env File

```bash
# .env
OPENWEBUI_API_KEY=your-openwebui-api-token
OPENWEBUI_API_BASE=http://myinstance.com/api
```

### Run with Environment Variables

```bash
docker run \
  -v $(pwd)/litellm_config.yaml:/app/config.yaml \
  -e OPENWEBUI_API_KEY=$OPENWEBUI_API_KEY \
  -e OPENWEBUI_API_BASE=$OPENWEBUI_API_BASE \
  -p 4000:4000 \
  ghcr.io/berriai/litellm:main-latest \
  --config /app/config.yaml --detailed_debug
```

## Docker Compose

### Basic Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    container_name: litellm-proxy
    ports:
      - "4000:4000"
    volumes:
      - ./litellm_config.yaml:/app/config.yaml:ro
    environment:
      - OPENWEBUI_API_KEY=${OPENWEBUI_API_KEY}
      - OPENWEBUI_API_BASE=${OPENWEBUI_API_BASE}
    command: --config /app/config.yaml --detailed_debug
    restart: unless-stopped
```

### Production Setup

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  litellm:
    image: ghcr.io/berriai/litellm:main-stable
    container_name: litellm-proxy
    ports:
      - "127.0.0.1:4000:4000"  # Bind only to localhost
    volumes:
      - ./litellm_config.yaml:/app/config.yaml:ro
    environment:
      - OPENWEBUI_API_KEY=${OPENWEBUI_API_KEY}
      - OPENWEBUI_API_BASE=${OPENWEBUI_API_BASE}
    command: --config /app/config.yaml
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    # Security options
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
```

### Running with Docker Compose

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Advanced Configurations

### Using Cloud Storage for Config

If you can't mount files (e.g., AWS Fargate), use S3 or GCS:

```bash
# AWS S3
docker run --name litellm-proxy \
  -e AWS_ACCESS_KEY_ID=your_access_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret_key \
  -e AWS_DEFAULT_REGION=us-west-2 \
  -e LITELLM_CONFIG_BUCKET_NAME=my-bucket \
  -e LITELLM_CONFIG_BUCKET_OBJECT_KEY="configs/litellm_config.yaml" \
  -e LITELLM_CONFIG_BUCKET_TYPE="s3" \
  -p 4000:4000 \
  ghcr.io/berriai/litellm:main-latest

# Google Cloud Storage
docker run --name litellm-proxy \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/gcs-key.json \
  -v $(pwd)/gcs-key.json:/app/gcs-key.json:ro \
  -e LITELLM_CONFIG_BUCKET_NAME=my-bucket \
  -e LITELLM_CONFIG_BUCKET_OBJECT_KEY="configs/litellm_config.yaml" \
  -e LITELLM_CONFIG_BUCKET_TYPE="gcs" \
  -p 4000:4000 \
  ghcr.io/berriai/litellm:main-latest
```

### Network Configuration

#### Custom Network

```bash
# Create network
docker network create litellm-net

# Run with custom network
docker run -d \
  --name litellm-proxy \
  --network litellm-net \
  -v $(pwd)/litellm_config.yaml:/app/config.yaml:ro \
  -p 4000:4000 \
  ghcr.io/berriai/litellm:main-latest \
  --config /app/config.yaml
```

#### Behind a Proxy

```bash
docker run -d \
  --name litellm-proxy \
  -e HTTP_PROXY=http://proxy.company.com:8080 \
  -e HTTPS_PROXY=http://proxy.company.com:8080 \
  -e NO_PROXY=localhost,127.0.0.1 \
  -v $(pwd)/litellm_config.yaml:/app/config.yaml:ro \
  -p 4000:4000 \
  ghcr.io/berriai/litellm:main-latest \
  --config /app/config.yaml
```

## Container Management

### View Logs

```bash
# Follow logs
docker logs -f litellm-proxy

# Last 100 lines
docker logs --tail 100 litellm-proxy

# With timestamps
docker logs -t litellm-proxy
```

### Container Stats

```bash
# Resource usage
docker stats litellm-proxy

# Inspect container
docker inspect litellm-proxy
```

### Update Container

```bash
# Pull latest image
docker pull ghcr.io/berriai/litellm:main-latest

# Stop and remove old container
docker stop litellm-proxy
docker rm litellm-proxy

# Start with new image
docker run -d \
  --name litellm-proxy \
  -v $(pwd)/litellm_config.yaml:/app/config.yaml:ro \
  -p 4000:4000 \
  ghcr.io/berriai/litellm:main-latest \
  --config /app/config.yaml
```

## Testing

### Health Check

```bash
curl http://localhost:4000/health
```

### Test Request

```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openwebui-default",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs litellm-proxy

# Run interactively for debugging
docker run -it --rm \
  -v $(pwd)/litellm_config.yaml:/app/config.yaml \
  ghcr.io/berriai/litellm:main-latest \
  --config /app/config.yaml --detailed_debug
```

### Permission Issues

```bash
# Fix config file permissions
chmod 644 litellm_config.yaml

# Run with user mapping
docker run -d \
  --name litellm-proxy \
  --user $(id -u):$(id -g) \
  -v $(pwd)/litellm_config.yaml:/app/config.yaml:ro \
  -p 4000:4000 \
  ghcr.io/berriai/litellm:main-latest \
  --config /app/config.yaml
```

### Network Issues

```bash
# Test from inside container
docker exec litellm-proxy curl http://myinstance.com/api

# Check DNS
docker exec litellm-proxy nslookup myinstance.com
```

## Best Practices

1. **Use Specific Tags**: Instead of `latest`, use specific versions for production
2. **Resource Limits**: Set memory and CPU limits in production
3. **Health Checks**: Always configure health checks
4. **Logging**: Configure proper log rotation
5. **Security**: Use read-only mounts and run as non-root when possible

## Next Steps

- Set up reverse proxy (nginx/traefik) for SSL
- Configure monitoring and alerts
- Implement backup strategies for configuration
- Scale with Docker Swarm or Kubernetes