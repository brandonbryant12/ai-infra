#!/usr/bin/env python3
"""
Test script to verify user tracking through LiteLLM to Langfuse
"""
import requests
import json
import os
import time
from datetime import datetime

# LiteLLM endpoint
LITELLM_URL = "http://localhost:4000"
LITELLM_API_KEY = "sk-1234"  # From .env file

# Test user ID (simulating OpenWebUI)
TEST_USER_ID = "test-user-123"
TEST_USER_EMAIL = "test@example.com"

def test_chat_completion():
    """Test chat completion with user headers"""
    
    print(f"\n{'='*60}")
    print(f"Testing LiteLLM User Tracking - {datetime.now()}")
    print(f"{'='*60}\n")
    
    # Headers simulating OpenWebUI request
    headers = {
        "Authorization": f"Bearer {LITELLM_API_KEY}",
        "Content-Type": "application/json",
        # Simulate OpenWebUI headers
        "X-OpenWebUI-User-Id": TEST_USER_ID,
        "X-OpenWebUI-User-Email": TEST_USER_EMAIL,
        "X-OpenWebUI-User-Name": "Test User",
        "X-OpenWebUI-User-Role": "user"
    }
    
    # Chat completion request
    data = {
        "model": "switchpoint-router",  # Using a more reliable model for testing
        "messages": [
            {
                "role": "user",
                "content": "What is 2+2? Answer in one word."
            }
        ],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    print(f"Sending request to: {LITELLM_URL}/v1/chat/completions")
    print(f"User ID: {TEST_USER_ID}")
    print(f"Headers: {json.dumps({k: v for k, v in headers.items() if k != 'Authorization'}, indent=2)}")
    print(f"Request body: {json.dumps(data, indent=2)}")
    
    try:
        # Make the request
        response = requests.post(
            f"{LITELLM_URL}/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        print(f"\nResponse status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Extract the answer
            if 'choices' in result and len(result['choices']) > 0:
                answer = result['choices'][0]['message']['content']
                print(f"\n✅ Success! Model response: {answer}")
                print(f"\nNow check Langfuse at https://langfuse.brandonbryant.io")
                print(f"Look for traces with user ID: {TEST_USER_ID}")
            
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def check_litellm_config():
    """Check LiteLLM configuration"""
    print("\nChecking LiteLLM configuration...")
    
    headers = {
        "Authorization": f"Bearer {LITELLM_API_KEY}"
    }
    
    try:
        # Get model list
        response = requests.get(f"{LITELLM_URL}/models", headers=headers)
        if response.status_code == 200:
            models = response.json()
            print(f"✅ LiteLLM is running with {len(models['data'])} models")
        else:
            print(f"❌ Failed to get models: {response.text}")
    except Exception as e:
        print(f"❌ Failed to connect to LiteLLM: {str(e)}")

if __name__ == "__main__":
    # Check LiteLLM is running
    check_litellm_config()
    
    # Test user tracking
    test_chat_completion()
    
    print("\n" + "="*60)
    print("Test completed. Check Langfuse dashboard for results.")
    print("="*60)