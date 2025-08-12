#!/usr/bin/env python3
import asyncio
from typing import Dict, Any

from custom_callbacks import log_incoming_data


async def main() -> None:
    sample: Dict[str, Any] = {
        "headers": {
            "X-OpenWebUI-User-Id": "user-xyz",
            "X-OpenWebUI-Chat-Id": "chat-abc",
        },
        "messages": [{"role": "user", "content": "ping"}],
    }
    print("=== Running log_incoming_data ===")
    result = await log_incoming_data({}, sample, "chat.completions")
    print("=== Callback returned ===")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
