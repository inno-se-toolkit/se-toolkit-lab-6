import json
import os
import sys

import httpx
from dotenv import load_dotenv


def main() -> int:
    load_dotenv(".env.agent.secret")

    api_key = os.getenv("LLM_API_KEY")
    api_base = os.getenv("LLM_API_BASE")
    model = os.getenv("LLM_MODEL")

    if not api_key or not api_base or not model:
        print("Missing LLM configuration in .env.agent.secret", file=sys.stderr)
        return 1

    if len(sys.argv) < 2:
        print('Usage: uv run agent.py "your question"', file=sys.stderr)
        return 1

    question = sys.argv[1]

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question},
        ],
    }

    try:
        response = httpx.post(
            f"{api_base}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        answer = data["choices"][0]["message"]["content"]

        result = {
            "answer": answer,
            "tool_calls": [],
        }

        print(json.dumps(result, ensure_ascii=False))
        return 0

    except Exception as e:
        print(f"Agent error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())