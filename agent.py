import sys
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(".env.agent.secret")

def main():
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py <question>", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    client = OpenAI(
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_API_BASE"),
    )

    print(f"Sending question to LLM...", file=sys.stderr)

    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Answer questions concisely."},
            {"role": "user", "content": question},
        ],
        timeout=60,
    )

    answer = response.choices[0].message.content.strip()

    result = {"answer": answer, "tool_calls": []}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
