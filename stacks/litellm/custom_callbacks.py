"""
LiteLLM custom callbacks.

- log_incoming_data: logs the full incoming request payload to stdout
- log_incoming_and_map: logs, then delegates to the existing OpenWebUI→Langfuse mapper
"""
from __future__ import annotations

import json
from typing import Any, Dict

# Using print for guaranteed stdout emission inside Docker logs

async def log_incoming_data(
    user_api_key_dict: Dict[str, Any],
    data: Dict[str, Any],
    call_type: str,
):
    """Log the full incoming request payload and return it unchanged.
    This is a pre-call hook; LiteLLM will pass the request body as `data`.
    """
    try:
        print("[LiteLLM-Callback] Incoming request")
        print(f"[LiteLLM-Callback] call_type={call_type}")
        # Pretty-print JSON; fallback to str for non-serializable entries
        print(
            "[LiteLLM-Callback] data="
            + json.dumps(data, indent=2, ensure_ascii=False, default=str)
        )
    except Exception as exc:  # Never block requests on logging failures
        print(f"[LiteLLM-Callback] Logging failed: {exc}")
    return data

# Optional: preserve existing mapping behavior by delegating after logging
try:
    from openwebui_langfuse_hook import map_openwebui_to_langfuse
except Exception:  # If not present, define a no-op fallback
    async def map_openwebui_to_langfuse(
        user_api_key_dict: Dict[str, Any],
        data: Dict[str, Any],
        call_type: str,
    ):
        return data


async def log_incoming_and_map(
    user_api_key_dict: Dict[str, Any],
    data: Dict[str, Any],
    call_type: str,
):
    """Log incoming payload, then run the existing mapping hook."""
    data = await log_incoming_data(user_api_key_dict, data, call_type)
    return await map_openwebui_to_langfuse(user_api_key_dict, data, call_type)
