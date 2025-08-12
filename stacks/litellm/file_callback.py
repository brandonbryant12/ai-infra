"""
File-based callback for LiteLLM - logs all requests/responses to a file
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Log file inside Docker container (not mounted)
LOG_FILE = "/tmp/litellm.log"

def write_log_entry(entry_type, data, error=None):
    """Write a structured log entry to file"""
    try:
        timestamp = datetime.utcnow().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "type": entry_type,
            "data": data
        }
        if error:
            log_entry["error"] = str(error)
        
        # Write as JSON line
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            f.flush()
            
    except Exception as e:
        # Fallback to simpler logging if JSON fails
        try:
            with open(LOG_FILE, "a") as f:
                f.write(f"{datetime.utcnow().isoformat()} | {entry_type} | Error: {e}\n")
                f.flush()
        except:
            pass


def log_success(kwargs, response, start_time, end_time):
    """Success callback - logs successful API calls"""
    try:
        # Calculate duration
        if isinstance(start_time, (int, float)) and isinstance(end_time, (int, float)):
            duration = end_time - start_time
        else:
            duration = (end_time - start_time).total_seconds() if hasattr(end_time - start_time, 'total_seconds') else 0
        
        # Extract key information
        log_data = {
            "status": "success",
            "duration_seconds": duration,
            "model": kwargs.get("model", "unknown"),
            "messages_count": len(kwargs.get("messages", [])),
        }
        
        # Add request details
        if "messages" in kwargs:
            messages = kwargs["messages"]
            if messages:
                log_data["first_message"] = messages[0] if len(messages) > 0 else None
                log_data["last_message"] = messages[-1] if len(messages) > 0 else None
        
        # Add response details
        if hasattr(response, 'usage') and response.usage:
            log_data["usage"] = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        
        if hasattr(response, 'model'):
            log_data["response_model"] = response.model
            
        if hasattr(response, 'id'):
            log_data["response_id"] = response.id
        
        # Extract response content
        if hasattr(response, 'choices') and response.choices:
            choices_data = []
            for i, choice in enumerate(response.choices):
                choice_info = {"index": i}
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    choice_info["content"] = choice.message.content
                if hasattr(choice, 'finish_reason'):
                    choice_info["finish_reason"] = choice.finish_reason
                choices_data.append(choice_info)
            log_data["choices"] = choices_data
        
        # Add cost if available
        if "response_cost" in kwargs:
            log_data["cost"] = kwargs["response_cost"]
        
        write_log_entry("SUCCESS", log_data)
        
    except Exception as e:
        write_log_entry("ERROR", {"error": "Failed to log success event"}, error=e)


def log_failure(kwargs, response, start_time, end_time):
    """Failure callback - logs failed API calls"""
    try:
        # Calculate duration
        if isinstance(start_time, (int, float)) and isinstance(end_time, (int, float)):
            duration = end_time - start_time
        else:
            duration = (end_time - start_time).total_seconds() if hasattr(end_time - start_time, 'total_seconds') else 0
        
        log_data = {
            "status": "failure",
            "duration_seconds": duration,
            "model": kwargs.get("model", "unknown"),
            "messages_count": len(kwargs.get("messages", [])),
        }
        
        # Add error details
        if isinstance(response, Exception):
            log_data["error_type"] = type(response).__name__
            log_data["error_message"] = str(response)
        else:
            log_data["response"] = str(response)
        
        # Add request context
        if "messages" in kwargs and kwargs["messages"]:
            log_data["first_message"] = kwargs["messages"][0]
        
        write_log_entry("FAILURE", log_data)
        
    except Exception as e:
        write_log_entry("ERROR", {"error": "Failed to log failure event"}, error=e)


# Module initialization
write_log_entry("INIT", {
    "message": "File callback module loaded",
    "log_file": LOG_FILE,
    "pid": os.getpid(),
    "working_dir": os.getcwd()
})