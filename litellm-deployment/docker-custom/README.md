# LiteLLM Docker Custom Deployment

A flexible Docker setup for deploying LiteLLM proxy with support for multiple model providers and dynamic configuration.

## Features

- Environment-based model configuration via `litellm.env` file
- Dynamic configuration generation using Jinja2 templates
- Support for multiple model providers (OpenAI, Anthropic, Ollama, vLLM, etc.)
- Separate database setup with Docker
- Automatic master key generation
- Environment variable substitution in API keys

## Quick Start

1. **Set up the database** (optional - for local PostgreSQL):
   ```bash
   ./setup-db.sh
   # Add the DATABASE_URL to your litellm.env file
   ```

   Or use an external database by adding to `litellm.env`:
   ```bash
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

2. **Configure your models** in `litellm.env`:
   ```bash
   # Example model configuration
   LITELLM_MODEL_GPT4=model=openai/gpt-4,api_base=https://api.openai.com/v1,api_key=${OPENAI_API_KEY}
   ```

3. **Run the start script**:
   ```bash
   ./start.sh
   ```

## Model Configuration

Models are configured in the `litellm.env` file using environment variables.

### Configuration Format

Edit `litellm.env` to add your models:

```bash
LITELLM_MODEL_<NAME>=model=<provider/model-id>,api_base=<api-endpoint>,api_key=<api-key>
```

### Example Configurations

#### Local Models (vLLM, Ollama, etc.)
```bash
# Qwen models via vLLM
LITELLM_MODEL_QWEN3_72B=model=openai/Qwen/Qwen2.5-72B-Instruct,api_base=http://localhost:8000/v1,api_key=local-key
LITELLM_MODEL_QWEN3_32B=model=openai/Qwen/Qwen2.5-32B-Instruct,api_base=http://localhost:8001/v1,api_key=local-key

# Llama models via Ollama  
LITELLM_MODEL_LLAMA3_70B=model=openai/llama3.1:70b,api_base=http://localhost:11434/v1,api_key=ollama
LITELLM_MODEL_MISTRAL=model=openai/mistral:latest,api_base=http://localhost:11434/v1,api_key=ollama
```

#### Cloud Providers
```bash
# OpenAI
LITELLM_MODEL_GPT4=model=openai/gpt-4,api_base=https://api.openai.com/v1,api_key=${OPENAI_API_KEY}
LITELLM_MODEL_GPT35_TURBO=model=openai/gpt-3.5-turbo,api_base=https://api.openai.com/v1,api_key=${OPENAI_API_KEY}

# Anthropic
LITELLM_MODEL_CLAUDE3_OPUS=model=anthropic/claude-3-opus-20240229,api_base=https://api.anthropic.com/v1,api_key=${ANTHROPIC_API_KEY}
LITELLM_MODEL_CLAUDE3_SONNET=model=anthropic/claude-3-sonnet-20240229,api_base=https://api.anthropic.com/v1,api_key=${ANTHROPIC_API_KEY}

# Azure OpenAI
LITELLM_MODEL_AZURE_GPT4=model=azure/gpt-4,api_base=https://your-resource.openai.azure.com,api_key=${AZURE_API_KEY}

# Google Vertex AI
LITELLM_MODEL_GEMINI_PRO=model=vertex_ai/gemini-pro,api_base=https://us-central1-aiplatform.googleapis.com,api_key=${VERTEX_API_KEY}
```

#### Custom/Self-Hosted Endpoints
```bash
# Text Generation Inference (HuggingFace)
LITELLM_MODEL_FALCON_40B=model=openai/tiiuae/falcon-40b,api_base=http://your-tgi-server:8080/v1,api_key=your-key

# Custom OpenAI-compatible endpoints
LITELLM_MODEL_CUSTOM1=model=openai/custom-model-1,api_base=https://your-api.com/v1,api_key=${CUSTOM_API_KEY}
```

### Using Environment Variables

You can use environment variables in the `api_key` field by using the format `${VARIABLE_NAME}`:

```bash
LITELLM_MODEL_GPT4=model=openai/gpt-4,api_base=https://api.openai.com/v1,api_key=${OPENAI_API_KEY}
```

Then set the environment variable in `litellm.env`:
```bash
OPENAI_API_KEY=sk-your-actual-api-key
```

## Database Setup

### Option 1: Local PostgreSQL with Docker

Run the setup script to start a PostgreSQL container:

```bash
./setup-db.sh
```

This will:
- Start a PostgreSQL container named `litellm-postgres`
- Use port 5444 (configurable with `DB_PORT` env var)
- Display the DATABASE_URL to export

Then export the DATABASE_URL:
```bash
export DATABASE_URL="postgresql://litellm:litellm@localhost:5444/litellm"
```

### Option 2: External Database

Simply set your DATABASE_URL:
```bash
export DATABASE_URL="postgresql://user:password@host:port/database"
```

## Environment Variables

### Required
- `DATABASE_URL`: PostgreSQL connection string

### Optional
- `LITELLM_MASTER_KEY`: Admin access key (auto-generated if not set)
- `LITELLM_PORT`: Proxy port (default: 4000)
- `USER_HEADER_NAME`: User identification header (default: X-OpenWebUI-User-Email)
- `DISABLE_END_USER_COST_TRACKING`: Disable cost tracking (default: false)
- `DISABLE_END_USER_COST_TRACKING_PROMETHEUS_ONLY`: Prometheus-only cost tracking (default: false)
- `LITELLM_EXTRA_HEADERS`: Additional headers for spend tracking (comma-separated)

## Usage

### Start Services

1. Ensure database is running and DATABASE_URL is set
2. Configure your models in `models.yaml`
3. Run:
   ```bash
   ./start.sh
   ```

### View Logs
```bash
docker-compose logs -f litellm
```

### Stop Services
```bash
docker-compose down
```

### Stop Database
```bash
docker stop litellm-postgres
```

### Clean Everything
```bash
# Stop and remove LiteLLM
docker-compose down -v

# Stop and remove database
docker rm -f litellm-postgres
docker volume rm litellm-db-data
```

## Testing Your Configuration

Once running, test your endpoints:

```bash
# List available models
curl http://localhost:4000/v1/models \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"

# Test a specific model
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Files

- `litellm.env`: Environment configuration file (you create this)
- `setup-db.sh`: Database setup script
- `start.sh`: Main startup script
- `docker-compose.yml`: Docker services definition
- `litellm_config.yaml.j2`: Jinja2 template for LiteLLM config
- `litellm_config.yaml`: Generated configuration (git-ignored)
- `docker-compose.override.yml`: Generated overrides (git-ignored)

## Troubleshooting

### No Models Configured Error
```
Error: No models configured!
```
Solution: Edit `litellm.env` and add at least one LITELLM_MODEL_* configuration

### Database Connection Error
```
Error: DATABASE_URL not set in litellm.env!
```
Solution: Run `./setup-db.sh` and add the DATABASE_URL to litellm.env, or set your own

### Configuration Parse Error
Check your `litellm.env` syntax. Each model needs: model, api_base, and api_key parameters

### Connection Refused
- Verify your model endpoints are accessible
- Check API keys are correct
- Use `docker-compose logs litellm` to see detailed errors

## Security Notes

- Master key is displayed during startup - save it securely
- Store API keys as environment variables in litellm.env, not directly
- Use HTTPS for production deployments
- The `.gitignore` should include `litellm.env`, `litellm_config.yaml` and `docker-compose.override.yml`