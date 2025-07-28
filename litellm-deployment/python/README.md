# LiteLLM Python Local Deployment

Deploy LiteLLM proxy gateway locally using Python without any database requirements.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Access to your OpenWebUI instance

## Installation

```bash
pip install 'litellm[proxy]'
```

## Configuration

### Step 1: Create Configuration File

Create a file named `litellm_config.yaml`:

```yaml
model_list:
  - model_name: openwebui-default
    litellm_params:
      model: openai/openwebui-model
      api_base: http://myinstance.com/api
      api_key: your-openwebui-api-token
      
  # Add more models as needed
  - model_name: openwebui-gpt4
    litellm_params:
      model: openai/gpt-4
      api_base: http://myinstance.com/api
      api_key: your-openwebui-api-token

# Optional: Set default timeout
litellm_settings:
  drop_params: True
  set_verbose: False
```

### Step 2: Environment Variables (Optional)

For better security, use environment variables:

```bash
export OPENWEBUI_API_KEY="your-openwebui-api-token"
export OPENWEBUI_API_BASE="http://myinstance.com/api"
```

Then update your config to reference these:

```yaml
model_list:
  - model_name: openwebui-default
    litellm_params:
      model: openai/openwebui-model
      api_base: os.environ/OPENWEBUI_API_BASE
      api_key: os.environ/OPENWEBUI_API_KEY
```

## Running the Proxy

### Basic Start

```bash
litellm --config ./litellm_config.yaml --port 4000
```

### With Debug Output

```bash
litellm --config ./litellm_config.yaml --port 4000 --detailed_debug
```

### Custom Host and Port

```bash
litellm --config ./litellm_config.yaml --host 0.0.0.0 --port 8080
```

## Testing the Connection

### Health Check

```bash
curl http://localhost:4000/health
```

### List Available Models

```bash
curl http://localhost:4000/v1/models
```

### Test Chat Completion

```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openwebui-default",
    "messages": [{"role": "user", "content": "Hello, how are you?"}]
  }'
```

## Advanced Configuration

### Enable Request Logging

```yaml
litellm_settings:
  drop_params: True
  set_verbose: True
  log_raw_request_response: True
```

### Set Timeouts

```yaml
litellm_settings:
  request_timeout: 600  # 10 minutes
  stream_timeout: 60    # 1 minute
```

### Rate Limiting

```yaml
model_list:
  - model_name: openwebui-default
    litellm_params:
      model: openai/openwebui-model
      api_base: http://myinstance.com/api
      api_key: your-openwebui-api-token
      rpm: 100      # requests per minute
      tpm: 100000   # tokens per minute
```

## Running as a Service

### Using systemd (Linux)

Create `/etc/systemd/system/litellm.service`:

```ini
[Unit]
Description=LiteLLM Proxy
After=network.target

[Service]
Type=simple
User=litellm
WorkingDirectory=/opt/litellm
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/local/bin/litellm --config /opt/litellm/litellm_config.yaml --port 4000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable litellm
sudo systemctl start litellm
```

### Using PM2 (Cross-platform)

```bash
# Install PM2
npm install -g pm2

# Start LiteLLM
pm2 start litellm --name litellm-proxy -- --config ./litellm_config.yaml --port 4000

# Save PM2 configuration
pm2 save
pm2 startup
```

## Troubleshooting

### Common Issues

1. **Module not found**: Ensure you installed with `pip install 'litellm[proxy]'` (note the quotes)

2. **Port already in use**: Change the port or kill the process using the port:
   ```bash
   lsof -i :4000
   kill -9 <PID>
   ```

3. **Connection refused to OpenWebUI**: Verify the API base URL and that your instance is accessible

4. **Authentication errors**: Double-check your API token and ensure it's correctly set

### Debug Mode

Run with maximum verbosity:

```bash
litellm --config ./litellm_config.yaml --port 4000 --detailed_debug --set_verbose True
```

## Next Steps

- Add more model providers to your configuration
- Set up authentication for the proxy itself
- Configure load balancing across multiple models
- Monitor usage with callbacks