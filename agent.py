#!/usr/bin/env python3
"""Documentation Agent with tools for Task 2."""

import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv('.env.agent.secret')

LLM_API_KEY = os.getenv('LLM_API_KEY')
LLM_API_BASE = os.getenv('LLM_API_BASE')
LLM_MODEL = os.getenv('LLM_MODEL')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def safe_path(user_path):
    """Prevent directory traversal."""
    full_path = os.path.abspath(os.path.join(PROJECT_ROOT, user_path))
    if not full_path.startswith(PROJECT_ROOT):
        return None
    return full_path

def list_files(path="."):
    full_path = safe_path(path)
    if not full_path:
        return "Error: Invalid path"
    try:
        items = os.listdir(full_path)
        return "\n".join(items)
    except Exception as e:
        return f"Error: {str(e)}"

def read_file(path):
    full_path = safe_path(path)
    if not full_path:
        return "Error: Invalid path"
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at a path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path from project root"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path from project root"}
                },
                "required": ["path"]
            }
        }
    }
]

def call_llm(messages, tools=None, tool_choice=None):
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": 0.7
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = tool_choice or "auto"
    
    response = requests.post(
        f"{LLM_API_BASE}/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}"
        },
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    return response.json()

def execute_tool(tool_name, args):
    if tool_name == "list_files":
        return list_files(**args)
    elif tool_name == "read_file":
        return read_file(**args)
    return f"Error: Unknown tool {tool_name}"

def agentic_loop(question):
    system_prompt = (
        "You are a documentation agent. You have tools to list files and read files. "
        "Use list_files to discover wiki files, then read_file to find answers. "
        "When you have the answer, provide it with the source file and section (e.g., wiki/git-workflow.md#section)."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]
    
    tool_calls_log = []
    
    for _ in range(10):  # max 10 iterations
        response = call_llm(messages, tools=TOOLS)
        choice = response['choices'][0]
        message = choice['message']
        
        if not message.get('tool_calls'):
            # Final answer
            answer = message['content']
            # Try to extract source from answer (simple heuristic)
            source = "wiki/unknown.md"
            if "wiki/" in answer:
                import re
                match = re.search(r'(wiki/[^\s#]+(?:#[^\s]+)?)', answer)
                if match:
                    source = match.group(1)
            return {
                "answer": answer,
                "source": source,
                "tool_calls": tool_calls_log
            }
        
        # Process tool calls
        for tool_call in message['tool_calls']:
            func = tool_call['function']
            name = func['name']
            args = json.loads(func['arguments'])
            result = execute_tool(name, args)
            tool_calls_log.append({
                "tool": name,
                "args": args,
                "result": result
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call['id'],
                "content": result
            })
    
    # If we hit 10 iterations, return whatever we have
    return {
        "answer": "Maximum iterations reached without final answer",
        "source": "wiki/unknown.md",
        "tool_calls": tool_calls_log
    }

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"answer": "Error: Please provide a question", "source": "", "tool_calls": []}))
        sys.exit(1)
    
    question = sys.argv[1]
    try:
        result = agentic_loop(question)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"answer": f"Error: {str(e)}", "source": "", "tool_calls": []}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()