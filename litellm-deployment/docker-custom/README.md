# LiteLLM Docker Custom Deployment

This directory contains a flexible Docker setup for deploying LiteLLM proxy with dynamic configuration support.

## Features

- Dynamic configuration generation using Jinja2 templates
- Support for external or local PostgreSQL database
- Environment variable-based model configuration
- Automatic master key generation if not provided
- Docker Compose override for flexible deployment

## Quick Start

1. Copy `.env.example` to `.env` and configure your settings:
   ```bash
   cp .env.example .env
   ```

2. Run the start script:
   ```bash
   ./start.sh
   ```

The script will:
- Install required dependencies (Jinja2)
- Generate `litellm_config.yaml` from environment variables
- Set up database (local or external based on `DATABASE_URL`)
- Start the LiteLLM proxy service

## Environment Variables

### Required
- `LITELLM_MASTER_KEY`: Admin access key (auto-generated if not set)

### Optional Database
- `DATABASE_URL`: External PostgreSQL URL (if not set, local DB is used)

### Model Configuration
Configure models using environment variables:
```bash
LITELLM_MODEL_<NAME>="model=<model>,api_base=<base>,api_key=<key>"
```

Example:
```bash
LITELLM_MODEL_GPT4="model=openai/gpt-4,api_base=https://api.openai.com/v1,api_key=sk-xxx"
LITELLM_MODEL_CLAUDE="model=anthropic/claude-3,api_base=https://api.anthropic.com,api_key=sk-ant-xxx"
```

### Other Settings
- `LITELLM_PORT`: Proxy port (default: 4000)
- `USER_HEADER_NAME`: User identification header
- `DISABLE_END_USER_COST_TRACKING`: Disable cost tracking
- `LITELLM_EXTRA_HEADERS`: Additional headers for spend tracking
- See `.env.example` for all available options

## Usage

### Start services
```bash
./start.sh
```

### View logs
```bash
docker-compose logs -f
```

### Stop services
```bash
docker-compose down
```

### Clean up (including volumes)
```bash
docker-compose down -v
```

## Files

- `start.sh`: Main startup script
- `litellm_config.yaml.j2`: Jinja2 template for config generation
- `docker-compose.yml`: Base Docker Compose configuration
- `docker-compose.override.yml`: Generated override (do not edit)
- `.env.example`: Example environment variables
- `Dockerfile`: Custom LiteLLM image (optional)

## Database Configuration

### Using External Database
Set the `DATABASE_URL` environment variable:
```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

### Using Local Database
Leave `DATABASE_URL` empty, and the script will automatically set up a local PostgreSQL container.

## Advanced Configuration

### Router Settings
For load balancing and Redis integration:
```bash
LITELLM_ROUTER_STRATEGY=simple-shuffle
LITELLM_ROUTER_REDIS_HOST=localhost
LITELLM_ROUTER_REDIS_PORT=6379
LITELLM_ROUTER_REDIS_PASSWORD=your-redis-password
```

### Request Handling
```bash
LITELLM_MAX_PARALLEL_REQUESTS=100
LITELLM_NUM_RETRIES=3
LITELLM_REQUEST_TIMEOUT=600
```

## Troubleshooting

### Check if services are running
```bash
docker-compose ps
```

### View detailed logs
```bash
docker-compose logs litellm
docker-compose logs db  # if using local database
```

### Regenerate configuration
```bash
./start.sh
```

### Access the proxy
The proxy will be available at `http://localhost:4000` (or the port specified in `LITELLM_PORT`)

## Security Notes

- The master key is displayed during startup - save it securely
- Use strong passwords for database connections
- Keep API keys secure in environment variables
- Consider using Docker secrets for production deployments