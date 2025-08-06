"""
Pre-call hook to map Open WebUI user info to Langfuse trace fields
This implements Option 1 from the original problem description.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def map_openwebui_to_langfuse(
    user_api_key_dict: Dict[str, Any],
    data: Dict[str, Any],
    call_type: str,
):
    """Map Open WebUI user info to Langfuse trace fields"""
    
    try:
        headers = data.get("headers", {})
        
        # Initialize metadata if not present
        if "metadata" not in data:
            data["metadata"] = {}
        
        # Map Open WebUI user to Langfuse trace_user_id
        # Try different header names Open WebUI might use
        user_id = (
            headers.get("X-OpenWebUI-User-Id") or 
            headers.get("X-OpenWebUI-User-Name") or
            headers.get("x-openwebui-user-id") or
            headers.get("x-openwebui-user-name")
        )
        
        if user_id:
            data["metadata"]["trace_user_id"] = user_id
            logger.debug(f"Mapped Open WebUI user '{user_id}' to Langfuse trace_user_id")
        
        # Map chat ID to session
        chat_id = (
            headers.get("X-OpenWebUI-Chat-Id") or
            headers.get("x-openwebui-chat-id")
        )
        
        if chat_id:
            data["metadata"]["session_id"] = chat_id
            logger.debug(f"Mapped Open WebUI chat '{chat_id}' to Langfuse session_id")
        
        # Optional: Add more user context to trace metadata
        user_email = (
            headers.get("X-OpenWebUI-User-Email") or
            headers.get("x-openwebui-user-email")
        )
        
        user_role = (
            headers.get("X-OpenWebUI-User-Role") or
            headers.get("x-openwebui-user-role")
        )
        
        if user_email or user_role:
            if "trace_metadata" not in data["metadata"]:
                data["metadata"]["trace_metadata"] = {}
            
            if user_email:
                data["metadata"]["trace_metadata"]["user_email"] = user_email
            
            if user_role:
                data["metadata"]["trace_metadata"]["user_role"] = user_role
            
            logger.debug(f"Added Open WebUI user context to trace metadata")
        
        # Also set standard user field for LiteLLM logging
        if user_id and "user" not in data:
            data["user"] = user_id
    
    except Exception as e:
        logger.warning(f"Failed to map Open WebUI headers to Langfuse: {e}")
    
    return data