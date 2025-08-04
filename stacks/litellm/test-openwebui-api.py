#!/usr/bin/env python3
"""
Test OpenWebUI API integration with LiteLLM
"""
import requests
import json
from datetime import datetime

# OpenWebUI configuration
OPENWEBUI_URL = "https://ai.brandonbryant.io"
OPENWEBUI_API_KEY = "sk-40917178ffac481c942f7e767bb6d3c3"

# Direct LiteLLM test
LITELLM_URL = "https://litellm.brandonbryant.io"
LITELLM_API_KEY = "sk-1234"

def test_openwebui_api():
    """Test if OpenWebUI is accessible and get user info"""
    print("\n" + "="*60)
    print("Testing OpenWebUI API")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {OPENWEBUI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Try to get user info
    try:
        response = requests.get(f"{OPENWEBUI_URL}/api/v1/auths", headers=headers)
        print(f"Auth endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error accessing OpenWebUI: {e}")

def test_direct_to_litellm():
    """Test direct request to LiteLLM with OpenWebUI headers"""
    print("\n" + "="*60)
    print("Testing Direct Request to LiteLLM")
    print("="*60)
    
    # Simulate OpenWebUI headers
    headers = {
        "Authorization": f"Bearer {LITELLM_API_KEY}",
        "Content-Type": "application/json",
        # These are the headers OpenWebUI should send
        "X-OpenWebUI-User-Id": "openwebui-test-user",
        "X-OpenWebUI-User-Email": "test@openwebui.com",
        "X-OpenWebUI-User-Name": "OpenWebUI Test User",
        "X-OpenWebUI-User-Role": "user"
    }
    
    data = {
        "model": "mistralai-mistral-7b-instruct-free",  # Using a free model
        "messages": [
            {
                "role": "user",
                "content": "Say 'Hello from OpenWebUI test' in 5 words or less"
            }
        ],
        "max_tokens": 20,
        "temperature": 0.1
    }
    
    print(f"Sending to: {LITELLM_URL}/v1/chat/completions")
    print(f"Headers: {json.dumps({k: v for k, v in headers.items() if k != 'Authorization'}, indent=2)}")
    
    try:
        response = requests.post(
            f"{LITELLM_URL}/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        print(f"\nResponse status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Model response: {result['choices'][0]['message']['content']}")
            print(f"\n✅ Check Langfuse for user: openwebui-test-user")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

def test_openwebui_chat():
    """Test chat through OpenWebUI API"""
    print("\n" + "="*60)
    print("Testing Chat via OpenWebUI API")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {OPENWEBUI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # First, get available models
    try:
        response = requests.get(f"{OPENWEBUI_URL}/api/models", headers=headers)
        if response.status_code == 200:
            models = response.json()
            print(f"Available models: {len(models.get('data', []))}")
            if models.get('data'):
                print(f"First model: {models['data'][0]['id']}")
        else:
            print(f"Failed to get models: {response.status_code}")
            return
    except Exception as e:
        print(f"Error getting models: {e}")
        return
    
    # Try to create a chat
    chat_data = {
        "model": "mistralai-mistral-7b-instruct-free",  # Adjust based on available models
        "messages": [
            {
                "role": "user",
                "content": "Test message from API"
            }
        ]
    }
    
    try:
        # Check if there's a chat completions endpoint
        response = requests.post(
            f"{OPENWEBUI_URL}/api/chat/completions",
            headers=headers,
            json=chat_data
        )
        print(f"\nChat completion status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"Error in chat: {e}")

if __name__ == "__main__":
    print(f"\nTesting at {datetime.now()}")
    
    # Test OpenWebUI API
    test_openwebui_api()
    
    # Test direct to LiteLLM
    test_direct_to_litellm()
    
    # Test through OpenWebUI
    test_openwebui_chat()
    
    print("\n" + "="*60)
    print("Tests completed. Check Langfuse for traces.")
    print("="*60)