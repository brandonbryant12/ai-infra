"""
Simple Logging Callback Handler for LiteLLM
Prints all incoming request and response data
"""

import json
import traceback
from datetime import datetime
from typing import Any, Dict
from litellm.integrations.custom_logger import CustomLogger


class SimpleLogger(CustomLogger):
    """
    Simple logger that prints all incoming data from LiteLLM requests
    Following the LiteLLM custom callback specification
    """
    
    def __init__(self):
        super().__init__()
        print(f"[SimpleLogger] Initialized at {datetime.utcnow().isoformat()}")
    
    def log_pre_api_call(self, model, messages, kwargs):
        """
        Called before making the API call
        """
        try:
            print(f"\n{'='*80}")
            print(f"[SimpleLogger] PRE-API CALL")
            print(f"[SimpleLogger] Timestamp: {datetime.utcnow().isoformat()}")
            print(f"-" * 40)
            
            print(f"  Model: {model}")
            
            print(f"\n  Messages:")
            for i, msg in enumerate(messages):
                print(f"    [{i}]: {json.dumps(msg, indent=6)}")
            
            print(f"\n  Kwargs:")
            for key, value in kwargs.items():
                try:
                    if isinstance(value, (dict, list)):
                        print(f"    {key}: {json.dumps(value, indent=6)}")
                    else:
                        print(f"    {key}: {value}")
                except:
                    print(f"    {key}: {str(value)}")
            
            print(f"{'='*80}\n")
        except Exception as e:
            print(f"[SimpleLogger] ERROR in log_pre_api_call: {str(e)}\n{traceback.format_exc()}")
    
    def log_post_api_call(self, kwargs, response_obj, start_time, end_time):
        """
        Called after receiving the API response
        """
        try:
            print(f"\n{'='*80}")
            print(f"[SimpleLogger] POST-API CALL")
            print(f"[SimpleLogger] Timestamp: {datetime.utcnow().isoformat()}")
            print(f"[SimpleLogger] Duration: {end_time - start_time:.3f} seconds")
            print(f"-" * 40)
            
            print(f"\n  Response Type: {type(response_obj).__name__}")
            
            if hasattr(response_obj, "__dict__"):
                print(f"\n  Response Attributes:")
                for key, value in response_obj.__dict__.items():
                    try:
                        if isinstance(value, (dict, list)):
                            print(f"    {key}: {json.dumps(value, indent=6)}")
                        else:
                            print(f"    {key}: {value}")
                    except:
                        print(f"    {key}: {str(value)}")
            
            print(f"{'='*80}\n")
        except Exception as e:
            print(f"[SimpleLogger] ERROR in log_post_api_call: {str(e)}\n{traceback.format_exc()}")
    
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        """
        Sync handler for successful completions
        """
        try:
            print(f"\n{'='*80}")
            print(f"[SimpleLogger] SUCCESS EVENT")
            print(f"[SimpleLogger] Timestamp: {datetime.utcnow().isoformat()}")
            print(f"[SimpleLogger] Duration: {end_time - start_time:.3f} seconds")
            print(f"-" * 40)
            
            # Print request kwargs
            print(f"\n  Request kwargs:")
            for key, value in kwargs.items():
                if key == "messages" and isinstance(value, list):
                    print(f"    {key}:")
                    for i, msg in enumerate(value):
                        print(f"      [{i}]: {json.dumps(msg, indent=8)}")
                elif key == "litellm_params" and isinstance(value, dict):
                    print(f"    {key}:")
                    print(f"      {json.dumps(value, indent=6)}")
                else:
                    try:
                        if isinstance(value, (dict, list)):
                            print(f"    {key}: {json.dumps(value, indent=6)}")
                        else:
                            print(f"    {key}: {value}")
                    except:
                        print(f"    {key}: {str(value)}")
            
            # Print response
            print(f"\n  Response:")
            if hasattr(response_obj, "__dict__"):
                for key, value in response_obj.__dict__.items():
                    try:
                        if isinstance(value, (dict, list)):
                            print(f"    {key}: {json.dumps(value, indent=6)}")
                        else:
                            print(f"    {key}: {value}")
                    except:
                        print(f"    {key}: {str(value)}")
            else:
                print(f"    {response_obj}")
            
            # Extract usage if available
            if hasattr(response_obj, "usage") and response_obj.usage:
                print(f"\n  Token Usage:")
                print(f"    Prompt tokens: {response_obj.usage.prompt_tokens}")
                print(f"    Completion tokens: {response_obj.usage.completion_tokens}")
                print(f"    Total tokens: {response_obj.usage.total_tokens}")
            
            # Extract response content
            if hasattr(response_obj, "choices") and response_obj.choices:
                print(f"\n  Response Content:")
                for i, choice in enumerate(response_obj.choices):
                    if hasattr(choice, "message"):
                        if hasattr(choice.message, "content"):
                            print(f"    Choice {i} content: {choice.message.content}")
                        if hasattr(choice.message, "function_call"):
                            print(f"    Choice {i} function call: {choice.message.function_call}")
                        if hasattr(choice.message, "tool_calls"):
                            print(f"    Choice {i} tool calls: {choice.message.tool_calls}")
            
            print(f"{'='*80}\n")
        except Exception as e:
            print(f"[SimpleLogger] ERROR in log_success_event: {str(e)}\n{traceback.format_exc()}")
    
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
            print(f"\n{'='*80}")
            print(f"[SimpleLogger] FAILURE EVENT")
            print(f"[SimpleLogger] Timestamp: {datetime.utcnow().isoformat()}")
            print(f"[SimpleLogger] Duration: {end_time - start_time:.3f} seconds")
            print(f"-" * 40)
            
            # Print request kwargs
            print(f"\n  Request kwargs:")
            for key, value in kwargs.items():
                if key == "messages" and isinstance(value, list):
                    print(f"    {key}:")
                    for i, msg in enumerate(value):
                        print(f"      [{i}]: {json.dumps(msg, indent=8)}")
                else:
                    try:
                        if isinstance(value, (dict, list)):
                            print(f"    {key}: {json.dumps(value, indent=6)}")
                        else:
                            print(f"    {key}: {value}")
                    except:
                        print(f"    {key}: {str(value)}")
            
            # Print error/response
            print(f"\n  Error/Response:")
            if isinstance(response_obj, Exception):
                print(f"    Exception Type: {type(response_obj).__name__}")
                print(f"    Error Message: {str(response_obj)}")
                print(f"    Traceback: {traceback.format_exc()}")
            elif hasattr(response_obj, "__dict__"):
                for key, value in response_obj.__dict__.items():
                    try:
                        if isinstance(value, (dict, list)):
                            print(f"    {key}: {json.dumps(value, indent=6)}")
                        else:
                            print(f"    {key}: {value}")
                    except:
                        print(f"    {key}: {str(value)}")
            else:
                print(f"    {response_obj}")
            
            print(f"{'='*80}\n")
        except Exception as e:
            print(f"[SimpleLogger] ERROR in log_failure_event: {str(e)}\n{traceback.format_exc()}")
    
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
            print(f"\n{'='*80}")
            print(f"[SimpleLogger] STREAM EVENT")
            print(f"[SimpleLogger] Timestamp: {datetime.utcnow().isoformat()}")
            print(f"[SimpleLogger] Duration: {end_time - start_time:.3f} seconds")
            print(f"-" * 40)
            
            # Print request kwargs
            print(f"\n  Request kwargs:")
            for key, value in kwargs.items():
                if key == "messages" and isinstance(value, list):
                    print(f"    {key}: {len(value)} messages")
                elif key != "complete_streaming_response":
                    try:
                        if isinstance(value, (dict, list)):
                            print(f"    {key}: {json.dumps(value, indent=6)}")
                        else:
                            print(f"    {key}: {value}")
                    except:
                        print(f"    {key}: {str(value)[:100]}...")
            
            # Print streaming response if available
            if "complete_streaming_response" in kwargs:
                print(f"\n  Complete Streaming Response:")
                streaming_response = kwargs.get("complete_streaming_response")
                if streaming_response:
                    print(f"    Type: {type(streaming_response).__name__}")
                    if hasattr(streaming_response, "__dict__"):
                        for key, value in streaming_response.__dict__.items():
                            try:
                                print(f"    {key}: {value if len(str(value)) < 200 else str(value)[:200] + '...'}")
                            except:
                                print(f"    {key}: [unable to print]")
            
            print(f"{'='*80}\n")
        except Exception as e:
            print(f"[SimpleLogger] ERROR in log_stream_event: {str(e)}\n{traceback.format_exc()}")
    
    async def async_log_stream_event(self, kwargs, response_obj, start_time, end_time):
        """
        Async handler for streaming completions
        """
        self.log_stream_event(kwargs, response_obj, start_time, end_time)