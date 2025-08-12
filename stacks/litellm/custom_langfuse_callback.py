"""
Simple Logging Callback Handler for LiteLLM
Prints all incoming request and response data
"""

import json
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from litellm.integrations.custom_logger import CustomLogger


def _print_both(message):
    """Helper to print to both stdout and stderr"""
    print(message, flush=True, file=sys.stdout)
    print(message, flush=True, file=sys.stderr)
    sys.stdout.flush()
    sys.stderr.flush()


class CustomLangfuseLoggerInstance(CustomLogger):
    """
    Simple logger that prints all incoming data from LiteLLM requests
    Following the LiteLLM custom callback specification
    """
    
    def __init__(self):
        super().__init__()
        # Print to both stdout and stderr to ensure visibility
        _print_both(f"[CustomLangfuseLogger] INIT: Instance created at {datetime.utcnow().isoformat()}")
    
    def log_pre_api_call(self, model, messages, kwargs):
        """
        Called before making the API call
        """
        try:
            _print_both(f"\n{'='*80}")
            _print_both(f"[CustomLangfuseLogger] PRE-API CALL")
            _print_both(f"[CustomLangfuseLogger] Timestamp: {datetime.utcnow().isoformat()}")
            _print_both(f"-" * 40)
            
            _print_both(f"  Model: {model}")
            
            _print_both(f"\n  Messages:")
            for i, msg in enumerate(messages):
                _print_both(f"    [{i}]: {json.dumps(msg, indent=6)}")
            
            _print_both(f"\n  Kwargs keys: {list(kwargs.keys())}")
            
            _print_both(f"{'='*80}\n")
        except Exception as e:
            _print_both(f"[CustomLangfuseLogger] ERROR in log_pre_api_call: {str(e)}\n{traceback.format_exc()}")
    
    def log_post_api_call(self, kwargs, response_obj, start_time, end_time):
        """
        Called after receiving the API response
        """
        try:
            _print_both(f"\n{'='*80}")
            _print_both(f"[CustomLangfuseLogger] POST-API CALL")
            _print_both(f"[CustomLangfuseLogger] Timestamp: {datetime.utcnow().isoformat()}")
            _print_both(f"[CustomLangfuseLogger] Duration: {end_time - start_time:.3f} seconds")
            _print_both(f"-" * 40)
            
            _print_both(f"\n  Response Type: {type(response_obj).__name__}")
            
            _print_both(f"{'='*80}\n")
        except Exception as e:
            _print_both(f"[CustomLangfuseLogger] ERROR in log_post_api_call: {str(e)}\n{traceback.format_exc()}")
    
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        """
        Sync handler for successful completions
        """
        try:
            _print_both(f"\n{'='*80}")
            _print_both(f"[CustomLangfuseLogger] SUCCESS EVENT")
            _print_both(f"[CustomLangfuseLogger] Timestamp: {datetime.utcnow().isoformat()}")
            _print_both(f"[CustomLangfuseLogger] Duration: {end_time - start_time:.3f} seconds")
            _print_both(f"-" * 40)
            
            # Print request kwargs
            _print_both(f"\n  Request kwargs keys: {list(kwargs.keys())}")
            
            # Print messages if present
            if "messages" in kwargs and isinstance(kwargs["messages"], list):
                _print_both(f"\n  Messages ({len(kwargs['messages'])} total)")
            
            # Print response
            _print_both(f"\n  Response Type: {type(response_obj).__name__}")
            
            # Extract usage if available
            if hasattr(response_obj, "usage") and response_obj.usage:
                _print_both(f"\n  Token Usage:")
                _print_both(f"    Prompt tokens: {response_obj.usage.prompt_tokens}")
                _print_both(f"    Completion tokens: {response_obj.usage.completion_tokens}")
                _print_both(f"    Total tokens: {response_obj.usage.total_tokens}")
            
            # Extract response content
            if hasattr(response_obj, "choices") and response_obj.choices:
                _print_both(f"\n  Response has {len(response_obj.choices)} choices")
                for i, choice in enumerate(response_obj.choices):
                    if hasattr(choice, "message") and hasattr(choice.message, "content"):
                        content = choice.message.content
                        if content and len(str(content)) > 200:
                            content = str(content)[:200] + "..."
                        _print_both(f"    Choice {i} preview: {content}")
            
            _print_both(f"{'='*80}\n")
        except Exception as e:
            _print_both(f"[CustomLangfuseLogger] ERROR in log_success_event: {str(e)}\n{traceback.format_exc()}")
    
    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        """
        Async handler for successful completions
        """
        _print_both(f"[CustomLangfuseLogger] ASYNC SUCCESS EVENT CALLED")
        self.log_success_event(kwargs, response_obj, start_time, end_time)
    
    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """
        Sync handler for failed completions
        """
        try:
            _print_both(f"\n{'='*80}")
            _print_both(f"[CustomLangfuseLogger] FAILURE EVENT")
            _print_both(f"[CustomLangfuseLogger] Timestamp: {datetime.utcnow().isoformat()}")
            _print_both(f"[CustomLangfuseLogger] Duration: {end_time - start_time:.3f} seconds")
            _print_both(f"-" * 40)
            
            # Print error/response
            _print_both(f"\n  Error/Response:")
            if isinstance(response_obj, Exception):
                _print_both(f"    Exception Type: {type(response_obj).__name__}")
                _print_both(f"    Error Message: {str(response_obj)}")
            else:
                _print_both(f"    {response_obj}")
            
            _print_both(f"{'='*80}\n")
        except Exception as e:
            _print_both(f"[CustomLangfuseLogger] ERROR in log_failure_event: {str(e)}\n{traceback.format_exc()}")
    
    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """
        Async handler for failed completions
        """
        _print_both(f"[CustomLangfuseLogger] ASYNC FAILURE EVENT CALLED")
        self.log_failure_event(kwargs, response_obj, start_time, end_time)
    
    def log_stream_event(self, kwargs, response_obj, start_time, end_time):
        """
        Sync handler for streaming completions
        """
        try:
            _print_both(f"\n{'='*80}")
            _print_both(f"[CustomLangfuseLogger] STREAM EVENT")
            _print_both(f"[CustomLangfuseLogger] Timestamp: {datetime.utcnow().isoformat()}")
            _print_both(f"[CustomLangfuseLogger] Duration: {end_time - start_time:.3f} seconds")
            
            _print_both(f"\n  Stream event completed")
            
            _print_both(f"{'='*80}\n")
        except Exception as e:
            _print_both(f"[CustomLangfuseLogger] ERROR in log_stream_event: {str(e)}\n{traceback.format_exc()}")
    
    async def async_log_stream_event(self, kwargs, response_obj, start_time, end_time):
        """
        Async handler for streaming completions
        """
        _print_both(f"[CustomLangfuseLogger] ASYNC STREAM EVENT CALLED")
        self.log_stream_event(kwargs, response_obj, start_time, end_time)


