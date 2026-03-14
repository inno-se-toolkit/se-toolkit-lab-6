#!/usr/bin/env python3
"""
Agent CLI - Calls an LLM with tools and returns a structured JSON answer.

Usage:
    uv run agent.py "Your question here"

Output:
    JSON to stdout: {"answer": "...", "source": "...", "tool_calls": [...]}
    All debug output goes to stderr.
"""

import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv


# Maximum number of tool calls per question
MAX_TOOL_CALLS = 10

# Project root directory (where agent.py is located)
PROJECT_ROOT = Path(__file__).parent.resolve()


def load_config() -> dict:
    """Load LLM configuration from .env.agent.secret."""
    env_file = PROJECT_ROOT / ".env.agent.secret"
    load_dotenv(env_file)

    config = {
        "api_key": os.getenv("LLM_API_KEY"),
        "api_base": os.getenv("LLM_API_BASE"),
        "model": os.getenv("LLM_MODEL", "qwen3-coder-plus"),
    }

    if not config["api_key"]:
        print("Error: LLM_API_KEY not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    if not config["api_base"]:
        print("Error: LLM_API_BASE not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)

    return config


def validate_path(path: str) -> Path:
    """
    Validate and resolve a path to ensure it's within the project root.
    
    Args:
        path: Relative path from project root
        
    Returns:
        Resolved absolute Path
        
    Raises:
        ValueError: If path is outside project root or invalid
    """
    # Reject absolute paths
    if Path(path).is_absolute():
        raise ValueError(f"Absolute paths not allowed: {path}")
    
    # Reject path traversal
    if ".." in path:
        raise ValueError(f"Path traversal not allowed: {path}")
    
    # Resolve to absolute path
    full_path = (PROJECT_ROOT / path).resolve()
    
    # Ensure it's within project root
    try:
        full_path.relative_to(PROJECT_ROOT)
    except ValueError:
        raise ValueError(f"Path outside project root: {path}")
    
    return full_path


def read_file(path: str) -> dict:
    """
    Read a file from the project repository.
    
    Args:
        path: Relative path from project root
        
    Returns:
        Dict with 'content' or 'error' key
    """
    try:
        safe_path = validate_path(path)
        
        if not safe_path.exists():
            return {"error": f"File not found: {path}"}
        
        if not safe_path.is_file():
            return {"error": f"Not a file: {path}"}
        
        content = safe_path.read_text(encoding="utf-8")
        return {"content": content}
        
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to read file: {e}"}


def list_files(path: str) -> dict:
    """
    List files and directories at a given path.
    
    Args:
        path: Relative directory path from project root
        
    Returns:
        Dict with 'entries' (newline-separated) or 'error' key
    """
    try:
        safe_path = validate_path(path)
        
        if not safe_path.exists():
            return {"error": f"Path not found: {path}"}
        
        if not safe_path.is_dir():
            return {"error": f"Not a directory: {path}"}
        
        entries = []
        for entry in safe_path.iterdir():
            # Skip hidden files and __pycache__
            if entry.name.startswith(".") or entry.name == "__pycache__":
                continue
            suffix = "/" if entry.is_dir() else ""
            entries.append(f"{entry.relative_to(PROJECT_ROOT)}{suffix}")
        
        return {"entries": "\n".join(sorted(entries))}
        
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to list directory: {e}"}


# Tool definitions for LLM function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file from the project repository. Use this to read wiki documentation or source code files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root (e.g., 'wiki/git-workflow.md' or 'agent.py')",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at a given path in the project repository. Use this to discover what files exist in a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path from project root (e.g., 'wiki' or 'backend/app')",
                    }
                },
                "required": ["path"],
            },
        },
    },
]

# System prompt for the documentation agent
SYSTEM_PROMPT = """You are a documentation assistant that helps users find information in the project wiki and codebase.

You have access to two tools:
1. `list_files` - List files in a directory
2. `read_file` - Read the contents of a file

When answering questions:
1. First use `list_files` to discover relevant wiki files
2. Then use `read_file` to read the specific files that contain the answer
3. Find the exact section that answers the question
4. Provide a clear answer with a source reference

For the source reference, use the format: `path/to/file.md#section-anchor`
The section anchor should be the heading that contains the answer (lowercase, hyphens instead of spaces).

Always be specific about which file and section contains the answer.
If you can't find the answer after exploring relevant files, say so honestly.

Limit your tool calls to what's necessary - don't read every file if you can find the answer more directly.
"""


def execute_tool(name: str, args: dict) -> dict:
    """
    Execute a tool and return the result.
    
    Args:
        name: Tool name ('read_file' or 'list_files')
        args: Tool arguments
        
    Returns:
        Tool result dict
    """
    if name == "read_file":
        return read_file(args.get("path", ""))
    elif name == "list_files":
        return list_files(args.get("path", ""))
    else:
        return {"error": f"Unknown tool: {name}"}


