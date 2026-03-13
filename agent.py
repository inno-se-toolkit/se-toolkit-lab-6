import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv(".env.agent.secret")


def main():
    if len(sys.argv) < 2:
        print("No question provided", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    api_key = os.getenv("LLM_API_KEY")
    api_base = os.getenv("LLM_API_BASE")
    model = os.getenv("LLM_MODEL")

    headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "se-toolkit-agent"
}

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Answer the question briefly."},
            {"role": "user", "content": question},
        ],
    }

    try:
        response = requests.post(
            f"{api_base}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )

        # Если статус не 2xx, печатаем реальный ответ сервера в stderr
        if not response.ok:
            print(f"API Error {response.status_code}: {response.text}", file=sys.stderr)
            sys.exit(1)

        data = response.json()
        answer = data["choices"][0]["message"]["content"].strip()

        output = {
            "answer": answer,
            "tool_calls": []
        }

        print(json.dumps(output))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()