# Create a singleton instance
_logger_instance = CustomLangfuseLoggerInstance()

# Export the class that LiteLLM expects (this will be instantiated by LiteLLM)
class CustomLangfuseLogger(CustomLogger):
    """
    Wrapper class that LiteLLM will instantiate
    Delegates all calls to the singleton instance
    """
    
    def __init__(self, *args, **kwargs):
        # Accept any arguments LiteLLM passes but ignore them
        super().__init__()
        _print_both(f"[CustomLangfuseLogger] Wrapper instantiated with args: {len(args)} positional, kwargs: {list(kwargs.keys())}")
    
    def log_pre_api_call(self, model, messages, kwargs):
        return _logger_instance.log_pre_api_call(model, messages, kwargs)
    
    def log_post_api_call(self, kwargs, response_obj, start_time, end_time):
        return _logger_instance.log_post_api_call(kwargs, response_obj, start_time, end_time)
    
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        return _logger_instance.log_success_event(kwargs, response_obj, start_time, end_time)
    
    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        return await _logger_instance.async_log_success_event(kwargs, response_obj, start_time, end_time)
    
    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        return _logger_instance.log_failure_event(kwargs, response_obj, start_time, end_time)
    
    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        return await _logger_instance.async_log_failure_event(kwargs, response_obj, start_time, end_time)
    
    def log_stream_event(self, kwargs, response_obj, start_time, end_time):
        return _logger_instance.log_stream_event(kwargs, response_obj, start_time, end_time)
    
    async def async_log_stream_event(self, kwargs, response_obj, start_time, end_time):
        return await _logger_instance.async_log_stream_event(kwargs, response_obj, start_time, end_time)


# Also create a function callback for compatibility
def custom_callback_function(kwargs, completion_response, start_time, end_time):
    """
    Function-based callback for LiteLLM
    """
    _print_both(f"[CustomLangfuseLogger] FUNCTION CALLBACK CALLED")
    _print_both(f"[CustomLangfuseLogger] Duration: {end_time - start_time:.3f} seconds")
    _print_both(f"[CustomLangfuseLogger] Response type: {type(completion_response).__name__}")
    
    if hasattr(completion_response, "usage") and completion_response.usage:
        _print_both(f"[CustomLangfuseLogger] Tokens - Prompt: {completion_response.usage.prompt_tokens}, "
                   f"Completion: {completion_response.usage.completion_tokens}, "
                   f"Total: {completion_response.usage.total_tokens}")