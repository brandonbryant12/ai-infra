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
        print(f"[CustomLangfuseLogger] Initialized at {datetime.utcnow().isoformat()}", flush=True)
        sys.stdout.flush()
    
    def log_pre_api_call(self, model, messages, kwargs):
        """
        Called before making the API call
        """
        try:
            print(f"\n{'='*80}", flush=True)
            print(f"[CustomLangfuseLogger] PRE-API CALL", flush=True)
            print(f"[CustomLangfuseLogger] Timestamp: {datetime.utcnow().isoformat()}", flush=True)
            print(f"-" * 40, flush=True)
            
            print(f"  Model: {model}", flush=True)
            
            print(f"\n  Messages:", flush=True)
            for i, msg in enumerate(messages):
                print(f"    [{i}]: {json.dumps(msg, indent=6)}", flush=True)
            
            print(f"\n  Kwargs:", flush=True)
            for key, value in kwargs.items():
                try:
                    if isinstance(value, (dict, list)):
                        print(f"    {key}: {json.dumps(value, indent=6)}", flush=True)
                    else:
                        print(f"    {key}: {value}", flush=True)
                except:
                    print(f"    {key}: {str(value)}", flush=True)
            
            print(f"{'='*80}\n", flush=True)
        except Exception as e:
            print(f"[CustomLangfuseLogger] ERROR in log_pre_api_call: {str(e)}\n{traceback.format_exc()}", flush=True)
    
    def log_post_api_call(self, kwargs, response_obj, start_time, end_time):
        """
        Called after receiving the API response
        """
        try:
            print(f"\n{'='*80}", flush=True)
            print(f"[CustomLangfuseLogger] POST-API CALL", flush=True)
            print(f"[CustomLangfuseLogger] Timestamp: {datetime.utcnow().isoformat()}", flush=True)
            print(f"[CustomLangfuseLogger] Duration: {end_time - start_time:.3f} seconds", flush=True)
            print(f"-" * 40, flush=True)
            
            print(f"\n  Response Type: {type(response_obj).__name__}", flush=True)
            
            if hasattr(response_obj, "__dict__"):
                print(f"\n  Response Attributes:", flush=True)
                for key, value in response_obj.__dict__.items():
                    try:
                        if isinstance(value, (dict, list)):
                            print(f"    {key}: {json.dumps(value, indent=6)}", flush=True)
                        else:
                            print(f"    {key}: {value}", flush=True)
                    except:
                        print(f"    {key}: {str(value)}", flush=True)
            
            print(f"{'='*80}\n", flush=True)
        except Exception as e:
            print(f"[CustomLangfuseLogger] ERROR in log_post_api_call: {str(e)}\n{traceback.format_exc()}", flush=True)
    
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        """
        Sync handler for successful completions
        """
        try:
            print(f"\n{'='*80}", flush=True)
            print(f"[CustomLangfuseLogger] SUCCESS EVENT", flush=True)
            print(f"[CustomLangfuseLogger] Timestamp: {datetime.utcnow().isoformat()}", flush=True)
            print(f"[CustomLangfuseLogger] Duration: {end_time - start_time:.3f} seconds", flush=True)
            print(f"-" * 40, flush=True)
            
            # Print request kwargs
            print(f"\n  Request kwargs:", flush=True)
            for key, value in kwargs.items():
                if key == "messages" and isinstance(value, list):
                    print(f"    {key}:", flush=True)
                    for i, msg in enumerate(value):
                        print(f"      [{i}]: {json.dumps(msg, indent=8)}", flush=True)
                elif key == "litellm_params" and isinstance(value, dict):
                    print(f"    {key}:", flush=True)
                    print(f"      {json.dumps(value, indent=6)}", flush=True)
                else:
                    try:
                        if isinstance(value, (dict, list)):
                            print(f"    {key}: {json.dumps(value, indent=6)}", flush=True)
                        else:
                            print(f"    {key}: {value}", flush=True)
                    except:
                        print(f"    {key}: {str(value)}", flush=True)
            
            # Print response
            print(f"\n  Response:", flush=True)
            if hasattr(response_obj, "__dict__"):
                for key, value in response_obj.__dict__.items():
                    try:
                        if isinstance(value, (dict, list)):
                            print(f"    {key}: {json.dumps(value, indent=6)}", flush=True)
                        else:
                            print(f"    {key}: {value}", flush=True)
                    except:
                        print(f"    {key}: {str(value)}", flush=True)
            else:
                print(f"    {response_obj}", flush=True)
            
            # Extract usage if available
            if hasattr(response_obj, "usage") and response_obj.usage:
                print(f"\n  Token Usage:", flush=True)
                print(f"    Prompt tokens: {response_obj.usage.prompt_tokens}", flush=True)
                print(f"    Completion tokens: {response_obj.usage.completion_tokens}", flush=True)
                print(f"    Total tokens: {response_obj.usage.total_tokens}", flush=True)
            
            # Extract response content
            if hasattr(response_obj, "choices") and response_obj.choices:
                print(f"\n  Response Content:", flush=True)
                for i, choice in enumerate(response_obj.choices):
                    if hasattr(choice, "message"):
                        if hasattr(choice.message, "content"):
                            print(f"    Choice {i} content: {choice.message.content}", flush=True)
                        if hasattr(choice.message, "function_call"):
                            print(f"    Choice {i} function call: {choice.message.function_call}", flush=True)
                        if hasattr(choice.message, "tool_calls"):
                            print(f"    Choice {i} tool calls: {choice.message.tool_calls}", flush=True)
            
            print(f"{'='*80}\n", flush=True)
        except Exception as e:
            print(f"[CustomLangfuseLogger] ERROR in log_success_event: {str(e)}\n{traceback.format_exc()}", flush=True)
    
    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        """
        Async handler for successful completions
        """
        self.log_success_event(kwargs, response_obj, start_time, end_time)
    
    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """
        Sync handler for failed completions
        """
        try:
            print(f"\n{'='*80}", flush=True)
            print(f"[CustomLangfuseLogger] FAILURE EVENT", flush=True)
            print(f"[CustomLangfuseLogger] Timestamp: {datetime.utcnow().isoformat()}", flush=True)
            print(f"[CustomLangfuseLogger] Duration: {end_time - start_time:.3f} seconds", flush=True)
            print(f"-" * 40, flush=True)
            
            # Print request kwargs
            print(f"\n  Request kwargs:", flush=True)
            for key, value in kwargs.items():
                if key == "messages" and isinstance(value, list):
                    print(f"    {key}:", flush=True)
                    for i, msg in enumerate(value):
                        print(f"      [{i}]: {json.dumps(msg, indent=8)}", flush=True)
                else:
                    try:
                        if isinstance(value, (dict, list)):
                            print(f"    {key}: {json.dumps(value, indent=6)}", flush=True)
                        else:
                            print(f"    {key}: {value}", flush=True)
                    except:
                        print(f"    {key}: {str(value)}", flush=True)
            
            # Print error/response
            print(f"\n  Error/Response:", flush=True)
            if isinstance(response_obj, Exception):
                print(f"    Exception Type: {type(response_obj).__name__}", flush=True)
                print(f"    Error Message: {str(response_obj)}", flush=True)
                print(f"    Traceback: {traceback.format_exc()}", flush=True)
            elif hasattr(response_obj, "__dict__"):
                for key, value in response_obj.__dict__.items():
                    try:
                        if isinstance(value, (dict, list)):
                            print(f"    {key}: {json.dumps(value, indent=6)}", flush=True)
                        else:
                            print(f"    {key}: {value}", flush=True)
                    except:
                        print(f"    {key}: {str(value)}", flush=True)
            else:
                print(f"    {response_obj}", flush=True)
            
            print(f"{'='*80}\n", flush=True)
        except Exception as e:
            print(f"[CustomLangfuseLogger] ERROR in log_failure_event: {str(e)}\n{traceback.format_exc()}", flush=True)
    
    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """
        Async handler for failed completions
        """
        self.log_failure_event(kwargs, response_obj, start_time, end_time)
    
    def log_stream_event(self, kwargs, response_obj, start_time, end_time):
        """
        Sync handler for streaming completions
        """
        try:
            print(f"\n{'='*80}", flush=True)
            print(f"[CustomLangfuseLogger] STREAM EVENT", flush=True)
            print(f"[CustomLangfuseLogger] Timestamp: {datetime.utcnow().isoformat()}", flush=True)
            print(f"[CustomLangfuseLogger] Duration: {end_time - start_time:.3f} seconds", flush=True)
            print(f"-" * 40, flush=True)
            
            # Print request kwargs
            print(f"\n  Request kwargs:", flush=True)
            for key, value in kwargs.items():
                if key == "messages" and isinstance(value, list):
                    print(f"    {key}: {len(value)} messages", flush=True)
                elif key != "complete_streaming_response":
                    try:
                        if isinstance(value, (dict, list)):
                            print(f"    {key}: {json.dumps(value, indent=6)}", flush=True)
                        else:
                            print(f"    {key}: {value}", flush=True)
                    except:
                        print(f"    {key}: {str(value)[:100]}...", flush=True)
            
            # Print streaming response if available
            if "complete_streaming_response" in kwargs:
                print(f"\n  Complete Streaming Response:", flush=True)
                streaming_response = kwargs.get("complete_streaming_response")
                if streaming_response:
                    print(f"    Type: {type(streaming_response).__name__}", flush=True)
                    if hasattr(streaming_response, "__dict__"):
                        for key, value in streaming_response.__dict__.items():
                            try:
                                print(f"    {key}: {value if len(str(value)) < 200 else str(value)[:200] + '...'}", flush=True)
                            except:
                                print(f"    {key}: [unable to print]", flush=True)
            
            print(f"{'='*80}\n", flush=True)
        except Exception as e:
            print(f"[CustomLangfuseLogger] ERROR in log_stream_event: {str(e)}\n{traceback.format_exc()}", flush=True)
    
    async def async_log_stream_event(self, kwargs, response_obj, start_time, end_time):
        """
        Async handler for streaming completions
        """
        self.log_stream_event(kwargs, response_obj, start_time, end_time)