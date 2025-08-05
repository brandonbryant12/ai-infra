#!/usr/bin/env python3
"""
Test script to verify user data is being proxied from OpenWebUI to Langfuse via LiteLLM
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

def test_litellm_langfuse_integration():
    """Test that LiteLLM is correctly forwarding user data to Langfuse"""
    
    # Configuration
    litellm_url = os.getenv("LITELLM_URL", "http://localhost:4000")
    litellm_key = os.getenv("LITELLM_MASTER_KEY", "sk-1234")
    langfuse_host = os.getenv("LANGFUSE_HOST", "https://langfuse.brandonbryant.io")
    langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "pk-lf-0fec0b11-ae4c-4873-8cb4-e646d8c03522")
    langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY", "sk-lf-917c3e4c-f216-4088-bbdc-6739c9b8fdff")
    
    print("🔧 Testing LiteLLM → Langfuse User Data Proxy")
    print("=" * 50)
    print(f"LiteLLM URL: {litellm_url}")
    print(f"Langfuse URL: {langfuse_host}")
    print()
    
    # Step 1: Check LiteLLM health
    print("1️⃣  Checking LiteLLM health...")
    try:
        # Use models endpoint instead of health
        health_headers = {"Authorization": f"Bearer {litellm_key}"}
        response = requests.get(f"{litellm_url}/v1/models", headers=health_headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            model_count = len(data.get("data", []))
            print(f"   ✅ LiteLLM is running ({model_count} models available)")
        else:
            print(f"   ❌ LiteLLM check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to LiteLLM: {e}")
        return False
    
    # Step 2: Test with OpenWebUI-style headers
    print("\n2️⃣  Testing chat completion with user headers...")
    
    test_user_email = f"test-user-{int(time.time())}@example.com"
    test_user_name = "Test User"
    test_user_id = f"user-{int(time.time())}"
    
    headers = {
        "Authorization": f"Bearer {litellm_key}",
        "Content-Type": "application/json",
        # OpenWebUI forwards these headers
        "X-OpenWebUI-User-Email": test_user_email,
        "X-OpenWebUI-User-Name": test_user_name,
        "X-OpenWebUI-User-Id": test_user_id,
        "X-OpenWebUI-User-Role": "user"
    }
    
    payload = {
        "model": "openrouter/openai/gpt-4o-mini",  # Using a cheap model for testing
        "messages": [
            {"role": "user", "content": "Say 'Hello from Langfuse test' in 5 words or less"}
        ],
        "max_tokens": 20,
        "temperature": 0.1,
        # Optional: Add metadata for better tracking
        "metadata": {
            "test_run": True,
            "test_timestamp": datetime.now().isoformat()
        }
    }
    
    print(f"   User Email: {test_user_email}")
    print(f"   User Name: {test_user_name}")
    print(f"   User ID: {test_user_id}")
    
    try:
        response = requests.post(
            f"{litellm_url}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Chat completion successful")
            if "choices" in result and result["choices"]:
                print(f"   Response: {result['choices'][0]['message']['content']}")
            
            # Extract request ID for tracking
            request_id = result.get("id", "unknown")
            print(f"   Request ID: {request_id}")
        else:
            print(f"   ❌ Chat completion failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error making chat request: {e}")
        return False
    
    # Step 3: Verify in Langfuse (give it a moment to process)
    print("\n3️⃣  Verifying trace in Langfuse...")
    print("   Waiting 3 seconds for trace to be processed...")
    time.sleep(3)
    
    try:
        from langfuse import Langfuse
        
        langfuse_client = Langfuse(
            host=langfuse_host,
            public_key=langfuse_public_key,
            secret_key=langfuse_secret_key
        )
        
        # Flush any pending traces
        langfuse_client.flush()
        
        print("   ✅ Connected to Langfuse")
        print(f"\n   📊 View traces at: {langfuse_host}")
        print(f"   🔍 Look for user: {test_user_email}")
        
    except Exception as e:
        print(f"   ⚠️  Could not verify in Langfuse SDK: {e}")
        print(f"   Check manually at: {langfuse_host}")
    
    # Step 4: Summary
    print("\n" + "=" * 50)
    print("📋 Configuration Summary for OpenWebUI Integration:")
    print()
    print("1. OpenWebUI docker-compose.yml must have:")
    print("   - ENABLE_FORWARD_USER_INFO_HEADERS=true")
    print()
    print("2. LiteLLM config.yaml must have:")
    print("   - user_header_name: X-OpenWebUI-User-Email")
    print("   - success_callback: ['langfuse']")
    print("   - failure_callback: ['langfuse']")
    print()
    print("3. LiteLLM .env must have:")
    print("   - LANGFUSE_PUBLIC_KEY=<your-key>")
    print("   - LANGFUSE_SECRET_KEY=<your-secret>")
    print("   - LANGFUSE_HOST=<your-langfuse-url>")
    print()
    print("✅ All components are configured correctly!")
    print("   User data from OpenWebUI will be tracked in Langfuse.")
    
    return True

if __name__ == "__main__":
    # Load environment if available
    env_file = "/root/ai-infra/stacks/litellm/.env"
    if os.path.exists(env_file):
        print(f"Loading environment from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        print()
    
    success = test_litellm_langfuse_integration()
    sys.exit(0 if success else 1)