# LiteLLM Deployment Guide

Complete deployment guide for LiteLLM proxy gateway without database requirements. This guide covers multiple deployment methods and includes configuration examples for integrating with OpenWebUI and other LLM providers.

## Overview

LiteLLM is a proxy gateway that provides a unified OpenAI-compatible API for 100+ LLM providers. This deployment guide focuses on lightweight, database-free configurations suitable for development and production use.

## Deployment Methods

| Method | Best For | Complexity | Size |
|--------|----------|------------|------|
| [Python](./python/) | Development, testing | Low | N/A |
| [Docker](./docker/) | Single server deployment | Medium | 500-800MB |
| [Docker Custom](./docker-custom/) | Optimized deployments | Medium-High | 80-250MB |
| [Helm](./helm/) | Kubernetes clusters | High | Varies |

## Quick Start

### 1. Clone or Download This Guide

```bash
git clone <repository-url>
cd litellm-deployment
```

### 2. Choose Your Deployment Method

- **For local development**: Use [Python deployment](./python/)
- **For server deployment**: Use [Docker deployment](./docker/)
- **For production optimization**: Use [Custom Docker build](./docker-custom/)
- **For Kubernetes**: Use [Helm deployment](./helm/)

### 3. Configure Your Models

Copy and modify the example configuration:

```bash
cp config/litellm_config.yaml ./my-config.yaml
```

Edit `my-config.yaml` with your OpenWebUI details:

```yaml
model_list:
  - model_name: openwebui-default
    litellm_params:
      model: openai/openwebui-model
      api_base: http://myinstance.com/api
      api_key: your-openwebui-api-token
```

## Configuration

### Basic OpenWebUI Configuration

```yaml
model_list:
  - model_name: openwebui-default
    litellm_params:
      model: openai/openwebui-model
      api_base: http://myinstance.com/api
      api_key: ${OPENWEBUI_API_KEY}
```

### Environment Variables

Create a `.env` file:

```bash
OPENWEBUI_API_KEY=your-openwebui-api-token
OPENWEBUI_API_BASE=http://myinstance.com/api
```

### Multiple Model Support

The [example configuration](./config/litellm_config.yaml) includes setups for:
- OpenWebUI
- OpenAI
- Azure OpenAI
- Anthropic Claude
- Google Gemini
- AWS Bedrock
- Local models (Ollama, LM Studio, vLLM)
- And many more...

## Testing Your Deployment

### Health Check

```bash
curl http://localhost:4000/health
```

### List Models

```bash
curl http://localhost:4000/v1/models
```

### Test Chat Completion

```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openwebui-default",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Client    │────▶│ LiteLLM Proxy│────▶│ OpenWebUI/APIs  │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Config File  │
                    └──────────────┘
```

## Features

- ✅ No database required
- ✅ OpenAI-compatible API
- ✅ Support for 100+ LLM providers
- ✅ Load balancing and fallbacks
- ✅ Rate limiting
- ✅ Request retry logic
- ✅ Logging and monitoring
- ✅ Multi-model routing

## Security Considerations

1. **API Keys**: Always use environment variables for sensitive data
2. **Network**: Bind to localhost in production, use reverse proxy for SSL
3. **Container**: Run as non-root user, use read-only filesystem
4. **Secrets**: Use Kubernetes secrets or secret management tools

## Performance Optimization

1. **Resource Limits**: Set appropriate CPU and memory limits
2. **Replicas**: Run multiple instances for high availability
3. **Caching**: Enable Redis caching for repeated requests
4. **Monitoring**: Set up Prometheus metrics and alerts

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if OpenWebUI URL is accessible
   - Verify network connectivity
   - Check firewall rules

2. **Authentication Failed**
   - Verify API token is correct
   - Check environment variable names
   - Ensure proper escaping of special characters

3. **Model Not Found**
   - Check model name matches configuration
   - Verify API endpoint supports the model
   - Review LiteLLM logs for details

### Debug Mode

Enable detailed logging by setting:

```yaml
litellm_settings:
  set_verbose: true
  detailed_debug: true
```

## Directory Structure

```
litellm-deployment/
├── README.md                 # This file
├── python/                   # Python deployment guide
│   └── README.md
├── docker/                   # Docker deployment guide
│   └── README.md
├── docker-custom/           # Custom Docker build guide
│   └── README.md
├── helm/                    # Helm chart deployment guide
│   └── README.md
└── config/                  # Configuration examples
    └── litellm_config.yaml
```

## Contributing

Feel free to submit issues and enhancement requests!

## Resources

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [LiteLLM GitHub](https://github.com/BerriAI/litellm)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

## License

This deployment guide is provided as-is for educational and operational purposes.