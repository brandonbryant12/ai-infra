# LiteLLM Docker Custom Deployment

A flexible Docker setup for deploying LiteLLM proxy with support for multiple model providers and dynamic configuration.

## Features

- YAML-based model configuration (models.yaml)
- Dynamic configuration generation using Jinja2 templates
- Support for multiple model providers (OpenAI, Anthropic, Ollama, vLLM, etc.)
- Separate database setup with Docker
- Automatic master key generation
- Environment variable substitution in API keys

## Quick Start

1. **Set up the database** (optional - for local PostgreSQL):
   ```bash
   ./setup-db.sh
   export DATABASE_URL="postgresql://litellm:litellm@localhost:5444/litellm"
   ```

   Or use an external database:
   ```bash
   export DATABASE_URL="postgresql://user:password@host:port/database"
   ```

2. **Configure your models** in `models.yaml`:
   ```yaml
   models:
     - name: gpt-4
       model: openai/gpt-4
       api_base: https://api.openai.com/v1
       api_key: ${OPENAI_API_KEY}
   ```

3. **Run the start script**:
   ```bash
   ./start.sh
   ```

## Model Configuration

Models are now configured in the `models.yaml` file instead of environment variables.

### Configuration Format

Edit `models.yaml` to add your models:

```yaml
models:
  - name: model-display-name
    model: provider/model-id
    api_base: https://api-endpoint.com/v1
    api_key: your-api-key-or-${ENV_VAR}
```

### Example Configurations

#### Local Models (vLLM, Ollama, etc.)
```yaml
models:
  # Qwen models via vLLM
  - name: qwen3-72b
    model: openai/Qwen/Qwen2.5-72B-Instruct
    api_base: http://localhost:8000/v1
    api_key: local-key
  
  - name: qwen3-32b
    model: openai/Qwen/Qwen2.5-32B-Instruct
    api_base: http://localhost:8001/v1
    api_key: local-key
  
  # Llama models via Ollama
  - name: llama3-70b
    model: openai/llama3.1:70b
    api_base: http://localhost:11434/v1
    api_key: ollama
  
  - name: mistral
    model: openai/mistral:latest
    api_base: http://localhost:11434/v1
    api_key: ollama
```

#### Cloud Providers
```yaml
models:
  # OpenAI
  - name: gpt-4
    model: openai/gpt-4
    api_base: https://api.openai.com/v1
    api_key: ${OPENAI_API_KEY}  # Uses environment variable
  
  - name: gpt-3.5-turbo
    model: openai/gpt-3.5-turbo
    api_base: https://api.openai.com/v1
    api_key: ${OPENAI_API_KEY}
  
  # Anthropic
  - name: claude-3-opus
    model: anthropic/claude-3-opus-20240229
    api_base: https://api.anthropic.com/v1
    api_key: ${ANTHROPIC_API_KEY}
  
  - name: claude-3-sonnet
    model: anthropic/claude-3-sonnet-20240229
    api_base: https://api.anthropic.com/v1
    api_key: ${ANTHROPIC_API_KEY}
  
  # Azure OpenAI
  - name: azure-gpt-4
    model: azure/gpt-4
    api_base: https://your-resource.openai.azure.com
    api_key: ${AZURE_API_KEY}
  
  # Google Vertex AI
  - name: gemini-pro
    model: vertex_ai/gemini-pro
    api_base: https://us-central1-aiplatform.googleapis.com
    api_key: ${VERTEX_API_KEY}
```

#### Custom/Self-Hosted Endpoints
```yaml
models:
  # Text Generation Inference (HuggingFace)
  - name: falcon-40b
    model: openai/tiiuae/falcon-40b
    api_base: http://your-tgi-server:8080/v1
    api_key: your-key
  
  # Custom OpenAI-compatible endpoints
  - name: custom-model-1
    model: openai/custom-model-1
    api_base: https://your-api.com/v1
    api_key: ${CUSTOM_API_KEY}
```

### Using Environment Variables

You can use environment variables in the `api_key` field by using the format `${VARIABLE_NAME}`:

```yaml
models:
  - name: gpt-4
    model: openai/gpt-4
    api_base: https://api.openai.com/v1
    api_key: ${OPENAI_API_KEY}
```

Then set the environment variable before running:
```bash
export OPENAI_API_KEY="sk-your-actual-api-key"
./start.sh
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

- `models.yaml`: Model configuration file (you create this)
- `setup-db.sh`: Database setup script
- `start.sh`: Main startup script
- `docker-compose.yml`: Docker services definition
- `litellm_config.yaml.j2`: Jinja2 template for LiteLLM config
- `litellm_config.yaml`: Generated configuration (git-ignored)
- `docker-compose.override.yml`: Generated overrides (git-ignored)

## Troubleshooting

### No Models Configured Error
```
Error: No models configured in models.yaml!
```
Solution: Edit `models.yaml` and uncomment/add at least one model configuration

### Database Connection Error
```
Error: DATABASE_URL environment variable is not set!
```
Solution: Run `./setup-db.sh` and export the DATABASE_URL, or set your own

### YAML Parse Error
Check your `models.yaml` syntax. Each model needs: name, model, api_base, and api_key

### Connection Refused
- Verify your model endpoints are accessible
- Check API keys are correct
- Use `docker-compose logs litellm` to see detailed errors

## Security Notes

- Master key is displayed during startup - save it securely
- Store API keys as environment variables, not directly in models.yaml
- Use HTTPS for production deployments
- The `.gitignore` should include `litellm_config.yaml` and `docker-compose.override.yml`