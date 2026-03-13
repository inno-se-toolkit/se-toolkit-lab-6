import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv(".env.agent.secret")



def list_files(path):
    try:
        base = os.getcwd()
        full = os.path.abspath(os.path.join(base, path))

        if not full.startswith(base):
            return "Access denied"

        return "\n".join(os.listdir(full))
    except Exception as e:
        return str(e)


def read_file(path):
    try:
        base = os.getcwd()
        full = os.path.abspath(os.path.join(base, path))

        if not full.startswith(base):
            return "Access denied"

        with open(full, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return str(e)

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

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file contents",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            },
        },
    },
]