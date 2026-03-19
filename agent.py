#!/usr/bin/env python3
"""Agent CLI that calls an LLM and returns structured JSON output.

Usage:
    uv run agent.py "Your question here"

Output:
    JSON to stdout: {"answer": "...", "tool_calls": []}
    Errors to stderr
"""

import json
import os
import sys
import urllib.request
import urllib.error
from typing import Any


def load_env() -> dict[str, str]:
    """Load environment variables from .env.agent.secret.
    
    Also reads from system environment (allows override).
    """
    env = {}
    env_file = ".env.agent.secret"
    
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip().strip('"').strip("'")
    
    # System environment takes precedence
    for key in ["LLM_API_KEY", "LLM_API_BASE", "LLM_MODEL"]:
        if key in os.environ:
            env[key] = os.environ[key]
    
    return env


def call_llm(question: str, api_key: str, api_base: str, model: str) -> str:
    """Call the LLM API and return the answer.
    
    Args:
        question: The user's question
        api_key: API key for authentication
        api_base: Base URL of the API (e.g., http://localhost:8080/v1)
        model: Model name to use
    
    Returns:
        The LLM's text answer
    
    Raises:
        SystemExit: On API error or timeout
    """
    url = f"{api_base}/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    
    body = {
        "model": model,
        "messages": [
            {"role": "user", "content": question}
        ],
        "temperature": 0.0,  # Deterministic answers
    }
    
    data = json.dumps(body).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
            
            # Extract answer from response
            choices = result.get("choices", [])
            if not choices:
                print("No choices in LLM response", file=sys.stderr)
                sys.exit(1)
            
            answer = choices[0].get("message", {}).get("content", "")
            if not answer:
                print("No content in LLM response", file=sys.stderr)
                sys.exit(1)
            
            return answer
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"API error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Cannot reach API: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except TimeoutError:
        print("API request timed out (60s)", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    # Check CLI arguments
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"Your question\"", file=sys.stderr)
        sys.exit(1)
    
    question = sys.argv[1]
    
    # Load configuration
    env = load_env()
    
    api_key = env.get("LLM_API_KEY", "")
    api_base = env.get("LLM_API_BASE", "")
    model = env.get("LLM_MODEL", "qwen3-coder-plus")
    
    # Validate configuration
    if not api_key:
        print("Missing LLM_API_KEY in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    
    if not api_base:
        print("Missing LLM_API_BASE in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    
    # Call the LLM
    answer = call_llm(question, api_key, api_base, model)
    
    # Output JSON result
    result = {
        "answer": answer,
        "tool_calls": []
    }
    
    print(json.dumps(result))


if __name__ == "__main__":
    main()