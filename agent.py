#!/usr/bin/env python3
"""Agent CLI — answers questions using an LLM.

Usage:
    uv run agent.py "What does REST stand for?"

Output (JSON to stdout):
    {"answer": "Representational State Transfer.", "tool_calls": []}

All debug output goes to stderr.
"""

import json
import sys
from pathlib import Path

import httpx

# Load environment variables from .env.agent.secret
env_file = Path(__file__).parent / ".env.agent.secret"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            import os
            os.environ.setdefault(key.strip(), value.strip())

LLM_API_KEY = sys.modules["os"].environ.get("LLM_API_KEY")
LLM_API_BASE = sys.modules["os"].environ.get("LLM_API_BASE")
LLM_MODEL = sys.modules["os"].environ.get("LLM_MODEL")


def main():
    # Validate arguments
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py <question>", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    # Validate environment
    if not LLM_API_KEY:
        print("Error: LLM_API_KEY not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    if not LLM_API_BASE:
        print("Error: LLM_API_BASE not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    if not LLM_MODEL:
        print("Error: LLM_MODEL not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)

    print(f"Sending question to LLM: {question}", file=sys.stderr)

    # Build request
    url = f"{LLM_API_BASE}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}",
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question},
        ],
    }

    try:
        # Send request with 60 second timeout
        print(f"POST {url}", file=sys.stderr)
        response = httpx.post(url, headers=headers, json=payload, timeout=60.0)
        response.raise_for_status()

        # Parse response
        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        # Output result
        result = {
            "answer": answer,
            "tool_calls": [],
        }
        print(json.dumps(result))

        print("Response received successfully", file=sys.stderr)
        sys.exit(0)

    except httpx.TimeoutException as e:
        print(f"Error: Request timed out after 60 seconds: {e}", file=sys.stderr)
        result = {"answer": "Request timed out.", "tool_calls": []}
        print(json.dumps(result))
        sys.exit(1)
    except httpx.HTTPError as e:
        print(f"Error: HTTP request failed: {e}", file=sys.stderr)
        result = {"answer": f"API error: {e}", "tool_calls": []}
        print(json.dumps(result))
        sys.exit(1)
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error: Failed to parse response: {e}", file=sys.stderr)
        result = {"answer": "Failed to parse LLM response.", "tool_calls": []}
        print(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
