#!/usr/bin/env python3
"""
OpenRouter Model Sync Script for LiteLLM
Queries OpenRouter API for available models and updates LiteLLM config.yaml
"""

import json
import os
import sys
import yaml
import requests
from typing import Dict, List, Any
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelSyncError(Exception):
    """Custom exception for model sync errors"""
    pass

class OpenRouterModelSync:
    def __init__(self, config_path: str = "/app/config.yaml"):
        self.config_path = config_path
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        
        if not self.openrouter_api_key:
            raise ModelSyncError("OPENROUTER_API_KEY environment variable not set")
    
    def fetch_openrouter_models(self) -> List[Dict[str, Any]]:
        """Fetch available models from OpenRouter API"""
        logger.info("Fetching models from OpenRouter API...")
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(
                f"{self.openrouter_base_url}/models", 
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            models = data.get("data", [])
            logger.info(f"Retrieved {len(models)} models from OpenRouter")
            return models
        
        except requests.exceptions.RequestException as e:
            raise ModelSyncError(f"Failed to fetch models from OpenRouter: {e}")
    
    def filter_models(self, models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter models based on criteria (exclude beta/test models, include popular ones)"""
        filtered_models = []
        
        # Priority models to always include
        priority_models = {
            "openai/gpt-4o", "openai/gpt-4o-mini", 
            "anthropic/claude-3.5-sonnet", "anthropic/claude-3-haiku",
            "google/gemini-2.0-flash-exp", "google/gemini-pro",
            "meta-llama/llama-3.1-405b-instruct", "meta-llama/llama-3.1-70b-instruct",
            "mistralai/mistral-large", "mistralai/codestral-latest",
            "qwen/qwen-2.5-72b-instruct", "deepseek/deepseek-coder"
        }
        
        for model in models:
            model_id = model.get("id", "")
            model_name = model.get("name", "")
            pricing = model.get("pricing", {})
            
            # Skip if no model ID
            if not model_id:
                continue
                
            # Always include priority models
            if model_id in priority_models:
                filtered_models.append(model)
                continue
            
            # Skip beta/test/experimental models unless they're priority
            if any(keyword in model_name.lower() for keyword in ["beta", "test", "experimental", "alpha"]):
                continue
                
            # Skip if pricing is too high (prompt > $10 per 1M tokens)
            prompt_price = float(pricing.get("prompt", "0"))
            if prompt_price > 0.00001:  # $10 per 1M tokens
                continue
                
            # Include free models
            if prompt_price == 0:
                filtered_models.append(model)
                continue
                
            # Include reasonably priced models
            if prompt_price <= 0.000005:  # $5 per 1M tokens or less
                filtered_models.append(model)
        
        logger.info(f"Filtered to {len(filtered_models)} suitable models")
        return filtered_models
    
    def generate_litellm_config(self, models: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate LiteLLM configuration from OpenRouter models"""
        model_list = []
        
        for model in models:
            model_id = model.get("id", "")
            model_name = model.get("name", "")
            
            # Create a clean model name for LiteLLM
            clean_name = model_id.replace("/", "-").replace(":", "-")
            
            model_config = {
                "model_name": clean_name,
                "litellm_params": {
                    "model": f"openrouter/{model_id}",
                    "api_key": "os.environ/OPENROUTER_API_KEY",
                    "api_base": "https://openrouter.ai/api/v1"
                }
            }
            
            model_list.append(model_config)
        
        # Base configuration
        config = {
            "model_list": model_list,
            "general_settings": {
                "user_header_name": "X-OpenWebUI-User-Id",
                "database_url": None,
                "master_key": "os.environ/LITELLM_MASTER_KEY",
                "health_check_interval": 300
            },
            "litellm_settings": {
                "drop_params": True,
                "set_verbose": False,
                "request_timeout": 600
            }
        }
        
        return config
    
    def backup_existing_config(self):
        """Create a backup of the existing config"""
        if os.path.exists(self.config_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.config_path}.backup_{timestamp}"
            
            try:
                with open(self.config_path, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
                logger.info(f"Backed up existing config to {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create backup: {e}")
    
    def write_config(self, config: Dict[str, Any]):
        """Write the new configuration to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False, indent=2)
            
            logger.info(f"Updated LiteLLM config with {len(config['model_list'])} models")
            
        except Exception as e:
            raise ModelSyncError(f"Failed to write config file: {e}")
    
    def validate_config(self) -> bool:
        """Validate the generated config file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Basic validation
            if not config.get("model_list"):
                raise ModelSyncError("No models found in generated config")
            
            if len(config["model_list"]) == 0:
                raise ModelSyncError("Empty model list in config")
            
            logger.info("Config validation passed")
            return True
            
        except Exception as e:
            raise ModelSyncError(f"Config validation failed: {e}")
    
    def run_sync(self):
        """Main sync process"""
        try:
            logger.info("Starting OpenRouter model sync...")
            
            # Fetch models from OpenRouter
            all_models = self.fetch_openrouter_models()
            
            # Filter models
            filtered_models = self.filter_models(all_models)
            
            if not filtered_models:
                raise ModelSyncError("No suitable models found after filtering")
            
            # Generate config
            config = self.generate_litellm_config(filtered_models)
            
            # Backup existing config
            self.backup_existing_config()
            
            # Write new config
            self.write_config(config)
            
            # Validate config
            self.validate_config()
            
            logger.info("Model sync completed successfully!")
            
            # Print summary
            print(f"\n=== SYNC SUMMARY ===")
            print(f"Total models available: {len(all_models)}")
            print(f"Filtered models: {len(filtered_models)}")
            print(f"Config updated: {self.config_path}")
            print("===================\n")
            
        except ModelSyncError as e:
            logger.error(f"Sync failed: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            sys.exit(1)

def main():
    """Main entry point"""
    config_path = os.getenv("CONFIG_PATH", "/app/config.yaml")
    
    sync = OpenRouterModelSync(config_path)
    sync.run_sync()

if __name__ == "__main__":
    main()