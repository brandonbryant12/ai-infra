import os
from typing import Dict, Any, Optional, Union
from litellm.integrations.custom_logger import CustomLogger
from litellm import completion
import logging

logger = logging.getLogger(__name__)

class LangfuseUserTracker(CustomLogger):
    """
    Custom callback to extract user ID from request context
    and pass it to Langfuse as trace_user_id metadata.
    
    This works with LiteLLM proxy to track OpenWebUI users.
    """
    
    def __init__(self):
        super().__init__()
        logger.info("LangfuseUserTracker initialized")
    
    def log_pre_api_call(self, model, messages, kwargs):
        """Extract user ID from request context and add to metadata before API call"""
        try:
            # In LiteLLM proxy mode, the request context is available via litellm_params
            litellm_params = kwargs.get("litellm_params", {})
            
            # Get metadata from litellm_params or create it
            metadata = litellm_params.get("metadata", {})
            
            # Check if user_id is already in metadata (from proxy preprocessing)
            user_id = metadata.get("user_id")
            
            if user_id:
                # Add trace_user_id for Langfuse
                metadata["trace_user_id"] = user_id
                
                # Also add as a tag for easier filtering
                if "tags" not in metadata:
                    metadata["tags"] = []
                if f"user:{user_id}" not in metadata["tags"]:
                    metadata["tags"].append(f"user:{user_id}")
                
                # Update the metadata in litellm_params
                litellm_params["metadata"] = metadata
                kwargs["litellm_params"] = litellm_params
                
                logger.debug(f"Added user_id to Langfuse trace: {user_id}")
            else:
                logger.debug("No user_id found in metadata")
                
        except Exception as e:
            logger.error(f"Error in LangfuseUserTracker.log_pre_api_call: {str(e)}")
    
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        """Log successful completion - handled by Langfuse callback"""
        pass
    
    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """Log failed completion - handled by Langfuse callback"""
        pass
    
    async def async_log_pre_api_call(self, model, messages, kwargs):
        """Async version of log_pre_api_call"""
        self.log_pre_api_call(model, messages, kwargs)
    
    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        """Async version - handled by Langfuse callback"""
        pass
    
    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """Async version - handled by Langfuse callback"""
        pass