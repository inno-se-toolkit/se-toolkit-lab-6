#!/usr/bin/env python3
"""
agent.py — CLI agent that calls an LLM and returns structured JSON.
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Load env vars from .env.agent.secret
env_path = Path(__file__).parent / ".env.agent.secret"
load_dotenv(env_path)

# Initialize LLM client
client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_API_BASE"),
)

MODEL = os.getenv("LLM_MODEL", "qwen3-coder-plus")
SYSTEM_PROMPT = "You are a helpful assistant. Answer concisely."


def log_debug(msg: str):
    """Print to stderr for debugging (not part of JSON output)."""
    print(f"[DEBUG] {msg}", file=sys.stderr)


def call_llm(question: str) -> dict:
    """Call LLM and return structured response."""
    log_debug(f"Sending question to LLM: {question[:50]}...")
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        temperature=0.1,
        timeout=60,
    )
    
    answer = response.choices[0].message.content.strip()
    log_debug(f"Received answer: {answer[:100]}...")
    
    return {
        "answer": answer,
        "tool_calls": []
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"Your question here\"", file=sys.stderr)
        sys.exit(1)
    
    question = sys.argv[1]
    
    try:
        result = call_llm(question)
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(0)
    except Exception as e:
        log_debug(f"Error: {e}")
        print(json.dumps({"answer": "", "tool_calls": [], "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()