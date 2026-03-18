import sys
import json
from openai import OpenAI

def main():

    if len(sys.argv) < 2:
        print("No input provided")
        return

    user_input = sys.argv[1]

    config = {}
    with open(".env.agent.secret", "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()

    api_key = config.get("LLM_API_KEY")
    base_url = config.get("LLM_API_BASE")
    model = config.get("LLM_MODEL")

    if not api_key or not base_url or not model:
        raise ValueError("One of API_KEY, LLM_API_BASE, or LLM_MODEL is missing in .env.agent.secret")

    client = OpenAI(api_key=api_key, base_url=base_url)

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": user_input}],
        temperature=0
    )

    answer = response.choices[0].message.content

    output = {
        "answer": answer,
        "tool_calls": []
    }

    print(json.dumps(output))

if __name__ == "__main__":
    main()