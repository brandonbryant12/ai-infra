# Langfuse Integration with LiteLLM

This guide explains how to integrate Langfuse observability with your LiteLLM proxy for comprehensive LLM monitoring and analytics.

## Overview

Langfuse provides observability, metrics, evals, prompt management and a playground for LLM applications. When integrated with LiteLLM, it automatically tracks:

- **Request/Response data**: All API calls, prompts, completions, and metadata
- **Performance metrics**: Latency, tokens used, costs, error rates  
- **User analytics**: Track usage by user, session, or custom tags
- **Model comparisons**: Compare performance across different models
- **Cost tracking**: Monitor spending across models and users

## Setup Instructions

### 1. Environment Variables

Add these variables to your `.env` file:

```bash
# Langfuse Configuration
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key-here
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key-here  
LANGFUSE_HOST=https://cloud.langfuse.com
# Or for self-hosted: LANGFUSE_HOST=http://localhost:3000

# LiteLLM Configuration
LITELLM_MASTER_KEY=sk-your-master-key-here
DATABASE_URL=postgresql://user:password@host:port/dbname
```

### 2. LiteLLM Configuration

Your `config.yaml` should include Langfuse callbacks:

```yaml
general_settings:
  success_callback: ["langfuse"]
  failure_callback: ["langfuse"]

litellm_settings:
  success_callback: ["langfuse"] 
  failure_callback: ["langfuse"]
  langfuse_public_key: os.environ/LANGFUSE_PUBLIC_KEY
  langfuse_secret_key: os.environ/LANGFUSE_SECRET_KEY
  langfuse_host: os.environ/LANGFUSE_HOST
```

### 3. Custom Headers for User Tracking

To track individual users, include these headers in your API requests:

```bash
# Basic user identification
curl -X POST "http://localhost:4000/chat/completions" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "X-User-Id: user123" \
  -H "X-Session-Id: session456" \
  -d '{...}'

# Advanced tracking with custom metadata
curl -X POST "http://localhost:4000/chat/completions" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "X-User-Id: user123" \
  -H "X-Session-Id: session456" \
  -H "X-Langfuse-Tags: production,customer-support" \
  -H "X-Langfuse-User-Props: {\"subscription\": \"premium\"}" \
  -d '{...}'
```

### 4. Verify Integration

1. **Start your services**: `make start` (starts Langfuse + LiteLLM)
2. **Make a test request** to your LiteLLM proxy
3. **Check Langfuse dashboard** at your `LANGFUSE_HOST` URL
4. **View traces** in the Langfuse UI - you should see your requests appear

## Custom Callbacks

The `custom_callbacks.py` file includes enhanced tracking:

- **Email extraction**: Automatically extracts email addresses from user IDs
- **Header forwarding**: Passes OpenWebUI headers to Langfuse
- **Enhanced metadata**: Includes model info, timestamps, and custom properties

## Useful Langfuse Features

### Dashboard Insights
- **Cost analysis** by model, user, or time period
- **Performance metrics** including P95 latency
- **Usage patterns** and peak hours
- **Error tracking** and debugging

### Prompt Management
- **Version prompts** and track performance
- **A/B testing** different prompt variations
- **Prompt templates** for consistent formatting

### Evaluation & Testing
- **Custom evaluations** for quality assessment  
- **Automated scoring** of model outputs
- **Regression testing** for prompt changes

## Troubleshooting

### Common Issues

1. **No traces appearing**:
   - Verify environment variables are set correctly
   - Check LiteLLM logs for callback errors
   - Ensure Langfuse service is running and accessible

2. **Authentication errors**:
   - Double-check your Langfuse public/secret keys
   - Verify the LANGFUSE_HOST URL is correct

3. **Missing user data**:
   - Include `X-User-Id` header in requests
   - Check custom_callbacks.py is loaded properly

### Debug Mode

Enable debug logging in LiteLLM:

```yaml
general_settings:
  set_verbose: true
  debug: true
```

### Health Checks

Test Langfuse connectivity:

```bash
# Test Langfuse API directly
curl -X GET "$LANGFUSE_HOST/api/public/health" \
  -H "Authorization: Bearer $LANGFUSE_PUBLIC_KEY"
```

## Integration with OpenWebUI

When using with OpenWebUI, user information is automatically forwarded through headers:

- `X-OpenWebUI-User-Id`: OpenWebUI user identifier
- `X-OpenWebUI-User-Email`: User's email address  
- `X-OpenWebUI-User-Name`: Display name
- `X-OpenWebUI-User-Role`: User role (admin, user, etc.)

This enables per-user tracking and analytics in Langfuse.

## Resources

- [Langfuse Documentation](https://langfuse.com/docs)
- [LiteLLM Callbacks Guide](https://docs.litellm.ai/docs/observability/langfuse_integration)
- [Langfuse Python SDK](https://github.com/langfuse/langfuse-python)