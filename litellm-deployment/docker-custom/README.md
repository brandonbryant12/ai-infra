# LiteLLM Docker Custom Deployment

A flexible Docker setup for deploying LiteLLM proxy with support for multiple model providers and dynamic configuration.

## Features

- Dynamic configuration generation using Jinja2 templates
- Support for multiple model providers (OpenAI, Anthropic, Ollama, vLLM, etc.)
- External or local PostgreSQL database support
- Environment variable-based model configuration
- Automatic master key generation
- Docker Compose deployment

## Quick Start

1. Configure your models using environment variables
2. Run the start script:
   ```bash
   ./start.sh
   ```

**Note**: At least one model must be configured or the script will exit with an error.

## Model Configuration

### Required Format
Configure models using environment variables with this pattern:
```bash
export LITELLM_MODEL_<NAME>="model=<provider>/<model>,api_base=<url>,api_key=<key>"
```

### Multiple Model Examples

#### Local Models (vLLM, Ollama, etc.)
```bash
# Qwen models via vLLM
export LITELLM_MODEL_QWEN3_72B="model=openai/Qwen/Qwen2.5-72B-Instruct,api_base=http://localhost:8000/v1,api_key=local-key"
export LITELLM_MODEL_QWEN3_32B="model=openai/Qwen/Qwen2.5-32B-Instruct,api_base=http://localhost:8001/v1,api_key=local-key"
export LITELLM_MODEL_QWEN3_14B="model=openai/Qwen/Qwen2.5-14B-Instruct,api_base=http://localhost:8002/v1,api_key=local-key"
export LITELLM_MODEL_QWEN3_7B="model=openai/Qwen/Qwen2.5-7B-Instruct,api_base=http://localhost:8003/v1,api_key=local-key"

# Llama models via Ollama
export LITELLM_MODEL_LLAMA3_70B="model=openai/llama3.1:70b,api_base=http://localhost:11434/v1,api_key=ollama"
export LITELLM_MODEL_LLAMA3_8B="model=openai/llama3.1:8b,api_base=http://localhost:11434/v1,api_key=ollama"
export LITELLM_MODEL_MISTRAL="model=openai/mistral:latest,api_base=http://localhost:11434/v1,api_key=ollama"
```

#### Cloud Providers
```bash
# OpenAI
export LITELLM_MODEL_GPT4="model=openai/gpt-4,api_base=https://api.openai.com/v1,api_key=sk-your-key"
export LITELLM_MODEL_GPT4_TURBO="model=openai/gpt-4-turbo-preview,api_base=https://api.openai.com/v1,api_key=sk-your-key"
export LITELLM_MODEL_GPT35="model=openai/gpt-3.5-turbo,api_base=https://api.openai.com/v1,api_key=sk-your-key"

# Anthropic
export LITELLM_MODEL_CLAUDE3_OPUS="model=anthropic/claude-3-opus-20240229,api_base=https://api.anthropic.com/v1,api_key=sk-ant-your-key"
export LITELLM_MODEL_CLAUDE3_SONNET="model=anthropic/claude-3-sonnet-20240229,api_base=https://api.anthropic.com/v1,api_key=sk-ant-your-key"
export LITELLM_MODEL_CLAUDE3_HAIKU="model=anthropic/claude-3-haiku-20240307,api_base=https://api.anthropic.com/v1,api_key=sk-ant-your-key"

# Azure OpenAI
export LITELLM_MODEL_AZURE_GPT4="model=azure/gpt-4,api_base=https://your-resource.openai.azure.com,api_key=your-azure-key"

# Google Vertex AI
export LITELLM_MODEL_GEMINI_PRO="model=vertex_ai/gemini-pro,api_base=https://us-central1-aiplatform.googleapis.com,api_key=your-vertex-key"

# Cohere
export LITELLM_MODEL_COMMAND="model=cohere/command,api_base=https://api.cohere.ai,api_key=your-cohere-key"
```

#### Custom/Self-Hosted Endpoints
```bash
# Text Generation Inference (HuggingFace)
export LITELLM_MODEL_FALCON="model=openai/tiiuae/falcon-40b,api_base=http://your-tgi-server:8080/v1,api_key=your-key"

# Custom OpenAI-compatible endpoints
export LITELLM_MODEL_CUSTOM1="model=openai/custom-model-1,api_base=https://your-api.com/v1,api_key=your-api-key"
export LITELLM_MODEL_CUSTOM2="model=openai/custom-model-2,api_base=https://another-api.com/v1,api_key=another-key"
```

### Batch Configuration Example
Create a `.env` file or shell script:
```bash
#!/bin/bash
# Local models
export LITELLM_MODEL_QWEN3_72B="model=openai/Qwen/Qwen2.5-72B-Instruct,api_base=http://localhost:8000/v1,api_key=local"
export LITELLM_MODEL_QWEN3_32B="model=openai/Qwen/Qwen2.5-32B-Instruct,api_base=http://localhost:8001/v1,api_key=local"

# Cloud models
export LITELLM_MODEL_GPT4="model=openai/gpt-4,api_base=https://api.openai.com/v1,api_key=$OPENAI_API_KEY"
export LITELLM_MODEL_CLAUDE="model=anthropic/claude-3-opus-20240229,api_base=https://api.anthropic.com/v1,api_key=$ANTHROPIC_API_KEY"

# Database (optional - uses local if not set)
export DATABASE_URL="postgresql://user:pass@host:5432/litellm"

# Run the deployment
./start.sh
```

## Core Environment Variables

### Required
- Model configuration (at least one `LITELLM_MODEL_*` variable)

### Optional
- `LITELLM_MASTER_KEY`: Admin access key (auto-generated if not set)
- `DATABASE_URL`: PostgreSQL connection string (local DB used if not set)
- `LITELLM_PORT`: Proxy port (default: 4000)
- `USER_HEADER_NAME`: User identification header (default: X-OpenWebUI-User-Email)
- `DISABLE_END_USER_COST_TRACKING`: Disable cost tracking (default: false)
- `LITELLM_EXTRA_HEADERS`: Additional headers for spend tracking

### Advanced Settings
```bash
# Router configuration
LITELLM_ROUTER_STRATEGY=simple-shuffle
LITELLM_ROUTER_REDIS_HOST=localhost
LITELLM_ROUTER_REDIS_PORT=6379
LITELLM_ROUTER_REDIS_PASSWORD=your-redis-password

# Request handling
LITELLM_MAX_PARALLEL_REQUESTS=100
LITELLM_NUM_RETRIES=3
LITELLM_REQUEST_TIMEOUT=600

# Logging
LITELLM_LOG_LEVEL=INFO
LITELLM_JSON_LOGS=true
```

## Usage

### Start Services
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

### Clean Everything (including database)
```bash
docker-compose down -v
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
    "model": "qwen3-72b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Files Generated

- `litellm_config.yaml`: Generated configuration (git-ignored)
- `docker-compose.override.yml`: Generated overrides (git-ignored)

## Troubleshooting

### No Models Configured Error
```bash
Error: No models configured!
You must set at least one model using environment variables.
```
Solution: Export at least one `LITELLM_MODEL_*` variable before running `./start.sh`

### Connection Refused
- Check if your model endpoints are accessible
- Verify API keys and URLs are correct
- Use `docker-compose logs litellm` to see detailed errors

### Database Issues
- For external DB: Verify `DATABASE_URL` is correct
- For local DB: Ensure port 5432 isn't already in use

## Security Notes

- Master key is displayed during startup - save it securely
- Store API keys in environment variables, not in code
- Use HTTPS for production deployments
- Consider using Docker secrets for sensitive data