def call_llm(messages: list, config: dict) -> dict:
    """
    Call the LLM API and return the response.
    
    Args:
        messages: List of message dicts for the conversation
        config: LLM configuration
        
    Returns:
        LLM response data dict
    """
    url = f"{config['api_base']}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}",
    }
    payload = {
        "model": config["model"],
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto",
    }

    print(f"Calling LLM at {url}...", file=sys.stderr)

    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    print(f"Got response from LLM", file=sys.stderr)
    return data


def extract_source_from_messages(messages: list) -> str:
    """
    Extract source reference from conversation messages.
    
    Looks for file paths mentioned in tool calls or content.
    
    Args:
        messages: List of conversation messages
        
    Returns:
        Source reference string (e.g., 'wiki/git-workflow.md#section')
    """
    # Look for the last read_file tool call to get the source
    for msg in reversed(messages):
        if msg.get("role") == "assistant" and "tool_calls" in msg:
            for tc in msg.get("tool_calls", []):
                if tc.get("function", {}).get("name") == "read_file":
                    path = tc.get("function", {}).get("arguments", {})
                    if isinstance(path, str):
                        try:
                            path = json.loads(path)
                        except json.JSONDecodeError:
                            pass
                    if isinstance(path, dict) and "path" in path:
                        return path["path"]
    
    return ""


def run_agentic_loop(question: str, config: dict) -> dict:
    """
    Run the agentic loop to answer a question using tools.
    
    Args:
        question: User's question
        config: LLM configuration
        
    Returns:
        Result dict with answer, source, and tool_calls
    """
    # Initialize conversation with system prompt and user question
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    
    all_tool_calls = []
    tool_call_count = 0
    
    print(f"Starting agentic loop for question: {question}", file=sys.stderr)
    
    while tool_call_count < MAX_TOOL_CALLS:
        # Call LLM
        response_data = call_llm(messages, config)
        
        # Get the assistant message
        assistant_message = response_data["choices"][0]["message"]
        
        # Check for tool calls
        tool_calls = assistant_message.get("tool_calls", [])
        
        if not tool_calls:
            # No tool calls - this is the final answer
            print(f"Final answer received", file=sys.stderr)
            answer = assistant_message.get("content", "")
            
            # Extract source from the conversation
            source = extract_source_from_messages(messages)
            
            return {
                "answer": answer,
                "source": source,
                "tool_calls": all_tool_calls,
            }
        
        # Execute tool calls
        for tool_call in tool_calls:
            tool_call_count += 1
            
            if tool_call_count > MAX_TOOL_CALLS:
                print(f"Reached max tool calls ({MAX_TOOL_CALLS})", file=sys.stderr)
                break
            
            function = tool_call.get("function", {})
            tool_name = function.get("name", "unknown")
            tool_args_str = function.get("arguments", "{}")
            
            # Parse arguments
            try:
                tool_args = json.loads(tool_args_str) if isinstance(tool_args_str, str) else tool_args_str
            except json.JSONDecodeError:
                tool_args = {}
            
            print(f"Executing tool: {tool_name} with args: {tool_args}", file=sys.stderr)
            
            # Execute the tool
            tool_result = execute_tool(tool_name, tool_args)
            
            # Record the tool call
            all_tool_calls.append({
                "tool": tool_name,
                "args": tool_args,
                "result": tool_result,
            })
            
            # Add assistant message with tool call to conversation
            messages.append(assistant_message.copy())
            
            # Add tool result as a new message
            tool_call_id = tool_call.get("id", f"call_{tool_call_count}")
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps(tool_result),
            })
            
            print(f"Tool result: {tool_result}", file=sys.stderr)
    
    # Reached max tool calls - provide whatever answer we have
    print(f"Reached max tool calls ({MAX_TOOL_CALLS}), returning partial answer", file=sys.stderr)
    
    # Try to extract an answer from the last tool result or conversation
    if all_tool_calls:
        last_result = all_tool_calls[-1].get("result", {})
        answer = last_result.get("content", last_result.get("entries", str(last_result)))
        source = extract_source_from_messages(messages)
    else:
        answer = "Unable to find answer within tool call limit."
        source = ""
    
    return {
        "answer": answer,
        "source": source,
        "tool_calls": all_tool_calls,
    }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"<question>\"", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]
    print(f"Question: {question}", file=sys.stderr)

    # Load configuration
    config = load_config()
    print(f"Using model: {config['model']}", file=sys.stderr)

    # Run agentic loop
    result = run_agentic_loop(question, config)

    # Output structured JSON
    print(json.dumps(result))


if __name__ == "__main__":
    main()
