#!/usr/bin/env python3
"""
Test script to verify LiteLLM proxy is working and models are available
"""

import requests
import json
import sys
import time
from typing import List, Dict

def wait_for_proxy(base_url: str = "http://localhost:4000", max_retries: int = 30):
    """Wait for LiteLLM proxy to be ready"""
    print("Waiting for LiteLLM proxy to be ready...")
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ LiteLLM proxy is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ Attempt {i+1}/{max_retries} - waiting...")
        time.sleep(2)
    
    print("❌ LiteLLM proxy did not become ready in time")
    return False

def get_available_models(base_url: str = "http://localhost:4000") -> List[Dict]:
    """Get list of available models from LiteLLM proxy"""
    try:
        response = requests.get(f"{base_url}/v1/models", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        models = data.get("data", [])
        return models
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get models: {e}")
        return []

def test_model_completion(model_id: str, base_url: str = "http://localhost:4000") -> bool:
    """Test a simple completion with a model"""
    try:
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": "Say 'Hello' if you can hear me."}],
            "max_tokens": 10
        }
        
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Model {model_id} test failed: {response.status_code}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Model {model_id} test error: {e}")
        return False

def main():
    base_url = "http://localhost:4000"
    
    # Wait for proxy to be ready
    if not wait_for_proxy(base_url):
        sys.exit(1)
    
    # Get available models
    print("\n=== Getting Available Models ===")
    models = get_available_models(base_url)
    
    if not models:
        print("❌ No models found!")
        sys.exit(1)
    
    print(f"✅ Found {len(models)} models:")
    
    # Print model summary
    for i, model in enumerate(models[:10], 1):  # Show first 10
        model_id = model.get("id", "unknown")
        print(f"  {i}. {model_id}")
    
    if len(models) > 10:
        print(f"  ... and {len(models) - 10} more models")
    
    # Test a few models
    print(f"\n=== Testing Models ===")
    test_models = models[:3]  # Test first 3 models
    
    for model in test_models:
        model_id = model.get("id", "")
        print(f"Testing {model_id}...")
        
        if test_model_completion(model_id, base_url):
            print(f"✅ {model_id} working!")
        else:
            print(f"❌ {model_id} failed!")
    
    print(f"\n=== Summary ===")
    print(f"Total models available: {len(models)}")
    print(f"LiteLLM proxy running at: {base_url}")
    print("✅ Setup verification complete!")

if __name__ == "__main__":
    main()