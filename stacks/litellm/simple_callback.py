"""
Simplified callback for LiteLLM - just functions, no classes
"""

import sys
import os
import json
from datetime import datetime

# Write to a file as well to ensure we're being called
LOG_FILE = "/tmp/litellm_callback.log"

def write_log(message):
    """Write to both stderr and a file for debugging"""
    # Print to stderr
    print(message, file=sys.stderr, flush=True)
    sys.stderr.flush()
    
    # Also write to stdout
    print(message, file=sys.stdout, flush=True)
    sys.stdout.flush()
    
    # Write to file
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{message}\n")
            f.flush()
    except:
        pass


def log_success(kwargs, response, start_time, end_time):
    """Success callback function"""
    write_log(f"\n{'='*60}")
    write_log(f"[CALLBACK] SUCCESS at {datetime.utcnow().isoformat()}")
    
    # Handle both float timestamps and datetime objects
    try:
        if isinstance(start_time, (int, float)) and isinstance(end_time, (int, float)):
            duration = end_time - start_time
        else:
            duration = (end_time - start_time).total_seconds() if hasattr(end_time - start_time, 'total_seconds') else 0
        write_log(f"[CALLBACK] Duration: {duration:.3f}s")
    except Exception as e:
        write_log(f"[CALLBACK] Duration error: {e}")
    
    # Log request info
    try:
        if "messages" in kwargs:
            write_log(f"[CALLBACK] Messages: {len(kwargs.get('messages', []))} messages")
        
        if "model" in kwargs:
            write_log(f"[CALLBACK] Model: {kwargs['model']}")
        
        # Log response info
        if hasattr(response, 'usage'):
            usage = response.usage
            if usage:
                write_log(f"[CALLBACK] Tokens - Prompt: {usage.prompt_tokens}, Completion: {usage.completion_tokens}, Total: {usage.total_tokens}")
        
        if hasattr(response, 'choices') and response.choices:
            for i, choice in enumerate(response.choices):
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    content = str(choice.message.content)[:100] if choice.message.content else "None"
                    write_log(f"[CALLBACK] Response preview: {content}...")
                    break
    except Exception as e:
        write_log(f"[CALLBACK] Error processing response: {e}")
    
    write_log(f"{'='*60}")


def log_failure(kwargs, response, start_time, end_time):
    """Failure callback function"""
    write_log(f"\n{'='*60}")
    write_log(f"[CALLBACK] FAILURE at {datetime.utcnow().isoformat()}")
    
    # Handle both float timestamps and datetime objects
    try:
        if isinstance(start_time, (int, float)) and isinstance(end_time, (int, float)):
            duration = end_time - start_time
        else:
            duration = (end_time - start_time).total_seconds() if hasattr(end_time - start_time, 'total_seconds') else 0
        write_log(f"[CALLBACK] Duration: {duration:.3f}s")
    except Exception as e:
        write_log(f"[CALLBACK] Duration error: {e}")
    
    try:
        if isinstance(response, Exception):
            write_log(f"[CALLBACK] Error: {type(response).__name__}: {str(response)}")
        else:
            write_log(f"[CALLBACK] Response: {response}")
    except Exception as e:
        write_log(f"[CALLBACK] Error processing failure: {e}")
    
    write_log(f"{'='*60}")


# Export the callbacks
success_callback = log_success
failure_callback = log_failure

# Log when module loads
write_log(f"[simple_callback.py] Module loaded at {datetime.utcnow().isoformat()}")
write_log(f"[simple_callback.py] Log file: {LOG_FILE}")
write_log(f"[simple_callback.py] Python version: {sys.version}")
write_log(f"[simple_callback.py] Working directory: {os.getcwd()}")