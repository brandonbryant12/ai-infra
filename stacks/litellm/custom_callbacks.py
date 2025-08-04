import os
from typing import Dict, Any, Optional
from litellm.integrations.custom_logger import CustomLogger
from litellm import completion

class LangfuseUserTracker(CustomLogger):
    """
    Custom callback to extract user ID from X-OpenWebUI-User-Id header
    and pass it to Langfuse as trace_user_id metadata
    """
    
    def log_pre_api_call(self, model, messages, kwargs):
        """Extract user ID from headers and add to metadata before API call"""
        # Get the request headers from kwargs if available
        headers = kwargs.get("headers", {})
        
        # Extract user ID from the X-OpenWebUI-User-Id header
        user_id = headers.get("X-OpenWebUI-User-Id") or headers.get("x-openwebui-user-id")
        
        if user_id:
            # Ensure metadata exists
            if "metadata" not in kwargs:
                kwargs["metadata"] = {}
            
            # Add user ID to metadata for Langfuse
            kwargs["metadata"]["trace_user_id"] = user_id
            
            # Also add as a tag for easier filtering
            if "tags" not in kwargs["metadata"]:
                kwargs["metadata"]["tags"] = []
            kwargs["metadata"]["tags"].append(f"user:{user_id}")
    
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        """Log successful completion - handled by Langfuse callback"""
        pass
    
    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """Log failed completion - handled by Langfuse callback"""
        pass