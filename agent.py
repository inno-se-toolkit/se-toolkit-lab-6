#!/usr/bin/env python3
"""
Agent that calls an LLM to answer questions.
Usage: uv run agent.py "your question here"
"""

import os
import sys
import json
import dotenv
from openai import OpenAI
import argparse

# Load environment variables
dotenv.load_dotenv(".env.agent.secret")

def main():
    # Parse command line argument
    parser = argparse.ArgumentParser(description="LLM Agent")
    parser.add_argument("question", help="Question to ask the LLM")
    args = parser.parse_args()
    
    # Get API configuration from environment
    api_key = os.getenv("LLM_API_KEY")
    api_base = os.getenv("LLM_API_BASE")
    model = os.getenv("LLM_MODEL", "qwen3-coder-plus")
    
    if not api_key or not api_base:
        print("Error: LLM_API_KEY and LLM_API_BASE must be set in .env.agent.secret", 
              file=sys.stderr)
        sys.exit(1)
    
    try:
        # Initialize OpenAI-compatible client
        client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        
        # Print debug info to stderr
        print(f"Using model: {model}", file=sys.stderr)
        print(f"Question: {args.question}", file=sys.stderr)
        
        # Make API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer the user's question concisely and accurately."},
                {"role": "user", "content": args.question}
            ],
            timeout=60
        )
        
        # Extract answer
        answer = response.choices[0].message.content
        
        # Output JSON to stdout
        result = {
            "answer": answer,
            "tool_calls": []  # Empty for Task 1
        }
        print(json.dumps(result))
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()