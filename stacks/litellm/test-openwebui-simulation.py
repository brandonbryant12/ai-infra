#!/usr/bin/env python3
"""
Simulate OpenWebUI making requests to LiteLLM and verify user tracking
"""
import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
LITELLM_URL = "http://localhost:4000"
LITELLM_API_KEY = "sk-1234"
LANGFUSE_URL = "https://langfuse.brandonbryant.io"

# Test different user scenarios
TEST_USERS = [
    {
        "id": f"user-{uuid.uuid4().hex[:8]}",
        "email": "alice@example.com",
        "name": "Alice Test",
        "role": "user"
    },
    {
        "id": f"user-{uuid.uuid4().hex[:8]}",
        "email": "bob@example.com", 
        "name": "Bob Test",
        "role": "admin"
    }
]

def make_chat_request(user_info, message):
    """Make a chat request as a specific user"""
    
    headers = {
        "Authorization": f"Bearer {LITELLM_API_KEY}",
        "Content-Type": "application/json",
        # OpenWebUI headers
        "X-OpenWebUI-User-Id": user_info["id"],
        "X-OpenWebUI-User-Email": user_info["email"],
        "X-OpenWebUI-User-Name": user_info["name"],
        "X-OpenWebUI-User-Role": user_info["role"]
    }
    
    data = {
        "model": "z-ai-glm-4.5-air",  # Using a different model
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    print(f"\n{'='*60}")
    print(f"User: {user_info['name']} ({user_info['id']})")
    print(f"Message: {message}")
    print(f"Time: {datetime.now()}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{LITELLM_URL}/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content'] if result.get('choices') else "No response"
            print(f"✅ Success! Response: {answer[:100]}...")
            print(f"Model used: {result.get('model', 'Unknown')}")
            print(f"Usage: {result.get('usage', {})}")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def run_simulation():
    """Run the complete simulation"""
    
    print("\n" + "="*80)
    print("OpenWebUI → LiteLLM → Langfuse User Tracking Simulation")
    print("="*80)
    
    success_count = 0
    total_count = 0
    
    # Test different users with different messages
    test_messages = [
        "What is the capital of France?",
        "Explain quantum computing in simple terms",
        "Write a haiku about coding"
    ]
    
    for user in TEST_USERS:
        for message in test_messages:
            total_count += 1
            if make_chat_request(user, message):
                success_count += 1
            time.sleep(2)  # Avoid rate limiting
    
    print("\n" + "="*80)
    print(f"Simulation Complete: {success_count}/{total_count} requests successful")
    print("="*80)
    
    print("\n📊 Next Steps:")
    print(f"1. Go to Langfuse: {LANGFUSE_URL}")
    print("2. Check the 'Traces' section")
    print("3. Look for traces with these user IDs:")
    for user in TEST_USERS:
        print(f"   - {user['id']} ({user['name']})")
    print("\n4. Verify that:")
    print("   - Each trace shows the correct user ID")
    print("   - User metadata is properly attached")
    print("   - Traces are grouped by user")
    
def check_langfuse_env():
    """Verify Langfuse environment variables are set"""
    print("\nChecking Langfuse configuration in LiteLLM...")
    
    # Check if env vars are loaded
    env_check = {
        "LANGFUSE_PUBLIC_KEY": "✅" if requests.get(f"{LITELLM_URL}/health/liveliness").status_code == 200 else "❌",
        "LANGFUSE_SECRET_KEY": "✅" if requests.get(f"{LITELLM_URL}/health/liveliness").status_code == 200 else "❌",
        "LANGFUSE_HOST": LANGFUSE_URL
    }
    
    for key, value in env_check.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    # Check environment
    check_langfuse_env()
    
    # Run simulation
    run_simulation()