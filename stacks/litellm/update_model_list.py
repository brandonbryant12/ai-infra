#!/usr/bin/env python3
# Usage: python update_model_list.py
# Usage with env file: python update_model_list.py --env litellm.env
# Usage with custom config: python update_model_list.py --config custom_config.yaml

import os
import sys
import json
import yaml
import argparse
import urllib.request

PROVIDERS = {
    "vllm": {
        "api_base_env": "VLLM_API_URL",
        "api_key_env": "VLLM_API_KEY",
        "prefix": "openai/"
    }
}

def load_env_file(env_path):
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def fetch_models(provider, config):
    api_base = os.getenv(config["api_base_env"])
    api_key = os.getenv(config["api_key_env"])
    
    if not api_base:
        print(f"Skipping {provider}: {config['api_base_env']} not set")
        return []
    
    url = f"{api_base.rstrip('/')}/v1/models"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read())
        return [m["id"] for m in data.get("data", []) if "id" in m]
    except Exception as e:
        print(f"Failed to fetch {provider}: {e}")
        return []

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="litellm_config.yaml")
    parser.add_argument("--env", help="Path to .env file")
    args = parser.parse_args()
    
    if args.env:
        load_env_file(args.env)
    
    config = {}
    if os.path.exists(args.config):
        with open(args.config) as f:
            config = yaml.safe_load(f) or {}
    
    if "model_list" not in config:
        config["model_list"] = []
    
    existing = {m["model_name"] for m in config["model_list"] if "model_name" in m}
    
    for provider, provider_config in PROVIDERS.items():
        models = fetch_models(provider, provider_config)
        prefix = provider_config.get("prefix", "openai/")
        
        for model_id in models:
            model_name = f"{provider}/{model_id}"
            if model_name not in existing:
                config["model_list"].append({
                    "model_name": model_name,
                    "litellm_params": {
                        "model": f"{prefix}{model_id}",
                        "api_base": f"os.environ/{provider_config['api_base_env']}",
                        "api_key": f"os.environ/{provider_config['api_key_env']}",
                    }
                })
                existing.add(model_name)
                print(f"Added: {model_name}")
    
    with open(args.config, "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)
    
    print("Done")

if __name__ == "__main__":
    main()
