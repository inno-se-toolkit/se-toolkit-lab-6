#!/usr/bin/env python3
"""
Agent CLI - Calls an LLM and returns a structured JSON answer.

Usage:
    uv run agent.py "Your question here"

Output:
    JSON to stdout: {"answer": "...", "tool_calls": []}
    All debug output goes to stderr.
"""

import json
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv


def load_config() -> dict:
    """Load LLM configuration from .env.agent.secret."""
    env_file = Path(__file__).parent / ".env.agent.secret"
    load_dotenv(env_file)

    import os

    config = {
        "api_key": os.getenv("LLM_API_KEY"),
        "api_base": os.getenv("LLM_API_BASE"),
        "model": os.getenv("LLM_MODEL", "qwen3-coder-plus"),
    }

    if not config["api_key"]:
        print("Error: LLM_API_KEY not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    if not config["api_base"]:
        print("Error: LLM_API_BASE not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)

    return config


def call_lllm(question: str, config: dict) -> str:
    """
    Call the LLM API and return the answer.

    Args:
        question: The user's question
        config: LLM configuration (api_key, api_base, model)

    Returns:
        The LLM's text response
    """
    url = f"{config['api_base']}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}",
    }
    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question},
        ],
    }

    print(f"Calling LLM at {url}...", file=sys.stderr)

    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    answer = data["choices"][0]["message"]["content"]
    print(f"Got response from LLM", file=sys.stderr)
    return answer


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"<question>\"", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]
    print(f"Question: {question}", file=sys.stderr)

    # Load configuration
    config = load_config()
    print(f"Using model: {config['model']}", file=sys.stderr)

    # Call LLM
    answer = call_lllm(question, config)

    # Output structured JSON
    result = {
        "answer": answer,
        "tool_calls": [],
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
