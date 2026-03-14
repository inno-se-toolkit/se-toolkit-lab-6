#!/usr/bin/env python3
"""
Documentation Agent with tools: read_file, list_files.
Usage: uv run agent.py "Your question about the wiki"
"""

import os
import sys
import json
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('.env.agent.secret')

LLM_API_KEY = os.getenv('LLM_API_KEY')
LLM_API_BASE = os.getenv('LLM_API_BASE', 'https://openrouter.ai/api/v1')
LLM_MODEL = os.getenv('LLM_MODEL', 'google/gemini-3-flash-preview')
MAX_TOOL_CALLS = 10
PROJECT_ROOT = Path(__file__).parent.absolute()

# -------------------- Tool implementations --------------------

def safe_path(user_path: str) -> Path:
    """Resolve a user-provided path relative to project root and prevent directory traversal."""
    requested = (PROJECT_ROOT / user_path).resolve()
    if not str(requested).startswith(str(PROJECT_ROOT)):
        raise ValueError("Path traversal attempt detected")
    return requested

def read_file(path: str) -> str:
    """Read a file from the project repository."""
    try:
        full_path = safe_path(path)
        if not full_path.is_file():
            return f"Error: File not found: {path}"
        return full_path.read_text(encoding='utf-8')
    except Exception as e:
        return f"Error reading file: {str(e)}"

def list_files(path: str) -> str:
    """List files and directories at the given path."""
    try:
        full_path = safe_path(path)
        if not full_path.is_dir():
            return f"Error: Not a directory: {path}"
        entries = list(full_path.iterdir())
        return "\n".join(sorted(e.name + ('/' if e.is_dir() else '') for e in entries))
    except Exception as e:
        return f"Error listing directory: {str(e)}"

# -------------------- Tool schemas for LLM --------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file from the project repository. Use this to get detailed information from wiki files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root, e.g., 'wiki/git-workflow.md'"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories in a given folder. Use this to discover what files are available in the wiki.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path, e.g., 'wiki'"
                    }
                },
                "required": ["path"]
            }
        }
    }
]

def call_tool(tool_name: str, args: dict) -> str:
    """Execute the requested tool and return its result."""
    if tool_name == "read_file":
        return read_file(**args)
    elif tool_name == "list_files":
        return list_files(**args)
    else:
        return f"Error: Unknown tool '{tool_name}'"

# -------------------- Agentic loop --------------------

def main():
    if len(sys.argv) < 2:
        print("Error: No question provided. Usage: agent.py \"Your question\"", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    # System prompt instructing the agent
    system_prompt = (
        "You are a helpful documentation assistant for a software project. "
        "You have access to two tools: list_files (to see what files exist) and read_file (to read file contents). "
        "Your goal is to answer questions about the project wiki. "
        "When you have enough information, provide a final answer and include the source file and section in the format 'wiki/filename.md#section'. "
        "If you cannot find the answer, say so, and note which files you examined.\n\n"
        "Always use list_files first to explore the wiki directory, then read_file on relevant files. "
        "Do not guess file contents without reading them."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    all_tool_calls = []  # stores each call with tool, args, result
    tool_call_count = 0

    # Create an HTTP client
    with httpx.Client(timeout=60.0) as client:
        while tool_call_count < MAX_TOOL_CALLS:
            payload = {
                "model": LLM_MODEL,
                "messages": messages,
                "tools": TOOLS,
                "tool_choice": "auto"
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {LLM_API_KEY}"
            }

            try:
                response = client.post(
                    f"{LLM_API_BASE}/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                print(f"Error calling LLM API: {e}", file=sys.stderr)
                sys.exit(1)

            # Extract assistant message
            assistant_msg = data['choices'][0]['message']

            # If no tool calls, we're done
            if not assistant_msg.get('tool_calls'):
                final_content = assistant_msg.get('content', '')
                break

            # Process tool calls
            for tool_call in assistant_msg['tool_calls']:
                tool_call_count += 1
                if tool_call_count > MAX_TOOL_CALLS:
                    break

                function = tool_call['function']
                tool_name = function['name']
                try:
                    args = json.loads(function['arguments'])
                except json.JSONDecodeError:
                    args = {}

                print(f"Calling tool: {tool_name} with args {args}", file=sys.stderr)
                result = call_tool(tool_name, args)

                # Record this tool call
                all_tool_calls.append({
                    "tool": tool_name,
                    "args": args,
                    "result": result
                })

                # Append tool result to messages
                messages.append({
                    "role": "assistant",
                    "tool_calls": [tool_call]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call['id'],
                    "content": result
                })

            # If we hit max tool calls, break
            if tool_call_count >= MAX_TOOL_CALLS:
                print(f"Reached maximum tool calls ({MAX_TOOL_CALLS}). Stopping.", file=sys.stderr)
                final_content = assistant_msg.get('content', 'Reached maximum tool calls without final answer.')
                break

    # Extract source from the final answer (simple heuristic: look for a wiki path)
    source = ""
    if "wiki/" in final_content:
        import re
        match = re.search(r'(wiki/[a-zA-Z0-9_\-/]+\.md(?:#[a-zA-Z0-9\-]+)?)', final_content)
        if match:
            source = match.group(1)

    # Prepare final output
    output = {
        "answer": final_content.strip(),
        "source": source,
        "tool_calls": all_tool_calls
    }
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
