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
            "qwen/qwen-2.5-72b-instruct", "deepseek/deepseek-coder",
            "openrouter/horizon-beta"  # Free community testing model
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
    
    def generate_template_data(self, models: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate template data for Jinja2 rendering"""
        processed_models = []
        
        for model in models:
            model_id = model.get("id", "")
            model_name = model.get("name", "")
            architecture = model.get("architecture", {})
            top_provider = model.get("top_provider", {})
            
            # Create a clean model name for LiteLLM
            clean_name = model_id.replace("/", "-").replace(":", "-")
            
            processed_model = {
                "id": model_id,
                "name": clean_name,
                "display_name": model_name,
                "context_length": architecture.get("context_length") or top_provider.get("context_length"),
                "max_completion_tokens": top_provider.get("max_completion_tokens"),
                "modality": architecture.get("modality", "text->text"),
                "pricing": model.get("pricing", {}),
                "is_free": float(model.get("pricing", {}).get("prompt", "0")) == 0.0
            }
            
            processed_models.append(processed_model)
        
        # Template data with configuration options
        template_data = {
            "models": processed_models,
            "verbose": os.getenv("LITELLM_VERBOSE", "false").lower() == "true",
            "request_timeout": int(os.getenv("LITELLM_REQUEST_TIMEOUT", "600")),
            "enable_caching": os.getenv("LITELLM_ENABLE_CACHING", "false").lower() == "true",
            "redis_host": os.getenv("REDIS_HOST", "localhost"),
            "redis_port": int(os.getenv("REDIS_PORT", "6379")),
            "enable_fallbacks": os.getenv("LITELLM_ENABLE_FALLBACKS", "false").lower() == "true",
            "model_groups": self._create_model_groups(processed_models)
        }
        
        return template_data
    
    def _create_model_groups(self, models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create logical model groups for routing"""
        groups = []
        
        # Group by provider
        providers = {}
        for model in models:
            provider = model["id"].split("/")[0]
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(model["name"])
        
        for provider, model_names in providers.items():
            if len(model_names) > 1:  # Only create groups with multiple models
                groups.append({
                    "alias": f"{provider}-models",
                    "models": model_names[:5]  # Limit to 5 models per group
                })
        
        return groups
    
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
    
    def write_template_data(self, template_data: Dict[str, Any]):
        """Write template data to JSON file for Jinja2 CLI"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Write template data as JSON
            data_path = "/app/template_data.json"
            with open(data_path, 'w') as f:
                json.dump(template_data, f, indent=2, default=str)
            
            logger.info(f"Generated template data with {len(template_data['models'])} models")
            return data_path
            
        except Exception as e:
            raise ModelSyncError(f"Failed to write template data: {e}")
    
    def render_config_with_jinja2(self, data_path: str):
        """Render config using Jinja2 CLI"""
        import subprocess
        
        try:
            template_path = "./config.yaml.j2"
            
            # Use jinja2 CLI to render the template
            cmd = [
                "jinja2",
                template_path,
                data_path,
                "--format", "json"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Write rendered config
            with open(self.config_path, 'w') as f:
                f.write(result.stdout)
            
            logger.info(f"Rendered config to {self.config_path}")
            
        except subprocess.CalledProcessError as e:
            raise ModelSyncError(f"Jinja2 rendering failed: {e.stderr}")
        except Exception as e:
            raise ModelSyncError(f"Failed to render config: {e}")
    
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
            logger.info("Starting OpenRouter model sync with Jinja2 templating...")
            
            # Fetch models from OpenRouter
            all_models = self.fetch_openrouter_models()
            
            # Filter models
            filtered_models = self.filter_models(all_models)
            
            if not filtered_models:
                raise ModelSyncError("No suitable models found after filtering")
            
            # Generate template data
            template_data = self.generate_template_data(filtered_models)
            
            # Backup existing config
            self.backup_existing_config()
            
            # Write template data and render config with Jinja2
            data_path = self.write_template_data(template_data)
            self.render_config_with_jinja2(data_path)
            
            # Validate config
            self.validate_config()
            
            logger.info("Model sync completed successfully!")
            
            # Print summary
            print(f"\n=== SYNC SUMMARY ===")
            print(f"Total models available: {len(all_models)}")
            print(f"Filtered models: {len(filtered_models)}")
            print(f"Template data: {data_path}")
            print(f"Config rendered: {self.config_path}")
            print(f"Jinja2 templating: ✅ Enabled")
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