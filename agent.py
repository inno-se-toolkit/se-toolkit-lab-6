#!/usr/bin/env python3
"""
Agent CLI - Calls an LLM to answer questions.

Usage:
    uv run agent.py "Your question here"

Output:
    JSON with "answer" and "tool_calls" fields to stdout.
    All debug output goes to stderr.
"""

import json
import os
import sys

import httpx
from dotenv import load_dotenv


def load_env():
    """Load environment variables from .env.agent.secret."""
    # Load from .env.agent.secret in the project root
    load_dotenv(".env.agent.secret")
    
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
    
    return api_key, api_base, model


def call_llm(question: str, api_key: str, api_base: str, model: str) -> str:
    """
    Call the LLM API with the user's question.
    
    Args:
        question: The user's question
        api_key: API key for authentication
        api_base: Base URL of the LLM API
        model: Model name to use
    
    Returns:
        The LLM's text response
    """
    url = f"{api_base}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    body = {
        "model": model,
        "messages": [
            {"role": "user", "content": question}
        ],
    }
    
    print(f"Calling LLM at {url}...", file=sys.stderr)
    
    try:
        response = httpx.post(url, headers=headers, json=body, timeout=60.0)
        response.raise_for_status()
    except httpx.TimeoutException:
        print("Error: LLM request timed out (60s)", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Error: Failed to connect to LLM: {e}", file=sys.stderr)
        sys.exit(1)
    
    data = response.json()
    
    # Extract the answer from the response
    try:
        answer = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        print(f"Error: Unexpected API response format: {e}", file=sys.stderr)
        print(f"Response: {data}", file=sys.stderr)
        sys.exit(1)
    
    return answer


def main():
    """Main entry point."""
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"Your question here\"", file=sys.stderr)
        sys.exit(1)
    
    question = sys.argv[1]
    
    # Load environment variables
    api_key, api_base, model = load_env()
    
    # Call the LLM
    answer = call_llm(question, api_key, api_base, model)
    
    # Output JSON to stdout
    output = {
        "answer": answer,
        "tool_calls": []
    }
    
    print(json.dumps(output))


if __name__ == "__main__":
    main()
