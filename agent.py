import json
import os
import sys
import httpx


def load_env_file(path: str) -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        raise SystemExit('Usage: uv run agent.py "your question"')

    load_env_file(".env.agent.secret")

    api_key = os.getenv("LLM_API_KEY", "").strip()
    base = os.getenv("LLM_API_BASE", "").strip().rstrip("/")
    model = os.getenv("LLM_MODEL", "").strip()
    if not api_key or not base or not model:
        raise SystemExit("Missing LLM_API_KEY / LLM_API_BASE / LLM_MODEL in .env.agent.secret")

    url = f"{base}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Answer briefly and clearly."},
            {"role": "user", "content": question},
        ],
        "temperature": 0.2,
    }

   

    with httpx.Client(timeout=55.0) as client:
        r = client.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        r.raise_for_status()
        data = r.json()

    answer = data["choices"][0]["message"]["content"].strip()
    print(json.dumps({"answer": answer, "tool_calls": []}, ensure_ascii=False))


if __name__ == "__main__":
    main()
