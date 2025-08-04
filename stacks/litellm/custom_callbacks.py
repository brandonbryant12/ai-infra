"""
Optional LiteLLM custom callbacks.

Note:

* The repo mounts this file read-only. Providing a stub prevents Docker from
  failing on a missing host path.
* Built-in Langfuse callbacks are enabled via:
  success\_callback: \["langfuse"]
  failure\_callback: \["langfuse"]
  in config.yaml.j2 and environment variables LANGFUSE\_\*.
  """

from typing import Any, Dict

def noop\_callback(\*args: Any, \*\*kwargs: Dict\[str, Any]) -> None:
"""A no-op callback you can wire for local debugging if needed."""
return
======

```