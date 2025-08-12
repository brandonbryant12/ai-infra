"""
Simplified callback for LiteLLM - just functions, no classes
"""

import sys
import json
from datetime import datetime


def log_success(kwargs, response, start_time, end_time):
    """Success callback function"""
    print(f"\n{'='*60}", file=sys.stderr, flush=True)
    print(f"[CALLBACK] SUCCESS at {datetime.utcnow().isoformat()}", file=sys.stderr, flush=True)
    print(f"[CALLBACK] Duration: {end_time - start_time:.3f}s", file=sys.stderr, flush=True)
    
    # Log request info
    if "messages" in kwargs:
        print(f"[CALLBACK] Messages: {len(kwargs.get('messages', []))} messages", file=sys.stderr, flush=True)
    
    if "model" in kwargs:
        print(f"[CALLBACK] Model: {kwargs['model']}", file=sys.stderr, flush=True)
    
    # Log response info
    if hasattr(response, 'usage'):
        usage = response.usage
        if usage:
            print(f"[CALLBACK] Tokens - Prompt: {usage.prompt_tokens}, Completion: {usage.completion_tokens}, Total: {usage.total_tokens}", file=sys.stderr, flush=True)
    
    if hasattr(response, 'choices') and response.choices:
        for i, choice in enumerate(response.choices):
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                content = str(choice.message.content)[:100] if choice.message.content else "None"
                print(f"[CALLBACK] Response preview: {content}...", file=sys.stderr, flush=True)
                break
    
    print(f"{'='*60}", file=sys.stderr, flush=True)
    sys.stderr.flush()


def log_failure(kwargs, response, start_time, end_time):
    """Failure callback function"""
    print(f"\n{'='*60}", file=sys.stderr, flush=True)
    print(f"[CALLBACK] FAILURE at {datetime.utcnow().isoformat()}", file=sys.stderr, flush=True)
    print(f"[CALLBACK] Duration: {end_time - start_time:.3f}s", file=sys.stderr, flush=True)
    
    if isinstance(response, Exception):
        print(f"[CALLBACK] Error: {type(response).__name__}: {str(response)}", file=sys.stderr, flush=True)
    else:
        print(f"[CALLBACK] Response: {response}", file=sys.stderr, flush=True)
    
    print(f"{'='*60}", file=sys.stderr, flush=True)
    sys.stderr.flush()


# Export the callbacks
success_callback = log_success
failure_callback = log_failure

print(f"[simple_callback.py] Module loaded at {datetime.utcnow().isoformat()}", file=sys.stderr, flush=True)