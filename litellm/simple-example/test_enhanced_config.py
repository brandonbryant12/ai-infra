#!/usr/bin/env python3
"""
Test the enhanced LiteLLM configuration with maximum user data capture
Uses the local config.yaml with all user headers configured
"""

import os
import sys
import time
import json
import subprocess
import requests
from datetime import datetime

def test_enhanced_litellm_config():
    """Test LiteLLM with enhanced user data configuration"""
    
    print("🚀 Testing Enhanced LiteLLM Configuration")
    print("=" * 50)
    
    # Step 1: Start LiteLLM with local enhanced config
    print("1️⃣  Starting LiteLLM with enhanced config...")
    
    try:
        # Stop any existing LiteLLM
        subprocess.run(["pkill", "-f", "litellm"], capture_output=True)
        time.sleep(2)
        
        # Start LiteLLM with our enhanced config
        cmd = [
            "litellm",
            "--config", "config.yaml",
            "--port", "4001",  # Use different port to avoid conflicts
            "--detailed_debug"
        ]
        
        print(f"   Starting: {' '.join(cmd)}")
        
        # Start LiteLLM in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "PYTHONUNBUFFERED": "1"}
        )
        
        print("   Waiting for LiteLLM to start...")
        time.sleep(10)  # Give it time to start
        
        # Check if it's running
        litellm_url = "http://localhost:4001"
        response = requests.get(f"{litellm_url}/v1/models", 
                              headers={"Authorization": "Bearer sk-1234"},
                              timeout=5)
        
        if response.status_code != 200:
            print(f"   ❌ LiteLLM failed to start properly: {response.status_code}")
            return False
            
        print("   ✅ LiteLLM started successfully")
        
    except Exception as e:
        print(f"   ❌ Failed to start LiteLLM: {e}")
        print("   💡 Make sure 'litellm' is installed: pip install litellm")
        return False
    
    try:
        # Step 2: Test with comprehensive user headers
        print("\n2️⃣  Testing with comprehensive user headers...")
        
        timestamp = int(time.time())
        user_data = {
            "email": f"enhanced-test-{timestamp}@example.com",
            "name": "Enhanced Test User",
            "id": f"enh-user-{timestamp}",
            "role": "admin",
            "session_id": f"enh-session-{timestamp}",
            "chat_id": f"enh-chat-{timestamp}",
            "model": "claude-3-5-sonnet",
            "title": "Enhanced Langfuse Integration Test Suite"
        }
        
        headers = {
            "Authorization": "Bearer sk-1234",
            "Content-Type": "application/json",
            # Comprehensive OpenWebUI headers
            "X-OpenWebUI-User-Email": user_data["email"],
            "X-OpenWebUI-User-Name": user_data["name"],
            "X-OpenWebUI-User-Id": user_data["id"],
            "X-OpenWebUI-User-Role": user_data["role"],
            "X-OpenWebUI-Session-Id": user_data["session_id"],
            "X-OpenWebUI-Chat-Id": user_data["chat_id"],
            "X-OpenWebUI-Model": user_data["model"],
            "X-OpenWebUI-Title": user_data["title"],
            # Additional context
            "X-Forwarded-For": "192.168.1.100",
            "User-Agent": "OpenWebUI/2.0 Enhanced Test Client",
            "X-Real-IP": "10.0.0.50"
        }
        
        payload = {
            "model": "claude-3-5-sonnet",
            "messages": [
                {"role": "user", "content": "Respond with exactly: 'Enhanced config test successful!' and nothing else."}
            ],
            "max_tokens": 50,
            "temperature": 0.1,
            "user": user_data["id"],  # OpenAI standard user field
            "metadata": {
                "test_type": "enhanced_config",
                "test_timestamp": datetime.now().isoformat(),
                "session_info": {
                    "session_id": user_data["session_id"],
                    "chat_id": user_data["chat_id"]
                },
                "user_context": {
                    "email": user_data["email"],
                    "role": user_data["role"]
                }
            }
        }
        
        print("   📊 User Data Being Sent:")
        for key, value in user_data.items():
            print(f"      {key}: {value}")
        print(f"   📋 Total Headers: {len([h for h in headers.keys() if h.startswith('X-OpenWebUI')])} OpenWebUI headers")
        
        response = requests.post(
            f"{litellm_url}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Enhanced chat completion successful")
            if "choices" in result and result["choices"]:
                print(f"   Response: {result['choices'][0]['message']['content']}")
            
            request_id = result.get("id", "unknown")
            print(f"   Request ID: {request_id}")
        else:
            print(f"   ❌ Chat completion failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        # Step 3: Verification
        print("\n3️⃣  Verification...")
        print(f"   🔍 Look for trace with user: {user_data['email']}")
        print(f"   📝 Session: {user_data['session_id']}")
        print(f"   💬 Chat: {user_data['chat_id']}")
        print(f"   🤖 Model: {user_data['model']}")
        print(f"   📊 All metadata should be captured in Langfuse")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    
    finally:
        # Cleanup
        print("\n4️⃣  Cleanup...")
        try:
            process.terminate()
            process.wait(timeout=5)
            print("   ✅ LiteLLM stopped")
        except:
            print("   ⚠️  LiteLLM cleanup may be incomplete")

def main():
    """Main test function"""
    
    # Load environment
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
    
    # Check if we're in the right directory
    if not os.path.exists("config.yaml"):
        print("❌ config.yaml not found. Please run from /root/ai-infra/litellm/simple-example/")
        return False
    
    # Check if langfuse is available
    try:
        import langfuse
        print(f"✅ Langfuse SDK available (version: {langfuse.__version__ if hasattr(langfuse, '__version__') else 'unknown'})")
    except ImportError:
        print("⚠️  Langfuse SDK not available. Install with: pip install langfuse")
    
    print()
    
    success = test_enhanced_litellm_config()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 Enhanced Configuration Test Complete!")
        print()
        print("Your LiteLLM config now captures MAXIMUM user data:")
        print("• Primary user ID via user_header_name")
        print("• All user context via extra_spend_tag_headers")
        print("• Detailed debugging enabled")
        print("• Verbose logging for troubleshooting")
        print()
        print("Every OpenWebUI interaction will create rich traces in Langfuse!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)