#!/usr/bin/env python3
"""
Agent CLI - Task 1: Call an LLM from Code

A simple CLI agent that takes a question, sends it to an LLM,
and returns a structured JSON answer.

Usage:
    uv run agent.py "What does REST stand for?"

Output:
    {"answer": "Representational State Transfer.", "tool_calls": []}
"""

import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv


def load_llm_config() -> dict:
    """
    Load LLM configuration from environment variables.

    Reads from:
    1. Direct environment variables (highest priority)
    2. .env.agent.secret file (for local development)

    Returns:
        dict with keys: LLM_API_KEY, LLM_API_BASE, LLM_MODEL

    Raises:
        SystemExit: If required configuration is missing
    """
    # First, try to load from .env.agent.secret file (local development)
    env_file = Path(__file__).parent / ".env.agent.secret"
    if env_file.exists():
        load_dotenv(env_file)

    # Read from environment variables (works for both local and autochecker)
    api_key = os.getenv("LLM_API_KEY")
    api_base = os.getenv("LLM_API_BASE")
    model = os.getenv("LLM_MODEL")

    if not api_key:
        print("Error: LLM_API_KEY not found in environment variables", file=sys.stderr)
        sys.exit(1)

    if not api_base:
        print("Error: LLM_API_BASE not found in environment variables", file=sys.stderr)
        sys.exit(1)

    if not model:
        print("Error: LLM_MODEL not found in environment variables", file=sys.stderr)
        sys.exit(1)

    return {
        "api_key": api_key,
        "api_base": api_base,
        "model": model,
    }


def call_llm(question: str, config: dict, timeout: int = 60) -> str:
    """
    Send a question to the LLM and get the answer.

    Args:
        question: The user's question
        config: LLM configuration (api_key, api_base, model)
        timeout: Request timeout in seconds (default: 60)

    Returns:
        The LLM's answer as a string

    Raises:
        SystemExit: If the API call fails
    """
    url = f"{config['api_base']}/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}",
    }

    payload = {
        "model": config["model"],
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer questions concisely and accurately.",
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        "temperature": 0.7,
    }

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # Extract the answer from the response
            answer = data["choices"][0]["message"]["content"]
            return answer

    except httpx.TimeoutException:
        print(f"Error: LLM API timeout after {timeout} seconds", file=sys.stderr)
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        print(f"Error: LLM API returned status {e.response.status_code}", file=sys.stderr)
        print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Error: Failed to connect to LLM API: {e}", file=sys.stderr)
        sys.exit(1)
    except (KeyError, IndexError) as e:
        print(f"Error: Invalid response format from LLM API: {e}", file=sys.stderr)
        sys.exit(1)


def format_response(answer: str, tool_calls: list) -> dict:
    """
    Build the structured JSON response.

    Args:
        answer: The LLM's answer
        tool_calls: List of tool calls (empty for Task 1)

    Returns:
        dict with 'answer' and 'tool_calls' fields
    """
    return {
        "answer": answer,
        "tool_calls": tool_calls,
    }


def main():
    """
    Main entry point for the agent CLI.

    Usage: agent.py "your question"

    Outputs valid JSON to stdout.
    All errors go to stderr.
    Exit code 0 on success, 1 on error.
    """
    # Check for question argument
    if len(sys.argv) < 2:
        print("Error: Missing question argument", file=sys.stderr)
        print('Usage: uv run agent.py "your question"', file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    # Load LLM configuration
    config = load_llm_config()

    # Call the LLM
    answer = call_llm(question, config)

    # Format and output the response
    response = format_response(answer, tool_calls=[])

    # Output valid JSON to stdout (single line)
    print(json.dumps(response, ensure_ascii=False))

    sys.exit(0)


if __name__ == "__main__":
    main()
