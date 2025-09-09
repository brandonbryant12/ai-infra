import os
from datetime import datetime

try:
    from langfuse import Langfuse
except ImportError:
    Langfuse = None
from litellm.integrations.custom_logger import CustomLogger


class LangFuseLogger(CustomLogger):
    """
    Custom Langfuse logger following litellm callback interface.
    This logger redacts all input/output data for privacy while logging
    metadata, usage, and timing information.

    Supports multiple environments (demo, dev, prod) based on API key mapping.

    Environment Variables Required:
    - DEMO_API_KEY, DEV_API_KEY, PROD_API_KEY: API keys to match against
    - DEMO_LANGFUSE_SECRET_KEY, DEMO_LANGFUSE_PUBLIC_KEY, DEMO_LANGFUSE_HOST
    - DEV_LANGFUSE_SECRET_KEY, DEV_LANGFUSE_PUBLIC_KEY, DEV_LANGFUSE_HOST
    - PROD_LANGFUSE_SECRET_KEY, PROD_LANGFUSE_PUBLIC_KEY, PROD_LANGFUSE_HOST

    The logger will automatically select the appropriate Langfuse client based on
    the API key found in the request metadata. Falls back to demo if no match.
    """
    def __init__(
        self,
        flush_interval=1,
    ):
        # Define environment configurations
        self.env_configs = {
            "demo": {
                "secret_key": os.getenv("DEMO_LANGFUSE_SECRET_KEY"),
                "public_key": os.getenv("DEMO_LANGFUSE_PUBLIC_KEY"),
                "host": os.getenv("DEMO_LANGFUSE_HOST", "https://cloud.langfuse.com"),
                "api_key": os.getenv("DEMO_API_KEY"),
            },
            "dev": {
                "secret_key": os.getenv("DEV_LANGFUSE_SECRET_KEY"),
                "public_key": os.getenv("DEV_LANGFUSE_PUBLIC_KEY"),
                "host": os.getenv("DEV_LANGFUSE_HOST", "https://cloud.langfuse.com"),
                "api_key": os.getenv("DEV_API_KEY"),
            },
            "prod": {
                "secret_key": os.getenv("PROD_LANGFUSE_SECRET_KEY"),
                "public_key": os.getenv("PROD_LANGFUSE_PUBLIC_KEY"),
                "host": os.getenv("PROD_LANGFUSE_HOST", "https://cloud.langfuse.com"),
                "api_key": os.getenv("PROD_API_KEY"),
            },
        }

        # Initialize Langfuse clients for each environment
        self.clients = {}
        if Langfuse and callable(Langfuse):
            for env, config in self.env_configs.items():
                if config["secret_key"] and config["public_key"]:
                    try:
                        parameters = {
                            "public_key": config["public_key"],
                            "secret_key": config["secret_key"],
                            "host": config["host"],
                            "flush_interval": flush_interval,
                            "sdk_integration": "litellm",
                        }
                        self.clients[env] = Langfuse(**parameters)
                    except Exception as e:
                        print(f"Warning: Failed to initialize Langfuse client for {env}: {e}")
                else:
                    print(f"Warning: Missing Langfuse credentials for {env} environment")

        else:
            print("Warning: Langfuse not available, logging will be disabled")

    def _get_client_for_api_key(self, api_key):
        """Determine which Langfuse client to use based on API key"""
        # Try to match API key with an environment
        if api_key:
            for env, config in self.env_configs.items():
                if config.get("api_key") == api_key:
                    # Found matching environment - use its client if available
                    client = self.clients.get(env)
                    if client:
                        return client
                    else:
                        # API key matched but environment client not available - skip logging
                        return None

        # No API key provided or no match found - try demo client
        demo_client = self.clients.get("demo")
        if demo_client:
            return demo_client

        # No demo client available - skip logging
        return None

    def _extract_api_key(self, kwargs):
        """Extract API key from request kwargs"""
        # Try different locations where API key might be stored
        api_key = None

        # Check in metadata
        metadata = kwargs.get("metadata", {})
        if metadata:
            api_key = metadata.get("api_key")

        # Check in optional_params
        optional_params = kwargs.get("optional_params", {})
        if not api_key and optional_params:
            api_key = optional_params.get("api_key")

        # Check in extra_body
        if not api_key and "extra_body" in optional_params:
            extra_body = optional_params["extra_body"]
            if isinstance(extra_body, dict):
                api_key = extra_body.get("api_key")

        return api_key

    def log_pre_api_call(self, model, messages, kwargs):
        """Log before API call - create trace"""
        try:
            # Extract API key to determine which client to use
            api_key = self._extract_api_key(kwargs)
            client = self._get_client_for_api_key(api_key)

            if not client:
                print(f"Langfuse: No client available for API key, skipping logging")
                return  # No client available, skip logging

            trace_id = kwargs.get("litellm_call_id", f"trace-{datetime.now().timestamp()}")

            # Extract user and session info from metadata
            metadata = kwargs.get("optional_params", {})
            user_id = None
            session_id = None

            if metadata:
                user_id = metadata.get('user')
                if 'extra_body' in metadata and isinstance(metadata['extra_body'], dict):
                    session_id = metadata['extra_body'].get('session_id')

            trace = client.trace(
                id=trace_id,
                name=f"litellm-{kwargs.get('call_type', 'completion')}",
                input="redacted-by-litellm",
                user_id=user_id,
                session_id=session_id
            )
            kwargs["_langfuse_trace"] = trace
            kwargs["_langfuse_client"] = client  # Store client for later use
        except Exception as e:
            print(f"Langfuse pre-api call error: {e}")

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        """Log successful API call"""
        try:
            trace = kwargs.get("_langfuse_trace")
            if not trace:
                print(f"Langfuse: No trace available for success event, skipping")
                return  # No trace available, skip logging

            usage = None
            if hasattr(response_obj, "usage") and response_obj.usage:
                usage = {
                    "prompt_tokens": getattr(response_obj.usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(response_obj.usage, "completion_tokens", 0),
                }

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
            if not trace:
                print(f"Langfuse: No trace available for failure event, skipping")
                return  # No trace available, skip logging

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

# Global logger instance for easy registration
logger = LangFuseLogger()