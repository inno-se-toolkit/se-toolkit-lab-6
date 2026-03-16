#!/usr/bin/env python3
"""
Agent CLI that takes a question and returns JSON response from LLM.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv('.env.agent.secret')

def debug_log(message):
    """Print debug messages to stderr."""
    print(message, file=sys.stderr)

def main():
    # Parse command line argument
    parser = argparse.ArgumentParser(description='Ask a question to LLM')
    parser.add_argument('question', type=str, help='The question to ask')
    args = parser.parse_args()
    
    # Get configuration from environment
    api_key = os.getenv('LLM_API_KEY')
    api_base = os.getenv('LLM_API_BASE')
    model = os.getenv('LLM_MODEL')
    
    # Validate configuration
    if not all([api_key, api_base, model]):
        debug_log("Error: Missing required environment variables")
        debug_log("Please set LLM_API_KEY, LLM_API_BASE, and LLM_MODEL")
        sys.exit(1)
    
    debug_log(f"Using model: {model}")
    debug_log(f"API Base: {api_base}")
    debug_log(f"Question: {args.question}")
    
    # Prepare the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": args.question}
        ],
        "temperature": 0.7
    }
    
    try:
        # Make the API call with timeout
        response = requests.post(
            f"{api_base}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        answer = result['choices'][0]['message']['content']
        
        # Output JSON to stdout
        output = {
            "answer": answer.strip(),
            "tool_calls": []
        }
        print(json.dumps(output))
        
    except requests.exceptions.Timeout:
        debug_log("Error: LLM request timed out after 60 seconds")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        debug_log(f"Error: API request failed - {e}")
        sys.exit(1)
    except (KeyError, json.JSONDecodeError) as e:
        debug_log(f"Error: Failed to parse LLM response - {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
