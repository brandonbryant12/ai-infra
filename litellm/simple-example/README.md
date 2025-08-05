# LiteLLM Simple Example

A minimal Docker Compose setup for LiteLLM proxy with OpenRouter and Langfuse integration.

## Quick Start

1. **Copy environment file:**
   ```bash
   cp litellm.env.example litellm.env
   ```

2. **Add your API keys to `litellm.env`:**
   - Get OpenRouter API key from: https://openrouter.ai/keys
   - Get Langfuse keys from: https://cloud.langfuse.com (optional)

3. **Start the service:**
   ```bash
   ./start.sh
   ```
   Or manually:
   ```bash
   docker compose up -d
   ```

4. **Test the endpoint:**
   ```bash
   curl -X POST http://localhost:4000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer sk-1234567890abcdef" \
     -d '{
       "model": "claude-3-5-sonnet",
       "messages": [{"role": "user", "content": "Hello!"}],
       "max_tokens": 100
     }'
   ```

## Configuration

### Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key (required)
- `LANGFUSE_PUBLIC_KEY`: Langfuse public key (optional)
- `LANGFUSE_SECRET_KEY`: Langfuse secret key (optional)
- `LANGFUSE_HOST`: Langfuse host URL (optional)
- `LITELLM_MASTER_KEY`: Master key for API authentication

### Available Endpoints

- Health check: `GET http://localhost:4000/health/readiness`
- Chat completions: `POST http://localhost:4000/v1/chat/completions`
- Available models: `GET http://localhost:4000/v1/models`

## Adding New Models

To add new models, edit the `config.yaml` file:

### 1. Add OpenRouter Models

```yaml
model_list:
  - model_name: claude-3-5-sonnet
    litellm_params:
      model: openrouter/anthropic/claude-3.5-sonnet
      api_key: os.environ/OPENROUTER_API_KEY

  # Add new OpenRouter model
  - model_name: gpt-4
    litellm_params:
      model: openrouter/openai/gpt-4
      api_key: os.environ/OPENROUTER_API_KEY
      
  - model_name: gemini-pro
    litellm_params:
      model: openrouter/google/gemini-pro
      api_key: os.environ/OPENROUTER_API_KEY
```

### 2. Add Other Providers

For non-OpenRouter providers, add the appropriate API key to your environment:

```yaml
# For direct OpenAI
- model_name: gpt-4-direct
  litellm_params:
    model: gpt-4
    api_key: os.environ/OPENAI_API_KEY

# For Anthropic direct
- model_name: claude-direct
  litellm_params:
    model: claude-3-5-sonnet-20241022
    api_key: os.environ/ANTHROPIC_API_KEY
```

Then add the corresponding environment variables to `litellm.env`:
```bash
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
```

### 3. Model Configuration Options

You can customize each model with additional parameters:

```yaml
- model_name: custom-model
  litellm_params:
    model: openrouter/anthropic/claude-3.5-sonnet
    api_key: os.environ/OPENROUTER_API_KEY
    max_tokens: 4096
    temperature: 0.7
    top_p: 1.0
    frequency_penalty: 0.0
    presence_penalty: 0.0
```

### 4. Restart After Changes

After modifying `config.yaml`, restart the container:

```bash
docker compose restart
```

## Monitoring

View logs to monitor requests and responses:
```bash
docker compose logs -f
```

Check Langfuse dashboard (if configured) for detailed analytics and tracing.

## Troubleshooting

### Common Issues

1. **Authentication Error**: Check your API keys in `litellm.env`
2. **Model Not Found**: Verify the model name in `config.yaml` matches the provider's format
3. **Container Won't Start**: Check logs with `docker compose logs litellm`

### Supported Model Formats

- OpenRouter: `openrouter/provider/model-name`
- OpenAI: `gpt-4`, `gpt-3.5-turbo`
- Anthropic: `claude-3-5-sonnet-20241022`, `claude-3-haiku-20240307`
- Google: `gemini-pro`, `gemini-pro-vision`

For more model formats, see: https://docs.litellm.ai/docs/providers