#!/usr/bin/env python3
"""
CLI Agent that connects to an LLM and answers questions.

Usage:
    uv run agent.py "Your question here"

Output:
    JSON with 'answer' and 'tool_calls' fields to stdout.
    Debug/progress output goes to stderr.
"""

import json
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv


def load_env() -> dict[str, str]:
    """Load environment variables from .env.agent.secret."""
    env_path = Path(__file__).parent / ".env.agent.secret"
    if not env_path.exists():
        print(f"Error: {env_path} not found", file=sys.stderr)
        print(
            "Copy .env.agent.example to .env.agent.secret and fill in your credentials",
            file=sys.stderr,
        )
        sys.exit(1)
    
    load_dotenv(env_path)
    
    import os
    
    api_key = os.getenv("LLM_API_KEY")
    api_base = os.getenv("LLM_API_BASE")
    model = os.getenv("LLM_MODEL")
    
    if not api_key or api_key == "your-llm-api-key-here":
        print("Error: LLM_API_KEY not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    if not api_base or "<your-vm-ip>" in api_base:
        print("Error: LLM_API_BASE not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    if not model:
        print("Error: LLM_MODEL not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    
    return {
        "api_key": api_key,
        "api_base": api_base.rstrip("/"),
        "model": model,
    }


def call_lllm(question: str, config: dict[str, str]) -> str:
    """
    Call the LLM API and return the answer.
    
    Args:
        question: The user's question
        config: Configuration dict with api_key, api_base, model
    
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
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer questions concisely and accurately.",
            },
            {"role": "user", "content": question},
        ],
        "max_tokens": 1024,
        "temperature": 0.7,
    }
    
    print(f"Calling LLM at {url}...", file=sys.stderr)
    
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get("choices"):
            print("Error: No choices in LLM response", file=sys.stderr)
            sys.exit(1)
        
        answer = data["choices"][0]["message"]["content"]
        
        if not answer:
            print("Error: Empty response from LLM", file=sys.stderr)
            sys.exit(1)
        
        return answer


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"Your question here\"", file=sys.stderr)
        sys.exit(1)
    
    question = sys.argv[1]
    
    if not question.strip():
        print("Error: Question cannot be empty", file=sys.stderr)
        sys.exit(1)
    
    print(f"Question: {question}", file=sys.stderr)
    
    config = load_env()
    print(f"Using model: {config['model']}", file=sys.stderr)
    
    answer = call_lllm(question, config)
    
    result: dict[str, str | list[dict[str, str]]] = {
        "answer": answer,
        "tool_calls": [],
    }
    
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
