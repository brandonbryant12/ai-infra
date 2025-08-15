#!/usr/bin/env python3
# Usage: python update_model_list.py                    # Update config file
# Usage: python update_model_list.py --mode api        # Update via LiteLLM API
# Usage: python update_model_list.py --env litellm.env # Load env file first
#
# Auto-discovers providers from environment variables:
# PROVIDER_<NAME>_API_URL and PROVIDER_<NAME>_API_KEY
# Example: PROVIDER_VLLM_API_URL, PROVIDER_OPENROUTER_API_KEY

import os
import sys
import json
import yaml
import argparse
import urllib.request
import re

def load_env_file(env_path):
    """Load environment variables from file."""
    if not os.path.exists(env_path):
        return
    
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

def discover_providers():
    """Auto-discover providers from PROVIDER_*_API_URL environment variables."""
    providers = {}
    pattern = re.compile(r'^PROVIDER_(.+)_API_URL$')
    
    for key in os.environ:
        match = pattern.match(key)
        if match:
            provider_name = match.group(1).lower()
            api_key_env = f"PROVIDER_{match.group(1)}_API_KEY"
            prefix = os.getenv(f"PROVIDER_{match.group(1)}_PREFIX", "openai")
            
            providers[provider_name] = {
                "api_base_env": key,
                "api_key_env": api_key_env,
                "prefix": prefix
            }
            print(f"Discovered provider: {provider_name}")
    
    return providers

def make_request(url, method="GET", data=None, headers=None):
    """Make HTTP request and return response data."""
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def fetch_models(provider, config):
    """Fetch available models from provider's /v1/models endpoint."""
    api_base = os.getenv(config["api_base_env"])
    api_key = os.getenv(config["api_key_env"])
    
    if not api_base:
        print(f"Skipping {provider}: {config['api_base_env']} not set")
        return []
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    data = make_request(f"{api_base.rstrip('/')}/v1/models", headers=headers)
    if data:
        return [m["id"] for m in data.get("data", []) if "id" in m]
    
    print(f"Failed to fetch models from {provider}")
    return []

def build_model_config(model_id, provider_config, for_api=False):
    """Build model configuration for either config file or API."""
    prefix = provider_config["prefix"]
    model_name = f"{prefix}/{model_id}"
    
    config = {
        "model_name": model_name,
        "litellm_params": {
            "model": model_name
        }
    }
    
    if for_api:
        # API mode: use actual values
        config["litellm_params"]["api_base"] = os.getenv(provider_config["api_base_env"])
        api_key = os.getenv(provider_config["api_key_env"])
        if api_key:
            config["litellm_params"]["api_key"] = api_key
    else:
        # Config mode: use environment variable references
        config["litellm_params"]["api_base"] = f"os.environ/{provider_config['api_base_env']}"
        config["litellm_params"]["api_key"] = f"os.environ/{provider_config['api_key_env']}"
    
    return config

def get_existing_models(mode, **kwargs):
    """Get existing model names based on mode."""
    if mode == "api":
        litellm_url = kwargs["litellm_url"]
        api_key = kwargs["api_key"]
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = make_request(f"{litellm_url}/model/info", headers=headers)
        if data:
            return {m.get("model_name", m.get("id")) for m in data.get("data", [])}
        return set()
    else:
        config_path = kwargs["config_path"]
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = yaml.safe_load(f) or {}
            return {m["model_name"] for m in config.get("model_list", []) if "model_name" in m}
        return set()

def add_model_to_config(model_config, config_path):
    """Add model to config file."""
    config = {}
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
    
    if "model_list" not in config:
        config["model_list"] = []
    
    config["model_list"].append(model_config)
    
    with open(config_path, "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)

def add_model_via_api(model_config, litellm_url, api_key):
    """Add model via LiteLLM API."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    return make_request(
        f"{litellm_url}/model/new",
        method="POST",
        data=model_config,
        headers=headers
    )

def process_providers(providers, mode, **kwargs):
    """Process all providers and update models."""
    # Get existing models
    existing = get_existing_models(mode, **kwargs)
    models_to_add = []
    
    # Collect all new models
    for provider, provider_config in providers.items():
        models = fetch_models(provider, provider_config)
        
        for model_id in models:
            prefix = provider_config["prefix"]
            full_model_name = f"{prefix}/{model_id}"
            
            if full_model_name not in existing:
                model_config = build_model_config(
                    model_id,
                    provider_config,
                    for_api=(mode == "api")
                )
                models_to_add.append((full_model_name, model_config))
                existing.add(full_model_name)
    
    # Add models based on mode
    if mode == "api":
        litellm_url = kwargs["litellm_url"]
        api_key = kwargs["api_key"]
        for model_name, model_config in models_to_add:
            if add_model_via_api(model_config, litellm_url, api_key):
                print(f"Added via API: {model_name}")
            else:
                print(f"Failed to add: {model_name}")
    else:
        config_path = kwargs["config_path"]
        # Load config once
        config = {}
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = yaml.safe_load(f) or {}
        
        if "model_list" not in config:
            config["model_list"] = []
        
        # Add all models
        for model_name, model_config in models_to_add:
            config["model_list"].append(model_config)
            print(f"Added: {model_name}")
        
        # Save once
        with open(config_path, "w") as f:
            yaml.safe_dump(config, f, sort_keys=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="litellm_config.yaml")
    parser.add_argument("--env", help="Path to .env file")
    parser.add_argument("--mode", choices=["config", "api"], default="config",
                       help="Update mode: config file or API")
    
    # Use LITELLM_API_URL env var as default, fallback to localhost
    default_litellm_url = os.getenv("LITELLM_API_URL", "http://localhost:4000")
    parser.add_argument("--litellm-url", default=default_litellm_url,
                       help="LiteLLM API URL (for API mode)")
    parser.add_argument("--api-key", help="LiteLLM master API key (for API mode)")
    args = parser.parse_args()
    
    if args.env:
        load_env_file(args.env)
    
    providers = discover_providers()
    if not providers:
        print("No providers found. Set PROVIDER_<NAME>_API_URL environment variables.")
        return
    
    if args.mode == "api":
        api_key = args.api_key or os.getenv("LITELLM_MASTER_KEY")
        if not api_key:
            print("API key required for API mode (--api-key or LITELLM_MASTER_KEY env)")
            return
        
        process_providers(
            providers,
            mode="api",
            litellm_url=args.litellm_url.rstrip('/'),
            api_key=api_key
        )
    else:
        process_providers(
            providers,
            mode="config",
            config_path=args.config
        )
    
    print("Done")

if __name__ == "__main__":
    main()
