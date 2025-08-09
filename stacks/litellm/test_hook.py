#!/usr/bin/env python3
"""
Test script for the OpenWebUI Langfuse hook
"""

import asyncio
from openwebui_langfuse_hook import map_openwebui_to_langfuse

async def test_hook():
    """Test the hook with sample Open WebUI headers"""
    
    # Sample data with Open WebUI headers
    test_data = {
        "headers": {
            "X-OpenWebUI-User-Id": "user123",
            "X-OpenWebUI-User-Email": "test@example.com", 
            "X-OpenWebUI-User-Role": "admin",
            "X-OpenWebUI-Chat-Id": "chat456"
        },
        "messages": [{"role": "user", "content": "Hello"}]
    }
    
    print("=== Before Hook ===")
    print(f"Headers: {test_data['headers']}")
    print(f"Metadata: {test_data.get('metadata', 'None')}")
    print(f"User: {test_data.get('user', 'None')}")
    
    # Apply the hook
    result = await map_openwebui_to_langfuse({}, test_data, "completion")
    
    print("\n=== After Hook ===")
    print(f"Metadata: {result.get('metadata', 'None')}")
    print(f"User: {result.get('user', 'None')}")
    
    # Verify mappings
    metadata = result.get("metadata", {})
    assert metadata.get("trace_user_id") == "user123", "trace_user_id mapping failed"
    assert metadata.get("session_id") == "chat456", "session_id mapping failed"
    assert result.get("user") == "user123", "user field mapping failed"
    
    trace_metadata = metadata.get("trace_metadata", {})
    assert trace_metadata.get("user_email") == "test@example.com", "user_email mapping failed"
    assert trace_metadata.get("user_role") == "admin", "user_role mapping failed"
    
    print("\n✅ All hook mappings work correctly!")

if __name__ == "__main__":
    asyncio.run(test_hook())