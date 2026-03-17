#!/usr/bin/env python3
"""
Agent module with query_api tool for backend API access.
"""

import os
import json
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.agent.secret')
load_dotenv('.env.docker.secret')  # For LMS_API_KEY

class Agent:
    def __init__(self):
        self.api_base = os.getenv('LLM_API_BASE', 'http://localhost:8000/v1')
        self.model = os.getenv('LLM_MODEL', 'qwen3-coder-plus')
        self.lms_api_key = os.getenv('LMS_API_KEY', '')
        self.agent_api_base = os.getenv('AGENT_API_BASE_URL', 'http://localhost:42002')
    
    def query_api(self, method: str, path: str, body: str = None) -> str:
        """
        Query the backend API with LMS_API_KEY authentication.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (e.g., '/items/', '/analytics/completion-rate')
            body: Optional JSON request body for POST/PUT requests
        
        Returns:
            JSON string with status_code and response body
        """
        if not self.lms_api_key:
            return json.dumps({
                "error": "LMS_API_KEY not set",
                "status_code": 401
            })
        
        try:
            url = f"{self.agent_api_base}{path}"
            headers = {"Authorization": f"Bearer {self.lms_api_key}"}
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                headers["Content-Type"] = "application/json"
                response = requests.post(url, headers=headers, json=json.loads(body) if body else None, timeout=10)
            else:
                return json.dumps({
                    "error": f"Method {method} not supported",
                    "status_code": 400
                })
            
            # Try to parse JSON response
            try:
                data = response.json()
            except:
                data = response.text
            
            return json.dumps({
                "status_code": response.status_code,
                "data": data
            })
            
        except requests.exceptions.ConnectionError:
            return json.dumps({
                "error": f"Cannot connect to {self.agent_api_base}",
                "status_code": 503
            })
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "status_code": 500
            })
    
    def call_llm(self, prompt):
        """Call the LLM with the given prompt."""
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def format_response(self, answer, tool_calls=None):
        """Format response as JSON."""
        return json.dumps({
            "answer": answer,
            "tool_calls": tool_calls or []
        })

def main():
    if len(sys.argv) < 2:
        print("Usage: python agent.py 'question'")
        sys.exit(1)
    
    agent = Agent()
    answer = agent.call_llm(sys.argv[1])
    print(agent.format_response(answer))

if __name__ == "__main__":
    main()
