#!/usr/bin/env python3
"""
Agent CLI - Calls an LLM to answer questions.

Usage:
    uv run agent.py "Your question here"

Output:
    JSON with 'answer' and 'tool_calls' fields to stdout.
    All debug/logging output goes to stderr.
"""

import json
import os
import sys

import httpx


def load_env_vars() -> dict[str, str]:
    """Load LLM configuration from environment variables."""
    required_vars = ["LLM_API_KEY", "LLM_API_BASE", "LLM_MODEL"]
    env_vars = {}

    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            print(
                f"Error: Missing required environment variable: {var}", file=sys.stderr
            )
            print(
                "Make sure .env.agent.secret exists and is loaded (e.g., via direnv or export)",
                file=sys.stderr,
            )
            sys.exit(1)
        env_vars[var] = value

    return env_vars


def call_llm_gemini(question: str, api_key: str, model: str) -> str:
    """
    Call Google Gemini API and return the answer.

    Args:
        question: The user's question
        api_key: API key for authentication
        model: Model name to use

    Returns:
        The LLM's answer as a string
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "contents": [{"parts": [{"text": question}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 500,
        },
    }

    print(f"Calling Gemini API for model {model}...", file=sys.stderr)

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # Extract the answer from Gemini response
            if "candidates" in data and len(data["candidates"]) > 0:
                answer = data["candidates"][0]["content"]["parts"][0]["text"]
                return answer
            else:
                print(f"Unexpected response format: {data}", file=sys.stderr)
                sys.exit(1)

    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Request error: {e}", file=sys.stderr)
        sys.exit(1)
    except (KeyError, IndexError) as e:
        print(f"Unexpected response format: {e}", file=sys.stderr)
        sys.exit(1)


def call_llm_openai(question: str, api_key: str, api_base: str, model: str) -> str:
    """
    Call an OpenAI-compatible LLM API and return the answer.

    Args:
        question: The user's question
        api_key: API key for authentication
        api_base: Base URL for the LLM API
        model: Model name to use

    Returns:
        The LLM's answer as a string
    """
    url = f"{api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer questions concisely and accurately.",
            },
            {"role": "user", "content": question},
        ],
        "temperature": 0.7,
        "max_tokens": 500,
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

    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Request error: {e}", file=sys.stderr)
        sys.exit(1)
    except (KeyError, IndexError) as e:
        print(f"Unexpected response format: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point for the agent CLI."""
    # Check command-line arguments
    if len(sys.argv) != 2:
        print('Usage: uv run agent.py "<question>"', file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    # Load environment variables
    env_vars = load_env_vars()
    api_key = env_vars["LLM_API_KEY"]
    api_base = env_vars["LLM_API_BASE"]
    model = env_vars["LLM_MODEL"]

    print(f"Question: {question}", file=sys.stderr)
    print(f"Using model: {model}", file=sys.stderr)

    # Call the LLM (detect API type by base URL)
    if "googleapis.com" in api_base:
        answer = call_llm_gemini(question, api_key, model)
    else:
        answer = call_llm_openai(question, api_key, api_base, model)

    # Format and output the response
    result = {
        "answer": answer,
        "tool_calls": [],
    }

    # Output valid JSON to stdout
    print(json.dumps(result))

    print("Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
