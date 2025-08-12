"""
Simple Logging Callback Handler for LiteLLM
Prints all incoming request and response data
"""

import json
import sys
import traceback
from datetime import datetime
from typing import Any, Dict
from litellm.integrations.custom_logger import CustomLogger


class CustomLangfuseLogger(CustomLogger):
    """
    Simple logger that prints all incoming data from LiteLLM requests
    Following the LiteLLM custom callback specification
    """
    
    def __init__(self):
        super().__init__()
        # Print to both stdout and stderr to ensure visibility
        print(f"[CustomLangfuseLogger] INIT: Initialized at {datetime.utcnow().isoformat()}", flush=True, file=sys.stdout)
        print(f"[CustomLangfuseLogger] INIT: Initialized at {datetime.utcnow().isoformat()}", flush=True, file=sys.stderr)
        sys.stdout.flush()
        sys.stderr.flush()
    
    def _print_both(self, message):
        """Helper to print to both stdout and stderr"""
        print(message, flush=True, file=sys.stdout)
        print(message, flush=True, file=sys.stderr)
        sys.stdout.flush()
        sys.stderr.flush()
    
    def log_pre_api_call(self, model, messages, kwargs):
        """
        Called before making the API call
        """
        try:
            self._print_both(f"\n{'='*80}")
            self._print_both(f"[CustomLangfuseLogger] PRE-API CALL")
            self._print_both(f"[CustomLangfuseLogger] Timestamp: {datetime.utcnow().isoformat()}")
            self._print_both(f"-" * 40)
            
            self._print_both(f"  Model: {model}")
            
            self._print_both(f"\n  Messages:")
            for i, msg in enumerate(messages):
                self._print_both(f"    [{i}]: {json.dumps(msg, indent=6)}")
            
            self._print_both(f"\n  Kwargs:")
            for key, value in kwargs.items():
                try:
                    if isinstance(value, (dict, list)):
                        self._print_both(f"    {key}: {json.dumps(value, indent=6)}")
                    else:
                        self._print_both(f"    {key}: {value}")
                except:
                    self._print_both(f"    {key}: {str(value)}")
            
            self._print_both(f"{'='*80}\n")
        except Exception as e:
            self._print_both(f"[CustomLangfuseLogger] ERROR in log_pre_api_call: {str(e)}\n{traceback.format_exc()}")
    
    def log_post_api_call(self, kwargs, response_obj, start_time, end_time):
        """
        Called after receiving the API response
        """
        try:
            self._print_both(f"\n{'='*80}")
            self._print_both(f"[CustomLangfuseLogger] POST-API CALL")
            self._print_both(f"[CustomLangfuseLogger] Timestamp: {datetime.utcnow().isoformat()}")
            self._print_both(f"[CustomLangfuseLogger] Duration: {end_time - start_time:.3f} seconds")
            self._print_both(f"-" * 40)
            
            self._print_both(f"\n  Response Type: {type(response_obj).__name__}")
            
            if hasattr(response_obj, "__dict__"):
                self._print_both(f"\n  Response Attributes:")
                for key, value in response_obj.__dict__.items():
                    try:
                        if isinstance(value, (dict, list)):
                            self._print_both(f"    {key}: {json.dumps(value, indent=6)}")
                        else:
                            self._print_both(f"    {key}: {value}")
                    except:
                        self._print_both(f"    {key}: {str(value)}")
            
            self._print_both(f"{'='*80}\n")
        except Exception as e:
            self._print_both(f"[CustomLangfuseLogger] ERROR in log_post_api_call: {str(e)}\n{traceback.format_exc()}")
    
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        """
        Sync handler for successful completions
        """
        try:
            self._print_both(f"\n{'='*80}")
            self._print_both(f"[CustomLangfuseLogger] SUCCESS EVENT")
            self._print_both(f"[CustomLangfuseLogger] Timestamp: {datetime.utcnow().isoformat()}")
            self._print_both(f"[CustomLangfuseLogger] Duration: {end_time - start_time:.3f} seconds")
            self._print_both(f"-" * 40)
            
            # Print request kwargs
            self._print_both(f"\n  Request kwargs keys: {list(kwargs.keys())}")
            
            # Print messages if present
            if "messages" in kwargs and isinstance(kwargs["messages"], list):
                self._print_both(f"\n  Messages ({len(kwargs['messages'])} total):")
                for i, msg in enumerate(kwargs["messages"]):
                    self._print_both(f"    [{i}]: {json.dumps(msg, indent=8)}")
            
            # Print response
            self._print_both(f"\n  Response Type: {type(response_obj).__name__}")
            
            # Extract usage if available
            if hasattr(response_obj, "usage") and response_obj.usage:
                self._print_both(f"\n  Token Usage:")
                self._print_both(f"    Prompt tokens: {response_obj.usage.prompt_tokens}")
                self._print_both(f"    Completion tokens: {response_obj.usage.completion_tokens}")
                self._print_both(f"    Total tokens: {response_obj.usage.total_tokens}")
            
            # Extract response content
            if hasattr(response_obj, "choices") and response_obj.choices:
                self._print_both(f"\n  Response Content:")
                for i, choice in enumerate(response_obj.choices):
                    if hasattr(choice, "message"):
                        if hasattr(choice.message, "content"):
                            content = choice.message.content
                            if len(str(content)) > 500:
                                content = str(content)[:500] + "..."
                            self._print_both(f"    Choice {i} content: {content}")
            
            self._print_both(f"{'='*80}\n")
        except Exception as e:
            self._print_both(f"[CustomLangfuseLogger] ERROR in log_success_event: {str(e)}\n{traceback.format_exc()}")
    
    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        """
        Async handler for successful completions
        """
        self._print_both(f"[CustomLangfuseLogger] ASYNC SUCCESS EVENT CALLED")
        self.log_success_event(kwargs, response_obj, start_time, end_time)
    
    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """
        Sync handler for failed completions
        """
        try:
            self._print_both(f"\n{'='*80}")
            self._print_both(f"[CustomLangfuseLogger] FAILURE EVENT")
            self._print_both(f"[CustomLangfuseLogger] Timestamp: {datetime.utcnow().isoformat()}")
            self._print_both(f"[CustomLangfuseLogger] Duration: {end_time - start_time:.3f} seconds")
            self._print_both(f"-" * 40)
            
            # Print request kwargs
            self._print_both(f"\n  Request kwargs keys: {list(kwargs.keys())}")
            
            # Print error/response
            self._print_both(f"\n  Error/Response:")
            if isinstance(response_obj, Exception):
                self._print_both(f"    Exception Type: {type(response_obj).__name__}")
                self._print_both(f"    Error Message: {str(response_obj)}")
            else:
                self._print_both(f"    {response_obj}")
            
            self._print_both(f"{'='*80}\n")
        except Exception as e:
            self._print_both(f"[CustomLangfuseLogger] ERROR in log_failure_event: {str(e)}\n{traceback.format_exc()}")
    
    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """
        Async handler for failed completions
        """
        self._print_both(f"[CustomLangfuseLogger] ASYNC FAILURE EVENT CALLED")
        self.log_failure_event(kwargs, response_obj, start_time, end_time)
    
    def log_stream_event(self, kwargs, response_obj, start_time, end_time):
        """
        Sync handler for streaming completions
        """
        try:
            self._print_both(f"\n{'='*80}")
            self._print_both(f"[CustomLangfuseLogger] STREAM EVENT")
            self._print_both(f"[CustomLangfuseLogger] Timestamp: {datetime.utcnow().isoformat()}")
            self._print_both(f"[CustomLangfuseLogger] Duration: {end_time - start_time:.3f} seconds")
            self._print_both(f"-" * 40)
            
            # Print request kwargs
            self._print_both(f"\n  Request kwargs keys: {list(kwargs.keys())}")
            
            # Print streaming response info
            if "complete_streaming_response" in kwargs:
                streaming_response = kwargs.get("complete_streaming_response")
                if streaming_response:
                    self._print_both(f"\n  Streaming Response Type: {type(streaming_response).__name__}")
            
            self._print_both(f"{'='*80}\n")
        except Exception as e:
            self._print_both(f"[CustomLangfuseLogger] ERROR in log_stream_event: {str(e)}\n{traceback.format_exc()}")
    
    async def async_log_stream_event(self, kwargs, response_obj, start_time, end_time):
        """
        Async handler for streaming completions
        """
        self._print_both(f"[CustomLangfuseLogger] ASYNC STREAM EVENT CALLED")
        self.log_stream_event(kwargs, response_obj, start_time, end_time)