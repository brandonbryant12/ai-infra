"""
File-based logger for LiteLLM modeled after the official LangfuseLogger
Logs all LLM interactions to a JSON file instead of Langfuse
"""

import json
import os
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import uuid
import hashlib


class LiteLLMFileLogger:
    """
    File logger that mimics LangfuseLogger behavior but writes to file
    """
    
    def __init__(self):
        """Initialize the file logger"""
        # Log file location
        self.log_file = os.getenv("LITELLM_LOG_FILE", "/tmp/litellm_logs.jsonl")
        
        # Initialize with a startup message
        self._write_log({
            "event": "logger_initialized",
            "timestamp": datetime.utcnow().isoformat(),
            "log_file": self.log_file,
            "pid": os.getpid()
        })
        
        # Track active traces
        self.trace_ids = {}
        
    def _write_log(self, data: Dict[str, Any]):
        """Write a log entry to file"""
        try:
            with open(self.log_file, "a") as f:
                json.dump(data, f)
                f.write("\n")
                f.flush()
        except Exception as e:
            # Fallback to stderr if file write fails
            import sys
            print(f"Error writing to log file: {e}", file=sys.stderr)
    
    def _generate_trace_id(self, kwargs: Dict[str, Any]) -> str:
        """Generate a unique trace ID for this request"""
        # Check if trace_id is already in metadata
        metadata = kwargs.get("litellm_params", {}).get("metadata", {})
        if metadata.get("trace_id"):
            return metadata["trace_id"]
        
        # Generate new trace ID
        return f"trace_{uuid.uuid4().hex[:16]}"
    
    def _extract_metadata(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant metadata from kwargs"""
        metadata = {}
        
        # Extract from litellm_params
        litellm_params = kwargs.get("litellm_params", {})
        if litellm_params:
            metadata["litellm_metadata"] = litellm_params.get("metadata", {})
            metadata["api_base"] = litellm_params.get("api_base")
            metadata["custom_llm_provider"] = litellm_params.get("custom_llm_provider")
        
        # Extract model info
        metadata["model"] = kwargs.get("model", "unknown")
        metadata["call_type"] = kwargs.get("call_type", "completion")
        metadata["stream"] = kwargs.get("stream", False)
        
        # Extract user/session info if available
        metadata["user"] = kwargs.get("user")
        metadata["litellm_call_id"] = kwargs.get("litellm_call_id")
        
        return metadata
    
    def _get_input_output_content(
        self, 
        kwargs: Dict[str, Any], 
        response_obj: Any,
        start_time: float,
        end_time: float
    ) -> Dict[str, Any]:
        """Extract input and output content from request/response"""
        content = {
            "timestamp": datetime.utcnow().isoformat(),
            "duration_seconds": end_time - start_time if start_time and end_time else 0
        }
        
        # Extract input
        if "messages" in kwargs:
            content["input"] = {"messages": kwargs["messages"]}
        elif "input" in kwargs:
            content["input"] = {"input": kwargs["input"]}
        elif "prompt" in kwargs:
            content["input"] = {"prompt": kwargs["prompt"]}
        
        # Extract output based on response type
        if response_obj:
            if hasattr(response_obj, "choices"):
                # Chat completion response
                choices = []
                for choice in response_obj.choices:
                    choice_dict = {}
                    if hasattr(choice, "message"):
                        msg = choice.message
                        choice_dict["message"] = {
                            "role": getattr(msg, "role", None),
                            "content": getattr(msg, "content", None),
                            "function_call": getattr(msg, "function_call", None),
                            "tool_calls": getattr(msg, "tool_calls", None)
                        }
                    if hasattr(choice, "finish_reason"):
                        choice_dict["finish_reason"] = choice.finish_reason
                    choices.append(choice_dict)
                content["output"] = {"choices": choices}
                
            elif hasattr(response_obj, "data"):
                # Embeddings response
                content["output"] = {"embeddings_count": len(response_obj.data)}
                
            elif hasattr(response_obj, "url"):
                # Image generation response
                content["output"] = {"image_url": response_obj.url}
            
            # Add usage information
            if hasattr(response_obj, "usage"):
                usage = response_obj.usage
                content["usage"] = {
                    "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(usage, "completion_tokens", 0),
                    "total_tokens": getattr(usage, "total_tokens", 0)
                }
            
            # Add model info
            if hasattr(response_obj, "model"):
                content["response_model"] = response_obj.model
            
            if hasattr(response_obj, "id"):
                content["response_id"] = response_obj.id
        
        return content
    
    def log_event(
        self,
        kwargs: Dict[str, Any],
        response_obj: Any,
        start_time: Optional[float],
        end_time: Optional[float],
        event_type: str = "completion"
    ):
        """Main logging method that handles all event types"""
        try:
            # Generate or retrieve trace ID
            trace_id = self._generate_trace_id(kwargs)
            
            # Extract metadata
            metadata = self._extract_metadata(kwargs)
            
            # Extract input/output content
            content = self._get_input_output_content(kwargs, response_obj, start_time, end_time)
            
            # Build log entry
            log_entry = {
                "event_type": event_type,
                "trace_id": trace_id,
                "metadata": metadata,
                **content
            }
            
            # Add error info if this is a failure
            if event_type == "error" and response_obj:
                if isinstance(response_obj, Exception):
                    log_entry["error"] = {
                        "type": type(response_obj).__name__,
                        "message": str(response_obj),
                        "traceback": traceback.format_exc()
                    }
                else:
                    log_entry["error"] = str(response_obj)
            
            # Write to log file
            self._write_log(log_entry)
            
        except Exception as e:
            # Log the logging error itself
            self._write_log({
                "event_type": "logging_error",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "traceback": traceback.format_exc()
            })
    
    # Callback methods for LiteLLM integration
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        """Sync success callback"""
        self.log_event(kwargs, response_obj, start_time, end_time, "success")
    
    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        """Async success callback"""
        self.log_event(kwargs, response_obj, start_time, end_time, "success")
    
    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """Sync failure callback"""
        self.log_event(kwargs, response_obj, start_time, end_time, "error")
    
    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """Async failure callback"""
        self.log_event(kwargs, response_obj, start_time, end_time, "error")
    
    def log_stream_event(self, kwargs, response_obj, start_time, end_time):
        """Sync stream event callback"""
        # For streaming, we log the complete response
        if "complete_streaming_response" in kwargs:
            response_obj = kwargs.get("complete_streaming_response")
        self.log_event(kwargs, response_obj, start_time, end_time, "stream_complete")
    
    async def async_log_stream_event(self, kwargs, response_obj, start_time, end_time):
        """Async stream event callback"""
        # For streaming, we log the complete response
        if "complete_streaming_response" in kwargs:
            response_obj = kwargs.get("complete_streaming_response")
        self.log_event(kwargs, response_obj, start_time, end_time, "stream_complete")
    
    # Additional methods for compatibility
    def log_pre_api_call(self, model, messages, kwargs):
        """Log before API call"""
        self._write_log({
            "event_type": "pre_api_call",
            "timestamp": datetime.utcnow().isoformat(),
            "model": model,
            "messages": messages,
            "kwargs_keys": list(kwargs.keys()) if kwargs else []
        })
    
    def log_post_api_call(self, kwargs, response_obj, start_time, end_time):
        """Log after API call"""
        self._write_log({
            "event_type": "post_api_call",
            "timestamp": datetime.utcnow().isoformat(),
            "duration_seconds": end_time - start_time if start_time and end_time else 0,
            "response_type": type(response_obj).__name__ if response_obj else None
        })


# Create a singleton instance
_logger_instance = LiteLLMFileLogger()

# Export the logger instance for use in callbacks
litellm_file_logger = _logger_instance