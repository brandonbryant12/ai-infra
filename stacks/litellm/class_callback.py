"""
Class-based callback for LiteLLM - more reliable than function callbacks
"""

import json
import os
from datetime import datetime
from litellm.integrations.custom_logger import CustomLogger

# Log file inside Docker container
LOG_FILE = "/tmp/litellm_class.log"


class FileLogger(CustomLogger):
    """Custom logger class that writes to file"""
    
    def __init__(self):
        super().__init__()
        self.log_file = LOG_FILE
        self.write_log("INIT", {"message": "FileLogger class initialized", "pid": os.getpid()})
    
    def write_log(self, event_type, data):
        """Write log entry to file"""
        try:
            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "type": event_type,
                "data": data
            }
            with open(self.log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
                f.flush()
        except Exception as e:
            # Fallback logging
            with open(self.log_file, "a") as f:
                f.write(f"{datetime.utcnow().isoformat()} | ERROR: {e}\n")
                f.flush()
    
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        """Sync success handler"""
        self.write_log("SYNC_SUCCESS_CALLED", {"method": "log_success_event"})
        
        try:
            # Calculate duration
            if isinstance(start_time, (int, float)) and isinstance(end_time, (int, float)):
                duration = end_time - start_time
            else:
                duration = 0
            
            data = {
                "status": "success",
                "duration": duration,
                "model": kwargs.get("model", "unknown"),
                "messages_count": len(kwargs.get("messages", [])),
            }
            
            # Add usage if available
            if hasattr(response_obj, 'usage') and response_obj.usage:
                data["usage"] = {
                    "prompt_tokens": response_obj.usage.prompt_tokens,
                    "completion_tokens": response_obj.usage.completion_tokens,
                    "total_tokens": response_obj.usage.total_tokens
                }
            
            # Add response content
            if hasattr(response_obj, 'choices') and response_obj.choices:
                data["response_preview"] = str(response_obj.choices[0].message.content)[:100] if response_obj.choices[0].message.content else None
            
            self.write_log("SUCCESS", data)
            
        except Exception as e:
            self.write_log("ERROR", {"error": str(e), "in": "log_success_event"})
    
    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        """Async success handler"""
        self.write_log("ASYNC_SUCCESS_CALLED", {"method": "async_log_success_event"})
        self.log_success_event(kwargs, response_obj, start_time, end_time)
    
    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """Sync failure handler"""
        self.write_log("SYNC_FAILURE_CALLED", {"method": "log_failure_event"})
        
        try:
            if isinstance(start_time, (int, float)) and isinstance(end_time, (int, float)):
                duration = end_time - start_time
            else:
                duration = 0
            
            data = {
                "status": "failure",
                "duration": duration,
                "model": kwargs.get("model", "unknown"),
                "error": str(response_obj) if response_obj else "Unknown error"
            }
            
            self.write_log("FAILURE", data)
            
        except Exception as e:
            self.write_log("ERROR", {"error": str(e), "in": "log_failure_event"})
    
    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """Async failure handler"""
        self.write_log("ASYNC_FAILURE_CALLED", {"method": "async_log_failure_event"})
        self.log_failure_event(kwargs, response_obj, start_time, end_time)
    
    def log_stream_event(self, kwargs, response_obj, start_time, end_time):
        """Sync stream handler - this might be called instead of success for streaming"""
        self.write_log("SYNC_STREAM_CALLED", {"method": "log_stream_event"})
        
        try:
            if isinstance(start_time, (int, float)) and isinstance(end_time, (int, float)):
                duration = end_time - start_time
            else:
                duration = 0
            
            data = {
                "status": "stream_complete",
                "duration": duration,
                "model": kwargs.get("model", "unknown"),
            }
            
            # Check for complete_streaming_response
            if "complete_streaming_response" in kwargs:
                streaming_resp = kwargs.get("complete_streaming_response")
                if streaming_resp and hasattr(streaming_resp, 'usage'):
                    data["usage"] = {
                        "prompt_tokens": streaming_resp.usage.prompt_tokens if hasattr(streaming_resp.usage, 'prompt_tokens') else 0,
                        "completion_tokens": streaming_resp.usage.completion_tokens if hasattr(streaming_resp.usage, 'completion_tokens') else 0,
                        "total_tokens": streaming_resp.usage.total_tokens if hasattr(streaming_resp.usage, 'total_tokens') else 0
                    }
            
            self.write_log("STREAM", data)
            
        except Exception as e:
            self.write_log("ERROR", {"error": str(e), "in": "log_stream_event"})
    
    async def async_log_stream_event(self, kwargs, response_obj, start_time, end_time):
        """Async stream handler"""
        self.write_log("ASYNC_STREAM_CALLED", {"method": "async_log_stream_event"})
        self.log_stream_event(kwargs, response_obj, start_time, end_time)


# Create and export the logger instance
logger_instance = FileLogger()

# Export the instance for use in callbacks
file_logger = logger_instance