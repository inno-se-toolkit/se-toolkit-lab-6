import os
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv

def main():
    # Load environment variables from .env.agent.secret
    load_dotenv(".env.agent.secret")
    
    api_key = os.getenv("LLM_API_KEY")
    api_base = os.getenv("LLM_API_BASE")
    model = os.getenv("LLM_MODEL", "qwen3-coder-plus")
    
    if not api_key or not api_base:
        print("Error: LLM_API_KEY or LLM_API_BASE not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
        
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py <question>", file=sys.stderr)
        sys.exit(1)
        
    question = sys.argv[1]
    
    client = OpenAI(
        api_key=api_key,
        base_url=api_base
    )
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Provide concise answers."},
                {"role": "user", "content": question}
            ]
        )
        
        answer = response.choices[0].message.content
        output = {
            "answer": answer,
            "tool_calls": []
        }
        
        # Print valid JSON to stdout
        print(json.dumps(output))
        
    except Exception as e:
        print(f"Error calling LLM: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
