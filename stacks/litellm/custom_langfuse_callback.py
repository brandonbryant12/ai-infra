"""
Custom Langfuse Callback Handler for LiteLLM with Open WebUI Integration
Tracks sessions, user metadata, tokens, timing, and all request details
"""

import json
import time
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import litellm
from litellm.integrations.custom_logger import CustomLogger
from litellm._logging import verbose_logger
import hashlib
import os

try:
    from langfuse import Langfuse
    langfuse_import_exception = None
except ImportError as e:
    langfuse_import_exception = e

class CustomLangfuseLogger(CustomLogger):
    """
    Enhanced Langfuse logger that captures Open WebUI session data and user metadata
    """
    
    def __init__(self):
        super().__init__()
        self.langfuse = None
        self.langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        self.langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        self.langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        self.flush_interval = int(os.getenv("LANGFUSE_FLUSH_INTERVAL", "1"))
        
        if langfuse_import_exception:
            raise ImportError(
                f"Langfuse not installed. Run 'pip install langfuse': {langfuse_import_exception}"
            )
        
        if not (self.langfuse_public_key and self.langfuse_secret_key):
            raise ValueError(
                "LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY must be set in environment"
            )
        
        self.initialize_langfuse()
        verbose_logger.info(
            f"Custom Langfuse Logger initialized with host: {self.langfuse_host}"
        )
    
    def initialize_langfuse(self):
        """Initialize Langfuse client"""
        self.langfuse = Langfuse(
            public_key=self.langfuse_public_key,
            secret_key=self.langfuse_secret_key,
            host=self.langfuse_host,
            flush_interval=self.flush_interval,
            sdk_integration="litellm-custom"
        )
    
    def extract_open_webui_metadata(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract Open WebUI specific metadata from request headers and metadata
        """
        metadata = {}
        
        # Extract from litellm_params metadata
        litellm_metadata = kwargs.get("litellm_params", {}).get("metadata", {})
        
        # Extract from additional headers
        headers = kwargs.get("litellm_params", {}).get("extra_headers", {})
        
        # Open WebUI user headers (when ENABLE_FORWARD_USER_INFO_HEADERS=true)
        user_headers = {
            "user_id": headers.get("X-OpenWebUI-User-Id"),
            "user_email": headers.get("X-OpenWebUI-User-Email"),
            "user_name": headers.get("X-OpenWebUI-User-Name"),
            "user_role": headers.get("X-OpenWebUI-User-Role"),
            "session_id": headers.get("X-OpenWebUI-Session-Id"),
            "chat_id": headers.get("X-OpenWebUI-Chat-Id"),
        }
        
        # Remove None values
        user_headers = {k: v for k, v in user_headers.items() if v is not None}
        
        # Generate session ID if not provided
        if not user_headers.get("session_id"):
            # Create session ID from user ID and timestamp
            user_id = user_headers.get("user_id", "anonymous")
            timestamp = datetime.now().strftime("%Y%m%d")
            session_hash = hashlib.md5(f"{user_id}-{timestamp}".encode()).hexdigest()[:8]
            user_headers["session_id"] = f"session-{session_hash}"
        
        # Combine all metadata
        metadata.update(user_headers)
        metadata.update(litellm_metadata)
        
        # Add request context
        metadata["request_id"] = kwargs.get("litellm_call_id")
        metadata["model"] = kwargs.get("model")
        metadata["api_base"] = kwargs.get("api_base")
        metadata["timestamp"] = datetime.utcnow().isoformat()
        
        return metadata
    
    def log_event(
        self,
        kwargs: Dict[str, Any],
        response_obj: Any,
        start_time: float,
        end_time: float,
        event_type: str = "completion"
    ):
        """
        Log event to Langfuse with enhanced metadata
        """
        try:
            # Extract metadata
            metadata = self.extract_open_webui_metadata(kwargs)
            
            # Calculate metrics
            latency = end_time - start_time
            
            # Extract token usage
            usage = {}
            if hasattr(response_obj, "usage") and response_obj.usage:
                usage = {
                    "prompt_tokens": response_obj.usage.prompt_tokens,
                    "completion_tokens": response_obj.usage.completion_tokens,
                    "total_tokens": response_obj.usage.total_tokens,
                    "cost": kwargs.get("response_cost", 0),
                }
            
            # Extract messages
            messages = kwargs.get("messages", [])
            
            # Prepare generation data
            generation_data = {
                "name": f"{event_type}-{metadata.get('model', 'unknown')}",
                "model": metadata.get("model"),
                "model_parameters": {
                    "temperature": kwargs.get("temperature"),
                    "max_tokens": kwargs.get("max_tokens"),
                    "top_p": kwargs.get("top_p"),
                    "frequency_penalty": kwargs.get("frequency_penalty"),
                    "presence_penalty": kwargs.get("presence_penalty"),
                    "stream": kwargs.get("stream", False),
                },
                "input": messages,
                "output": self.extract_response_content(response_obj),
                "usage": usage,
                "metadata": {
                    "open_webui": {
                        "user_id": metadata.get("user_id"),
                        "user_email": metadata.get("user_email"),
                        "user_name": metadata.get("user_name"),
                        "user_role": metadata.get("user_role"),
                        "chat_id": metadata.get("chat_id"),
                    },
                    "session": {
                        "session_id": metadata.get("session_id"),
                        "request_id": metadata.get("request_id"),
                    },
                    "performance": {
                        "latency_seconds": latency,
                        "timestamp": metadata.get("timestamp"),
                    },
                    "litellm": {
                        "api_base": metadata.get("api_base"),
                        "cache_hit": kwargs.get("cache_hit", False),
                        "custom_llm_provider": kwargs.get("custom_llm_provider"),
                    }
                },
                "level": "DEFAULT" if event_type == "completion" else "ERROR",
                "status_message": "success" if event_type == "completion" else "error",
            }
            
            # Create trace with session tracking
            trace = self.langfuse.trace(
                name=f"openwebui-{metadata.get('chat_id', 'unknown')}",
                session_id=metadata.get("session_id"),
                user_id=metadata.get("user_id"),
                metadata={
                    "source": "open-webui",
                    "user_email": metadata.get("user_email"),
                    "user_role": metadata.get("user_role"),
                },
                tags=self.generate_tags(metadata, event_type),
            )
            
            # Log generation
            trace.generation(**generation_data)
            
            # Log span for detailed timing
            trace.span(
                name="llm-call",
                start_time=datetime.fromtimestamp(start_time),
                end_time=datetime.fromtimestamp(end_time),
                metadata={
                    "latency_ms": latency * 1000,
                    "tokens_per_second": usage.get("total_tokens", 0) / latency if latency > 0 else 0,
                }
            )
            
            # Score if available (for user feedback integration)
            if metadata.get("user_feedback"):
                trace.score(
                    name="user_feedback",
                    value=metadata["user_feedback"].get("score"),
                    comment=metadata["user_feedback"].get("comment"),
                )
            
            # Flush to ensure data is sent
            self.langfuse.flush()
            
            verbose_logger.info(
                f"Logged to Langfuse: session={metadata.get('session_id')}, "
                f"user={metadata.get('user_id')}, tokens={usage.get('total_tokens', 0)}"
            )
            
        except Exception as e:
            verbose_logger.error(f"Error logging to Langfuse: {str(e)}\n{traceback.format_exc()}")
    
    def extract_response_content(self, response_obj: Any) -> Union[str, Dict, List]:
        """Extract content from response object"""
        if hasattr(response_obj, "choices") and response_obj.choices:
            choice = response_obj.choices[0]
            if hasattr(choice, "message"):
                if hasattr(choice.message, "content"):
                    return choice.message.content
                elif hasattr(choice.message, "function_call"):
                    return choice.message.function_call
                elif hasattr(choice.message, "tool_calls"):
                    return [tc.dict() for tc in choice.message.tool_calls]
        return str(response_obj)
    
    def generate_tags(self, metadata: Dict[str, Any], event_type: str) -> List[str]:
        """Generate tags for the trace"""
        tags = [
            "open-webui",
            event_type,
            f"model:{metadata.get('model', 'unknown')}",
        ]
        
        if metadata.get("user_role"):
            tags.append(f"role:{metadata['user_role']}")
        
        if metadata.get("user_id"):
            tags.append("authenticated")
        else:
            tags.append("anonymous")
        
        return tags
    
    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        """Async handler for successful completions"""
        try:
            self.log_event(kwargs, response_obj, start_time, end_time, "completion")
        except Exception as e:
            verbose_logger.error(f"Error in async_log_success_event: {e}")
    
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        """Sync handler for successful completions"""
        try:
            self.log_event(kwargs, response_obj, start_time, end_time, "completion")
        except Exception as e:
            verbose_logger.error(f"Error in log_success_event: {e}")
    
    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """Async handler for failed completions"""
        try:
            self.log_event(kwargs, response_obj, start_time, end_time, "error")
        except Exception as e:
            verbose_logger.error(f"Error in async_log_failure_event: {e}")
    
    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """Sync handler for failed completions"""
        try:
            self.log_event(kwargs, response_obj, start_time, end_time, "error")
        except Exception as e:
            verbose_logger.error(f"Error in log_failure_event: {e}")
    
    async def async_log_stream_event(self, kwargs, response_obj, start_time, end_time):
        """Async handler for streaming completions"""
        try:
            # For streaming, we log after the stream is complete
            self.log_event(kwargs, response_obj, start_time, end_time, "stream_completion")
        except Exception as e:
            verbose_logger.error(f"Error in async_log_stream_event: {e}")
    
    def log_stream_event(self, kwargs, response_obj, start_time, end_time):
        """Sync handler for streaming completions"""
        try:
            self.log_event(kwargs, response_obj, start_time, end_time, "stream_completion")
        except Exception as e:
            verbose_logger.error(f"Error in log_stream_event: {e}")