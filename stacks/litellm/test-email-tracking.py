#!/usr/bin/env python3
"""
Test email-based user tracking through LiteLLM to Langfuse
"""
import requests
import json
import time
from datetime import datetime

# LiteLLM configuration
LITELLM_URL = "https://litellm.brandonbryant.io"
LITELLM_API_KEY = "sk-1234"

# Test users with emails
TEST_USERS = [
    {
        "email": "alice@example.com",
        "name": "Alice Test",
        "role": "user"
    },
    {
        "email": "bob@company.io", 
        "name": "Bob Admin",
        "role": "admin"
    }
]

def test_with_email(user_info):
    """Test chat completion with email as identifier"""
    
    headers = {
        "Authorization": f"Bearer {LITELLM_API_KEY}",
        "Content-Type": "application/json",
        # Simulate OpenWebUI headers
        "X-OpenWebUI-User-Email": user_info["email"],
        "X-OpenWebUI-User-Name": user_info["name"],
        "X-OpenWebUI-User-Role": user_info["role"],
        # Still send ID for backward compatibility
        "X-OpenWebUI-User-Id": f"user-{hash(user_info['email']) % 10000}"
    }
    
    data = {
        "model": "mistralai-mistral-7b-instruct-free",
        "messages": [
            {
                "role": "user",
                "content": f"Hello, I am {user_info['name']}. Reply in 10 words or less."
            }
        ],
        "max_tokens": 30,
        "temperature": 0.7
    }
    
    print(f"\n{'='*60}")
    print(f"Testing with email: {user_info['email']}")
    print(f"User: {user_info['name']} ({user_info['role']})")
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
            print(f"✅ Success! Response: {answer}")
            print(f"Model: {result.get('model', 'Unknown')}")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    print("\n" + "="*80)
    print("Email-based User Tracking Test for LiteLLM → Langfuse")
    print("="*80)
    
    # Wait for LiteLLM to fully start
    print("\nWaiting for LiteLLM to start...")
    time.sleep(20)
    
    # Test each user
    success_count = 0
    for user in TEST_USERS:
        if test_with_email(user):
            success_count += 1
        time.sleep(2)  # Avoid rate limiting
    
    print("\n" + "="*80)
    print(f"Test Complete: {success_count}/{len(TEST_USERS)} requests successful")
    print("="*80)
    
    print("\n📊 Check Langfuse Dashboard:")
    print("1. Go to https://langfuse.brandonbryant.io")
    print("2. Look for traces with these emails:")
    for user in TEST_USERS:
        print(f"   - {user['email']} ({user['name']})")
    print("\n3. The user field should now show emails instead of IDs")

if __name__ == "__main__":
    main()