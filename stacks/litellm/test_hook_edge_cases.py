#!/usr/bin/env python3
"""
Test edge cases for the OpenWebUI Langfuse hook
"""

import asyncio
from openwebui_langfuse_hook import map_openwebui_to_langfuse

async def test_missing_headers():
    """Test hook with missing headers"""
    test_data = {
        "headers": {},
        "messages": [{"role": "user", "content": "Hello"}]
    }
    
    result = await map_openwebui_to_langfuse({}, test_data, "completion")
    
    # Should not crash and should return original data
    assert result == test_data, "Hook should return original data when no headers present"
    print("✅ Missing headers test passed")

async def test_partial_headers():
    """Test hook with only some headers present"""
    test_data = {
        "headers": {
            "X-OpenWebUI-User-Name": "john_doe",
            # Missing other headers
        },
        "messages": [{"role": "user", "content": "Hello"}]
    }
    
    result = await map_openwebui_to_langfuse({}, test_data, "completion")
    
    metadata = result.get("metadata", {})
    assert metadata.get("trace_user_id") == "john_doe", "Should map user_name to trace_user_id"
    assert result.get("user") == "john_doe", "Should set user field"
    assert "session_id" not in metadata, "Should not set session_id when chat_id missing"
    print("✅ Partial headers test passed")

async def test_case_insensitive():
    """Test hook with lowercase headers (some proxies might do this)"""
    test_data = {
        "headers": {
            "x-openwebui-user-id": "user789",
            "x-openwebui-chat-id": "chat789"
        },
        "messages": [{"role": "user", "content": "Hello"}]
    }
    
    result = await map_openwebui_to_langfuse({}, test_data, "completion")
    
    metadata = result.get("metadata", {})
    assert metadata.get("trace_user_id") == "user789", "Should handle lowercase headers"
    assert metadata.get("session_id") == "chat789", "Should handle lowercase headers"
    print("✅ Case insensitive headers test passed")

async def main():
    """Run all tests"""
    print("=== Testing Edge Cases ===")
    await test_missing_headers()
    await test_partial_headers()
    await test_case_insensitive()
    print("\n✅ All edge case tests passed!")

if __name__ == "__main__":
    asyncio.run(main())