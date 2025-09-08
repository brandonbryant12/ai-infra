# Simplified Langfuse Logger
import os
import traceback
from datetime import datetime
from typing import Any, Dict, Optional, Union

try:
    from langfuse import Langfuse
except ImportError:
    Langfuse = None

# Simple CustomLogger base class
class CustomLogger:
    def log_pre_api_call(self, model, messages, kwargs):
        pass

    def log_post_api_call(self, kwargs, response_obj, start_time, end_time):
        pass

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        pass

    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        pass

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        pass

    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        pass

class LangFuseLogger(CustomLogger):
    def __init__(
        self,
        langfuse_public_key=None,
        langfuse_secret=None,
        langfuse_host=None,
        flush_interval=1,
    ):
        if Langfuse is None:
            raise Exception(
                "Langfuse not installed, try running 'pip install langfuse'"
            )

        # Simplified initialization - no complex version checks or upstream logic
        self.secret_key = langfuse_secret or os.getenv("LANGFUSE_SECRET_KEY")
        self.public_key = langfuse_public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
        self.langfuse_host = langfuse_host or os.getenv("LANGFUSE_HOST")

        # Always set sdk_integration since SDK >= 2.6.0
        parameters = {
            "public_key": self.public_key,
            "secret_key": self.secret_key,
            "host": self.langfuse_host,
            "flush_interval": flush_interval,
            "sdk_integration": "litellm",
        }

        self.Langfuse = Langfuse(**parameters)  # type: ignore

    def log_pre_api_call(self, model, messages, kwargs):
        """Log before API call - create trace"""
        try:
            trace_id = kwargs.get("litellm_call_id", f"trace-{datetime.now().timestamp()}")
            trace = self.Langfuse.trace(
                id=trace_id,
                name=f"litellm-{kwargs.get('call_type', 'completion')}",
                input="redacted-by-litellm",
            )
            # Store trace for later use
            kwargs["_langfuse_trace"] = trace
        except Exception as e:
            print(f"Langfuse pre-api call error: {e}")

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        """Log successful API call"""
        try:
            trace = kwargs.get("_langfuse_trace")
            if trace:
                # Extract usage information
                usage = None
                if hasattr(response_obj, "usage") and response_obj.usage:
                    usage = {
                        "prompt_tokens": getattr(response_obj.usage, "prompt_tokens", 0),
                        "completion_tokens": getattr(response_obj.usage, "completion_tokens", 0),
                    }

                # Extract output content
                output = self._extract_output(response_obj)

                # Create generation
                trace.generation(
                    name=f"litellm-{kwargs.get('call_type', 'completion')}",
                    start_time=start_time,
                    end_time=end_time,
                    model=kwargs.get("model", ""),
                    input="redacted-by-litellm",
                    output="redacted-by-litellm",
                    usage=usage,
                    metadata=kwargs.get("metadata", {}),
                )
        except Exception as e:
            print(f"Langfuse success event error: {e}")

    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """Log failed API call"""
        try:
            trace = kwargs.get("_langfuse_trace")
            if trace:
                # Create generation with error
                trace.generation(
                    name=f"litellm-{kwargs.get('call_type', 'completion')}",
                    start_time=start_time,
                    end_time=end_time,
                    model=kwargs.get("model", ""),
                    input="redacted-by-litellm",
                    output="redacted-by-litellm",
                    level="ERROR",
                    status_message=str(response_obj) if response_obj else "Unknown error",
                    metadata=kwargs.get("metadata", {}),
                )
        except Exception as e:
            print(f"Langfuse failure event error: {e}")

    def log_post_api_call(self, kwargs, response_obj, start_time, end_time):
        """Post API call logging - can be used for additional processing"""
        pass

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        """Async version of success logging"""
        self.log_success_event(kwargs, response_obj, start_time, end_time)

    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """Async version of failure logging"""
        self.log_failure_event(kwargs, response_obj, start_time, end_time)

    def _extract_output(self, response_obj):
        """Extract output content from response object"""
        if not response_obj:
            return None

        # Handle different response types
        if hasattr(response_obj, "choices") and response_obj.choices:
            choice = response_obj.choices[0]
            if hasattr(choice, "message") and choice.message:
                return choice.message.content
            elif hasattr(choice, "text"):
                return choice.text

        # Fallback to string representation
        return str(response_obj)

# Global logger instance
logger = LangFuseLogger()