#!/usr/bin/env python3
"""
Agent CLI with tools (read_file, list_files) and agentic loop.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
import argparse
import glob
from pathlib import Path

# Load environment variables
load_dotenv('.env.agent.secret')

# Constants
MAX_TOOL_CALLS = 10
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def debug_log(message):
    """Print debug messages to stderr."""
    print(message, file=sys.stderr)

def validate_path(path):
    """
    Validate and normalize path to prevent directory traversal.
    Returns absolute path if valid, None if invalid.
    """
    try:
        # Convert to absolute path
        requested_path = os.path.abspath(os.path.join(PROJECT_ROOT, path))
        
        # Check if path is within project root
        if not requested_path.startswith(PROJECT_ROOT):
            debug_log(f"Security: Path traversal attempt blocked: {path}")
            return None
        
        return requested_path
    except Exception as e:
        debug_log(f"Path validation error: {e}")
        return None

def read_file(path):
    """Read contents of a file."""
    valid_path = validate_path(path)
    if not valid_path:
        return f"Error: Invalid path or path traversal detected: {path}"
    
    try:
        with open(valid_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"

def list_files(path):
    """List files and directories at given path."""
    valid_path = validate_path(path)
    if not valid_path:
        return f"Error: Invalid path or path traversal detected: {path}"
    
    try:
        if not os.path.exists(valid_path):
            return f"Error: Path not found: {path}"
        
        if not os.path.isdir(valid_path):
            return f"Error: Path is not a directory: {path}"
        
        entries = os.listdir(valid_path)
        return "\n".join(sorted(entries))
    except Exception as e:
        return f"Error listing directory: {e}"

# Tool definitions for function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a file from the project repository. Use this to examine wiki files and find answers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root (e.g., 'wiki/git-workflow.md')"
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
            "description": "List files and directories at a given path. Use this first to discover what wiki files are available.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path from project root (e.g., 'wiki')"
                    }
                },
                "required": ["path"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are a documentation assistant with access to the project wiki files.
You have two tools:
- list_files: Discover what files are in a directory
- read_file: Read the contents of a file

Follow this process:
1. First, use list_files on the 'wiki' directory to see what documentation is available
2. Then use read_file on relevant files to find the answer
3. Always include the source reference (file path and section if applicable)
4. When you have the answer, respond with the answer and source

Remember to explore systematically and cite your sources."""

def call_llm(messages, tools=None):
    """Call LLM with messages and optional tools."""
    api_key = os.getenv('LLM_API_KEY')
    api_base = os.getenv('LLM_API_BASE')
    model = os.getenv('LLM_MODEL')
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7
    }
    
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    
    try:
        response = requests.post(
            f"{api_base}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        debug_log(f"LLM call failed: {e}")
        raise

def execute_tool_call(tool_call):
    """Execute a tool call and return result."""
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    
    debug_log(f"Executing {function_name} with args: {arguments}")
    
    if function_name == "read_file":
        result = read_file(arguments["path"])
    elif function_name == "list_files":
        result = list_files(arguments["path"])
    else:
        result = f"Error: Unknown tool {function_name}"
    
    return {
        "tool_call_id": tool_call.id,
        "role": "tool",
        "name": function_name,
        "content": result
    }

def agent_loop(question):
    """Main agentic loop."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    
    all_tool_calls = []
    tool_call_count = 0
    
    while tool_call_count < MAX_TOOL_CALLS:
        debug_log(f"\n--- Loop iteration {tool_call_count + 1} ---")
        
        # Call LLM with tools
        response = call_llm(messages, TOOLS)
        assistant_message = response['choices'][0]['message']
        
        # Check if there are tool calls
        if 'tool_calls' not in assistant_message or not assistant_message['tool_calls']:
            # No tool calls - this is the final answer
            answer = assistant_message.get('content', '')
            
            # Try to extract source from answer (simple heuristic)
            source = None
            if 'wiki/' in answer:
                import re
                match = re.search(r'(wiki/[^\s#]+(?:#[^\s]+)?)', answer)
                if match:
                    source = match.group(1)
            
            # Add assistant message to history
            messages.append({"role": "assistant", "content": answer})
            
            return {
                "answer": answer,
                "source": source or "",
                "tool_calls": all_tool_calls
            }
        
        # Handle tool calls
        tool_calls = assistant_message['tool_calls']
        debug_log(f"Tool calls requested: {len(tool_calls)}")
        
        # Add assistant message with tool calls to history
        messages.append(assistant_message)
        
        # Execute each tool call
        for tool_call in tool_calls:
            tool_result = execute_tool_call(tool_call)
            messages.append(tool_result)
            
            # Record for output
            all_tool_calls.append({
                "tool": tool_result["name"],
                "args": json.loads(tool_call.function.arguments),
                "result": tool_result["content"]
            })
            
            tool_call_count += 1
        
        if tool_call_count >= MAX_TOOL_CALLS:
            debug_log(f"Reached maximum tool calls ({MAX_TOOL_CALLS})")
            # Get final response
            final_response = call_llm(messages)
            answer = final_response['choices'][0]['message'].get('content', 'Maximum tool calls reached')
            return {
                "answer": answer,
                "source": "",
                "tool_calls": all_tool_calls
            }
    
    return {
        "answer": "Maximum iterations reached without final answer",
        "source": "",
        "tool_calls": all_tool_calls
    }

def main():
    parser = argparse.ArgumentParser(description='Ask a question to the documentation agent')
    parser.add_argument('question', type=str, help='The question to ask')
    args = parser.parse_args()
    
    # Validate environment
    api_key = os.getenv('LLM_API_KEY')
    api_base = os.getenv('LLM_API_BASE')
    model = os.getenv('LLM_MODEL')
    
    if not all([api_key, api_base, model]):
        debug_log("Error: Missing required environment variables")
        sys.exit(1)
    
    # Create wiki directory if it doesn't exist (for testing)
    wiki_dir = os.path.join(PROJECT_ROOT, 'wiki')
    if not os.path.exists(wiki_dir):
        os.makedirs(wiki_dir)
        # Create sample wiki file for testing
        sample_file = os.path.join(wiki_dir, 'git-workflow.md')
        if not os.path.exists(sample_file):
            with open(sample_file, 'w') as f:
                f.write("""# Git Workflow

## Resolving Merge Conflicts
To resolve a merge conflict:
1. Edit the conflicting file
2. Choose which changes to keep
3. Stage the file: git add <file>
4. Commit: git commit
""")
    
    try:
        result = agent_loop(args.question)
        print(json.dumps(result))
    except Exception as e:
        debug_log(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
