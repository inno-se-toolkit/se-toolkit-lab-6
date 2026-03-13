#!/usr/bin/env python3
"""
Agent CLI - Calls an LLM and returns a structured JSON answer.

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


def load_config() -> dict:
    """Load configuration from environment variables."""
    config = {
        "api_key": os.environ.get("LLM_API_KEY"),
        "api_base": os.environ.get("LLM_API_BASE"),
        "model": os.environ.get("LLM_MODEL"),
    }

    missing = [key for key, value in config.items() if not value]
    if missing:
        print(
            f"Error: Missing required environment variables: {', '.join(missing)}",
            file=sys.stderr,
        )
        print(
            "Please set LLM_API_KEY, LLM_API_BASE, and LLM_MODEL in .env.agent.secret",
            file=sys.stderr,
        )
        sys.exit(1)

    return config


def call_lllm(question: str, config: dict) -> str:
    """
    Call the LLM API and return the raw response content.

    Args:
        question: The user's question
        config: Configuration dict with api_key, api_base, model

    Returns:
        The LLM's text response

    Raises:
        SystemExit: On HTTP errors or timeout
    """
    url = f"{config['api_base']}/chat/completions"

    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": config["model"],
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. "
                    "Respond with a valid JSON object containing exactly two fields: "
                    '"answer" (a string with your response) and "tool_calls" (an empty array). '
                    "Example: {\"answer\": \"Your response here\", \"tool_calls\": []}"
                ),
            },
            {"role": "user", "content": question},
        ],
        "temperature": 0.7,
    }

    print(f"Calling LLM at {url}...", file=sys.stderr)

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.TimeoutException:
        print("Error: LLM request timed out (60s limit)", file=sys.stderr)
        sys.exit(1)
    except httpx.HTTPError as e:
        print(f"Error: HTTP request failed: {e}", file=sys.stderr)
        if hasattr(e, "response") and e.response is not None:
            print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)

    data = response.json()

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        print(f"Error: Unexpected API response format: {e}", file=sys.stderr)
        print(f"Full response: {data}", file=sys.stderr)
        sys.exit(1)

    return content


def parse_response(content: str) -> dict:
    """
    Parse the LLM response into the required JSON format.

    Args:
        content: Raw text response from the LLM

    Returns:
        Dict with "answer" and "tool_calls" fields

    Raises:
        SystemExit: On JSON parse errors
    """
    # Try to extract JSON from the response (may contain markdown code blocks)
    text = content.strip()

    # Handle markdown code blocks
    if text.startswith("```json"):
        text = text.removeprefix("```json").removesuffix("```").strip()
    elif text.startswith("```"):
        text = text.removeprefix("```").removesuffix("```").strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse LLM response as JSON: {e}", file=sys.stderr)
        print(f"Raw response: {content}", file=sys.stderr)
        sys.exit(1)

    # Validate required fields
    if "answer" not in parsed:
        print('Error: Missing "answer" field in response', file=sys.stderr)
        sys.exit(1)

    if "tool_calls" not in parsed:
        print('Error: Missing "tool_calls" field in response', file=sys.stderr)
        sys.exit(1)

    if not isinstance(parsed["answer"], str):
        print('Error: "answer" must be a string', file=sys.stderr)
        sys.exit(1)

    if not isinstance(parsed["tool_calls"], list):
        print('Error: "tool_calls" must be an array', file=sys.stderr)
        sys.exit(1)

    return {"answer": parsed["answer"], "tool_calls": parsed["tool_calls"]}


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"<question>\"", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    # Load configuration
    config = load_config()
    print(f"Using model: {config['model']}", file=sys.stderr)

    # Call LLM
    content = call_lllm(question, config)
    print(f"LLM response received", file=sys.stderr)

    # Parse and output
    result = parse_response(content)

    # Output only valid JSON to stdout
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
