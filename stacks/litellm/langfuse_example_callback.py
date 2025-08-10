"""
Example Langfuse callback for LiteLLM demonstrating proper SDK usage.

This callback creates structured traces with generations for LLM requests,
following Langfuse API best practices.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional
import uuid

try:
    from langfuse import get_client
    langfuse_client = get_client()
    LANGFUSE_AVAILABLE = True
except ImportError:
    langfuse_client = None
    LANGFUSE_AVAILABLE = False

# Store active traces for completion callbacks
_active_traces = {}


async def langfuse_example_callback(
    user_api_key_dict: Dict[str, Any],
    data: Dict[str, Any],
    call_type: str,
):
    """
    Example Langfuse callback that creates proper traces and generations.
    
    This demonstrates:
    - Creating traces with user context
    - Creating generations for LLM calls
    - Proper error handling
    - Following Langfuse SDK best practices
    """
    if not LANGFUSE_AVAILABLE:
        print("[Langfuse-Example] SDK not available, skipping trace creation")
        return data
    
    try:
        # Generate a unique trace ID for this request
        trace_id = str(uuid.uuid4())
        
        # Create a trace with proper context
        with langfuse_client.start_as_current_span(name="litellm-request") as root_span:
            # Set trace attributes
            root_span.update_trace(
                name="litellm-api-call",
                user_id=user_api_key_dict.get("user_id", "anonymous"),
                session_id=data.get("metadata", {}).get("session_id"),
                tags=["litellm", call_type, data.get("model", "unknown")],
                metadata={
                    "call_type": call_type,
                    "model": data.get("model"),
                    "temperature": data.get("temperature"),
                    "max_tokens": data.get("max_tokens"),
                    "api_key_prefix": user_api_key_dict.get("api_key", "")[:8] + "..." if user_api_key_dict.get("api_key") else None
                }
            )
            
            # Create a generation for the LLM call
            with langfuse_client.start_as_current_generation(
                name="llm-completion",
                model=data.get("model", "unknown")
            ) as generation:
                
                # Extract input messages
                messages = data.get("messages", [])
                input_text = ""
                if messages:
                    # Format messages for better readability
                    input_text = "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in messages])
                
                # Update generation with input
                generation.update(
                    input=input_text,
                    metadata={
                        "message_count": len(messages),
                        "system_message": any(msg.get("role") == "system" for msg in messages),
                        "request_id": data.get("metadata", {}).get("request_id")
                    }
                )
                
                # Store trace info for potential completion callback
                _active_traces[trace_id] = {
                    "generation": generation,
                    "root_span": root_span,
                    "start_time": data.get("timestamp")
                }
        
        # Add trace ID to data for potential use in completion
        if "metadata" not in data:
            data["metadata"] = {}
        data["metadata"]["langfuse_trace_id"] = trace_id
        
        print(f"[Langfuse-Example] Created trace {trace_id} for {call_type} with model {data.get('model')}")
        
    except Exception as exc:
        print(f"[Langfuse-Example] Failed to create trace: {exc}")
    
    return data


async def langfuse_completion_callback(
    user_api_key_dict: Dict[str, Any],
    response_data: Dict[str, Any],
    call_type: str,
):
    """
    Example completion callback to finalize traces with response data.
    
    This should be called after LLM completion to log outputs and usage.
    """
    if not LANGFUSE_AVAILABLE:
        return response_data
    
    try:
        # Get trace ID from response metadata
        trace_id = response_data.get("metadata", {}).get("langfuse_trace_id")
        if not trace_id or trace_id not in _active_traces:
            print("[Langfuse-Example] No active trace found for completion")
            return response_data
        
        trace_info = _active_traces.pop(trace_id)
        generation = trace_info["generation"]
        root_span = trace_info["root_span"]
        
        # Extract response content
        choices = response_data.get("choices", [])
        output_text = ""
        if choices:
            output_text = choices[0].get("message", {}).get("content", "")
        
        # Update generation with output and usage
        usage = response_data.get("usage", {})
        generation.update(
            output=output_text,
            usage_details={
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            } if usage else None,
            metadata={
                "finish_reason": choices[0].get("finish_reason") if choices else None,
                "response_id": response_data.get("id"),
                "model_response": response_data.get("model")
            }
        )
        
        # Update trace with final output
        root_span.update_trace(
            output={"response": output_text, "usage": usage},
            metadata={
                "completed": True,
                "total_tokens": usage.get("total_tokens", 0) if usage else 0
            }
        )
        
        print(f"[Langfuse-Example] Completed trace {trace_id}")
        
    except Exception as exc:
        print(f"[Langfuse-Example] Failed to complete trace: {exc}")
    
    return response_data