#!/usr/bin/env python3
"""
Agent CLI — Call an LLM and return a structured JSON answer.

Usage:
    uv run agent.py "Your question here"

Output:
    JSON to stdout: {"answer": "...", "tool_calls": []}
    All debug output goes to stderr.
"""

import json
import os
import sys
from pathlib import Path

import httpx
from pydantic_settings import BaseSettings


class AgentSettings(BaseSettings):
    """Settings loaded from .env.agent.secret."""

    llm_api_key: str
    llm_api_base: str
    llm_model: str

    model_config = {
        "env_file": Path(__file__).parent / ".env.agent.secret",
        "env_file_encoding": "utf-8",
    }


def load_settings() -> AgentSettings:
    """Load and validate settings."""
    env_file = Path(__file__).parent / ".env.agent.secret"
    if not env_file.exists():
        print(f"Error: {env_file} not found", file=sys.stderr)
        print("Copy .env.agent.example to .env.agent.secret and fill in your credentials", file=sys.stderr)
        sys.exit(1)

    return AgentSettings()


def call_lllm(question: str, settings: AgentSettings) -> str:
    """Call the LLM API and return the answer."""
    url = f"{settings.llm_api_base}/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.llm_model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer questions concisely and accurately.",
            },
            {"role": "user", "content": question},
        ],
        "temperature": 0.7,
    }

    print(f"Calling LLM at {url}...", file=sys.stderr)

    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()

    data = response.json()

    # Extract answer from OpenAI-compatible response format
    try:
        answer = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        print(f"Error parsing LLM response: {e}", file=sys.stderr)
        print(f"Raw response: {data}", file=sys.stderr)
        sys.exit(1)

    return answer


def main() -> None:
    """Main entry point."""
    # Parse command-line arguments
    if len(sys.argv) != 2:
        print("Usage: uv run agent.py \"Your question here\"", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    # Load settings
    settings = load_settings()
    print(f"Using model: {settings.llm_model}", file=sys.stderr)

    # Call LLM
    answer = call_lllm(question, settings)
    print(f"Received answer from LLM", file=sys.stderr)

    # Output JSON to stdout
    result = {
        "answer": answer,
        "tool_calls": [],
    }

    # Output only valid JSON to stdout
    print(json.dumps(result))


if __name__ == "__main__":
    main()
