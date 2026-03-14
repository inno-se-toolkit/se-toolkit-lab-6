#!/usr/bin/env python3
"""
Agent CLI - A simple LLM-powered question answering agent.

Usage:
    uv run agent.py "Your question here"

Output:
    JSON with 'answer' and 'tool_calls' fields to stdout.
    All debug output goes to stderr.
"""

import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv


def load_config() -> dict[str, str]:
    """Load configuration from environment variables."""
    # Load .env.agent.secret from the script's directory
    script_dir = Path(__file__).parent
    env_file = script_dir / ".env.agent.secret"
    load_dotenv(env_file)

    api_key = os.getenv("LLM_API_KEY")
    api_base = os.getenv("LLM_API_BASE")
    model = os.getenv("LLM_MODEL")

    if not api_key:
        print("Error: LLM_API_KEY not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    if not api_base:
        print("Error: LLM_API_BASE not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    if not model:
        print("Error: LLM_MODEL not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)

    return {
        "api_key": api_key,
        "api_base": api_base,
        "model": model,
    }


def call_llm(question: str, config: dict[str, str]) -> str:
    """Call the LLM API and return the answer."""
    api_base = config["api_base"]
    api_key = config["api_key"]
    model = config["model"]

    # Ensure the endpoint ends with /v1
    endpoint = api_base.rstrip("/")
    if not endpoint.endswith("/v1"):
        endpoint = f"{endpoint}/v1"

    url = f"{endpoint}/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": question,
            }
        ],
        "max_tokens": 1024,
    }

    print(f"Calling LLM at {url}...", file=sys.stderr)

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # Extract the answer from the response
            answer = data["choices"][0]["message"]["content"]
            return answer

    except httpx.TimeoutException:
        print("Error: LLM request timed out (60s)", file=sys.stderr)
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        print(f"Error: HTTP error {e.response.status_code}", file=sys.stderr)
        print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Error: Request failed: {e}", file=sys.stderr)
        sys.exit(1)
    except (KeyError, IndexError) as e:
        print(f"Error: Unexpected API response format: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"Your question here\"", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    # Load configuration
    config = load_config()
    print(f"Using model: {config['model']}", file=sys.stderr)

    # Call the LLM
    answer = call_llm(question, config)
    print(f"Got answer from LLM", file=sys.stderr)

    # Format and output the result
    result = {
        "answer": answer,
        "tool_calls": [],
    }

    # Output valid JSON to stdout (single line)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
