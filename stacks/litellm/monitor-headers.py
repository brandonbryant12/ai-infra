#!/usr/bin/env python3
"""
Monitor LiteLLM logs to see what headers are received from OpenWebUI
"""
import subprocess
import time
import re

print("Monitoring LiteLLM logs for incoming headers...")
print("Make a request through OpenWebUI UI to see what headers are sent")
print("="*60)

# Start monitoring logs
process = subprocess.Popen(
    ["docker", "compose", "logs", "-f", "litellm"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True
)

header_pattern = re.compile(r'(X-OpenWebUI-|x-openwebui-|headers|Headers|USER|user)')
request_pattern = re.compile(r'(POST|GET).*chat/completions')

try:
    while True:
        line = process.stdout.readline()
        if line:
            # Look for request lines
            if request_pattern.search(line):
                print(f"\n🔵 REQUEST: {line.strip()}")
            # Look for header-related lines
            elif header_pattern.search(line):
                print(f"📋 HEADER: {line.strip()}")
            # Also print lines with user IDs
            elif "user_id" in line or "user-id" in line:
                print(f"👤 USER: {line.strip()}")
except KeyboardInterrupt:
    print("\nStopping monitor...")
    process.terminate()