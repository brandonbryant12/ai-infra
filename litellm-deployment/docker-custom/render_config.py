#!/usr/bin/env python3
import json
import os
import sys
from jinja2 import Template

def main():
    # Read template
    with open('/app/litellm_config.yaml.j2', 'r') as f:
        template_content = f.read()
    
    template = Template(template_content)
    
    # Parse models from environment
    models = []
    for key, value in sorted(os.environ.items()):
        if key.startswith('LITELLM_MODEL_'):
            model_name = key.replace('LITELLM_MODEL_', '').lower()
            model_config = {}
            
            # Parse the configuration string
            for param in value.split(','):
                if '=' in param:
                    k, v = param.split('=', 1)
                    if k == 'model':
                        model_config['model'] = v
                    elif k == 'api_base':
                        model_config['api_base'] = v
                    elif k == 'api_key':
                        model_config['api_key'] = v
            
            if all(k in model_config for k in ['model', 'api_base', 'api_key']):
                model_config['name'] = model_name
                models.append(model_config)
    
    # Use default models if none configured
    if not models:
        models = [
            {
                "name": "qwen3-32b",
                "model": "openai/qwen3-32b",
                "api_base": "http://localhost:3000/v1",
                "api_key": "sk-local"
            },
            {
                "name": "qwen3-14b",
                "model": "openai/qwen3-14b",
                "api_base": "http://localhost:3000/v1",
                "api_key": "sk-local"
            }
        ]
    
    # Parse extra headers
    extra_headers = []
    if os.environ.get('LITELLM_EXTRA_HEADERS'):
        extra_headers = [h.strip() for h in os.environ['LITELLM_EXTRA_HEADERS'].split(',')]
    else:
        extra_headers = [os.environ.get('USER_HEADER_NAME', 'X-OpenWebUI-User-Email')]
    
    # Build context
    context = {
        'models': models,
        'master_key': os.environ.get('LITELLM_MASTER_KEY', 'sk-MISSING'),
        'user_header_name': os.environ.get('USER_HEADER_NAME', 'X-OpenWebUI-User-Email'),
        'database_url': os.environ.get('DATABASE_URL', ''),
        'disable_end_user_cost_tracking': os.environ.get('DISABLE_END_USER_COST_TRACKING', 'false').lower() == 'true',
        'disable_end_user_cost_tracking_prometheus_only': os.environ.get('DISABLE_END_USER_COST_TRACKING_PROMETHEUS_ONLY', 'false').lower() == 'true',
        'extra_spend_tag_headers': extra_headers
    }
    
    # Add optional settings
    if os.environ.get('LITELLM_DROP_PARAMS'):
        context['drop_params'] = os.environ['LITELLM_DROP_PARAMS'].lower() == 'true'
    if os.environ.get('LITELLM_MAX_PARALLEL_REQUESTS'):
        context['max_parallel_requests'] = int(os.environ['LITELLM_MAX_PARALLEL_REQUESTS'])
    if os.environ.get('LITELLM_NUM_RETRIES'):
        context['num_retries'] = int(os.environ['LITELLM_NUM_RETRIES'])
    if os.environ.get('LITELLM_REQUEST_TIMEOUT'):
        context['request_timeout'] = int(os.environ['LITELLM_REQUEST_TIMEOUT'])
    if os.environ.get('LITELLM_TELEMETRY'):
        context['telemetry'] = os.environ['LITELLM_TELEMETRY'].lower() == 'true'
    
    # Router settings
    if any(key.startswith('LITELLM_ROUTER_') for key in os.environ):
        context['router_settings'] = {}
        if os.environ.get('LITELLM_ROUTER_STRATEGY'):
            context['router_settings']['routing_strategy'] = os.environ['LITELLM_ROUTER_STRATEGY']
        if os.environ.get('LITELLM_ROUTER_REDIS_HOST'):
            context['router_settings']['redis_host'] = os.environ['LITELLM_ROUTER_REDIS_HOST']
        if os.environ.get('LITELLM_ROUTER_REDIS_PORT'):
            context['router_settings']['redis_port'] = os.environ['LITELLM_ROUTER_REDIS_PORT']
        if os.environ.get('LITELLM_ROUTER_REDIS_PASSWORD'):
            context['router_settings']['redis_password'] = os.environ['LITELLM_ROUTER_REDIS_PASSWORD']
    
    # Render template
    output = template.render(**context)
    
    # Write output
    with open('/app/litellm_config.yaml', 'w') as f:
        f.write(output)
    
    print("Configuration generated successfully!")
    print(f"Models configured: {len(models)}")
    print(f"Master key: {context['master_key']}")

if __name__ == '__main__':
    main()