#!/usr/bin/env python3
import os
import sys
from datetime import datetime

def test_langfuse_connection():
    langfuse_host = os.getenv("LANGFUSE_HOST", "http://localhost:3100")
    langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    
    if not langfuse_public_key or not langfuse_secret_key:
        print("❌ Error: LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY must be set")
        print("\nPlease set the following environment variables:")
        print("  export LANGFUSE_PUBLIC_KEY=your_public_key")
        print("  export LANGFUSE_SECRET_KEY=your_secret_key")
        print(f"  export LANGFUSE_HOST={langfuse_host}  # Optional, defaults to http://localhost:3100")
        print("\nFor local Langfuse:")
        print("  1. Access Langfuse UI at http://localhost:3100")
        print("  2. Create an account and project")
        print("  3. Go to Settings -> API Keys")
        print("  4. Create new API keys and use them here")
        return False
    
    print(f"🔧 Testing Langfuse connection...")
    print(f"   Host: {langfuse_host}")
    print(f"   Public Key: {langfuse_public_key[:20]}...")
    
    try:
        from langfuse import Langfuse
        import langfuse
        
        # Print version for debugging
        if hasattr(langfuse, '__version__'):
            print(f"   Langfuse SDK version: {langfuse.__version__}")
        
        # Initialize Langfuse client with minimal params
        client = Langfuse(
            host=langfuse_host,
            public_key=langfuse_public_key,
            secret_key=langfuse_secret_key
        )
        
        # Test with a simple trace creation
        print("   Creating test trace...")
        
        # Test the connection by trying to send a trace
        try:
            # The trace method signature may vary
            client.trace(
                name="connection-test",
                user_id="test-user"
            )
            client.flush()
            print("✅ Langfuse connection successful! (trace created)")
            print(f"   View traces at: {langfuse_host}")
            return True
        except AttributeError:
            # Fallback: test API authentication directly
            import requests
            
            # Try different auth header formats
            auth_methods = [
                # Method 1: Basic auth
                {"auth": (langfuse_public_key, langfuse_secret_key)},
                # Method 2: Bearer token
                {"headers": {"Authorization": f"Bearer {langfuse_public_key}:{langfuse_secret_key}"}},
                # Method 3: X-API headers
                {"headers": {
                    "X-Langfuse-Public-Key": langfuse_public_key,
                    "X-Langfuse-Secret-Key": langfuse_secret_key
                }}
            ]
            
            for method in auth_methods:
                try:
                    response = requests.get(
                        f"{langfuse_host}/api/public/health",
                        timeout=5,
                        **method
                    )
                    
                    if response.status_code == 200:
                        print("✅ Langfuse connection successful! (API health check passed)")
                        print(f"   View Langfuse at: {langfuse_host}")
                        return True
                except:
                    continue
            
            # If all methods fail, try to check if Langfuse is at least running
            try:
                response = requests.get(f"{langfuse_host}/api/public/health", timeout=5)
                if response.status_code in [200, 401, 403]:
                    print("⚠️  Langfuse is running but authentication failed")
                    print("\nTo get correct API keys:")
                    print(f"  1. Open {langfuse_host} in your browser")
                    print("  2. Create an account or sign in")
                    print("  3. Create a new project")
                    print("  4. Go to Settings -> API Keys")
                    print("  5. Create new keys and export them:")
                    print("     export LANGFUSE_PUBLIC_KEY=<your-public-key>")
                    print("     export LANGFUSE_SECRET_KEY=<your-secret-key>")
                    return False
            except:
                pass
            
            print(f"❌ Could not authenticate with Langfuse")
            return False
        
    except ImportError:
        print("❌ Error: langfuse package not installed")
        print("Run: pip install langfuse")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        print("\nTroubleshooting tips:")
        print("1. Verify Langfuse is running at the specified host")
        print("   - For local: Check if running on port 3100")
        print("   - Run: docker ps | grep langfuse")
        print("2. Check your API keys are correct")
        print("3. Ensure network connectivity to Langfuse server")
        return False

if __name__ == "__main__":
    success = test_langfuse_connection()
    sys.exit(0 if success else 1)