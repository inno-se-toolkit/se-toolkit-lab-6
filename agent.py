#!/usr/bin/env python3

import json
import sys
from pathlib import Path

import httpx


def load_env() -> dict[str, str]:
    env_file = Path(__file__).parent / ".env.agent.secret"
    env_vars: dict[str, str] = {}

    if not env_file.exists():
        print(f"Error: {env_file} not found", file=sys.stderr)
        print("Copy .env.agent.example to .env.agent.secret and fill in the values", file=sys.stderr)
        sys.exit(1)

    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()

    return env_vars


def call_llm(question: str, api_key: str, api_base: str, model: str, timeout: int = 60) -> str:
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
                "content": "You are a helpful assistant. Answer questions concisely and accurately."
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "temperature": 0.7,
    }

    print(f"Calling LLM at {url} with model {model}...", file=sys.stderr)

    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    try:
        answer = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        print(f"Error parsing LLM response: {e}", file=sys.stderr)
        print(f"Response: {data}", file=sys.stderr)
        sys.exit(1)

    return answer


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"Your question here\"", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    env = load_env()

    api_key = env.get("LLM_API_KEY")
    api_base = env.get("LLM_API_BASE")
    model = env.get("LLM_MODEL")

    if not api_key:
        print("Error: LLM_API_KEY not found in .env.agent.secret", file=sys.stderr)
        sys.exit(1)

    if not api_base:
        print("Error: LLM_API_BASE not found in .env.agent.secret", file=sys.stderr)
        sys.exit(1)

    if not model:
        print("Error: LLM_MODEL not found in .env.agent.secret", file=sys.stderr)
        sys.exit(1)

    api_base = api_base.rstrip("/")

    try:
        answer = call_llm(question, api_key, api_base, model)

        output = {
            "answer": answer,
            "tool_calls": []
        }

        print(json.dumps(output, ensure_ascii=False))

    except httpx.TimeoutException:
        print("Error: LLM request timed out (60 seconds)", file=sys.stderr)
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        print(f"Error: HTTP error {e.response.status_code}", file=sys.stderr)
        print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Error: Request failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
