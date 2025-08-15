# LiteLLM Model Auto-Discovery Script

Automatically discovers and adds models from your AI providers to LiteLLM.

## What it does

- Finds all your AI providers from environment variables
- Fetches available models from each provider
- Updates your LiteLLM config with the models (or adds them via API)
- Never duplicates models (it's idempotent - safe to run multiple times)

## Quick Start

### 1. Set up your providers

Add environment variables for each provider you want to use:

```bash
# For vLLM
export PROVIDER_VLLM_API_URL=http://localhost:8000
export PROVIDER_VLLM_API_KEY=your-key-here

# For any other OpenAI-compatible provider
export PROVIDER_MYSERVICE_API_URL=http://your-service.com
export PROVIDER_MYSERVICE_API_KEY=your-api-key
```

### 2. Run the script

```bash
# Update config file (default: litellm_config.yaml)
python update_model_list.py

# Or update via LiteLLM API
export LITELLM_API_URL=http://localhost:4000
export LITELLM_MASTER_KEY=your-master-key
python update_model_list.py --mode api
```

## Environment Variables

### Provider Discovery
The script automatically finds providers using this pattern:
- `PROVIDER_<NAME>_API_URL` - The API endpoint (required)
- `PROVIDER_<NAME>_API_KEY` - The API key (optional)
- `PROVIDER_<NAME>_PREFIX` - Model prefix (optional, defaults to "openai")

Examples:
```bash
PROVIDER_VLLM_API_URL=http://localhost:8000
PROVIDER_VLLM_API_KEY=sk-1234567890
PROVIDER_VLLM_PREFIX=openai  # Models will be: openai/model-name
```

### LiteLLM Connection
```bash
LITELLM_API_URL=http://localhost:4000  # Your LiteLLM proxy URL
LITELLM_MASTER_KEY=sk-your-master-key  # For API mode
```

## Usage Examples

### Basic usage
```bash
# Discover providers and update config file
python update_model_list.py
```

### Use a .env file
```bash
# Load environment from file
python update_model_list.py --env litellm.env
```

### Update via API instead of config file
```bash
# Add models directly to running LiteLLM instance
python update_model_list.py --mode api
```

### Custom config file
```bash
# Use a different config file
python update_model_list.py --config my_config.yaml
```

### Full example with all options
```bash
python update_model_list.py \
  --env litellm.env \
  --mode api \
  --litellm-url http://localhost:4000 \
  --api-key sk-my-master-key
```

## How it works

1. **Discovers providers**: Looks for `PROVIDER_*_API_URL` in your environment
2. **Fetches models**: Calls `/v1/models` on each provider
3. **Updates LiteLLM**: Either:
   - Writes to config file (default)
   - Adds via API (with `--mode api`)
4. **Never duplicates**: Only adds models that don't already exist

## Output

The script will show you:
- Which providers it found
- Which models it added
- Any errors it encountered

Example output:
```
Discovered provider: vllm
Added: openai/gpt-4
Added: openai/gpt-3.5-turbo
Added: openai/llama-3.1-70b
Done
```

## Troubleshooting

**No providers found**
- Make sure your environment variables start with `PROVIDER_` and end with `_API_URL`

**Can't fetch models**
- Check your API URL is correct and accessible
- Verify your API key if the provider requires authentication

**API mode fails**
- Ensure LiteLLM is running
- Check `LITELLM_MASTER_KEY` is set correctly

## Requirements

- Python 3.6+
- PyYAML (`pip install pyyaml`)
- No other dependencies!