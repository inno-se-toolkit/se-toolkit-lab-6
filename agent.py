#!/usr/bin/env python3
"""
Agent CLI - Calls an LLM with tools to answer questions about the project.

Usage:
    uv run agent.py "Your question here"

Output:
    JSON with "answer", "source", and "tool_calls" fields to stdout.
    All debug output goes to stderr.
"""

import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv


# Maximum number of tool call iterations
MAX_ITERATIONS = 10

# System prompt for the agent
SYSTEM_PROMPT = """You are a documentation assistant for a software engineering lab project.
You have access to tools that let you read files and list directories in the project wiki.

When asked a question:
1. First use `list_files` to discover relevant wiki files in the 'wiki' directory
2. Then use `read_file` to read the contents of relevant files
3. Find the answer in the file contents
4. Provide the answer with a source reference (file path + section anchor)

Always include the source reference in your final answer. The source should be in the format:
wiki/filename.md#section-anchor

Section anchors are lowercase with hyphens instead of spaces (e.g., "resolving-merge-conflicts").
"""


def load_env():
    """Load environment variables from .env.agent.secret."""
    load_dotenv(".env.agent.secret")
    
    api_key = os.getenv("LLM_API_KEY")
    api_base = os.getenv("LLM_API_BASE")
    model = os.getenv("LLM_MODEL")
    
    if not api_key:
        print("Error: LLM_API_KEY not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    if not api_base:
        print("Error: LLM_API_BASE not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    if not model:
        print("Error: LLM_MODEL not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    
    return api_key, api_base, model


def validate_path(path: str) -> Path:
    """
    Validate and resolve a relative path safely.
    
    Prevents directory traversal attacks by:
    1. Rejecting paths containing '..'
    2. Ensuring the resolved path is within the project root
    """
    # Reject paths with traversal
    if ".." in path:
        raise ValueError(f"Path traversal not allowed: {path}")
    
    # Resolve to absolute path
    project_root = Path(__file__).parent.resolve()
    full_path = (project_root / path).resolve()
    
    # Ensure path is within project root
    if not str(full_path).startswith(str(project_root)):
        raise ValueError(f"Path outside project: {path}")
    
    return full_path


def read_file(path: str) -> str:
    """
    Read the contents of a file from the project repository.
    
    Args:
        path: Relative path from project root (e.g., 'wiki/git.md')
    
    Returns:
        File contents as string, or error message if file doesn't exist
    """
    try:
        full_path = validate_path(path)
        
        if not full_path.is_file():
            return f"Error: File not found: {path}"
        
        return full_path.read_text()
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error reading file: {e}"


def list_files(path: str) -> str:
    """
    List files and directories in a directory.
    
    Args:
        path: Relative directory path from project root (e.g., 'wiki')
    
    Returns:
        Newline-separated list of entries, or error message
    """
    try:
        full_path = validate_path(path)
        
        if not full_path.is_dir():
            return f"Error: Directory not found: {path}"
        
        entries = [entry.name for entry in full_path.iterdir()]
        return "\n".join(sorted(entries))
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error listing directory: {e}"


# Tool definitions for the LLM (using OpenAI-compatible format)
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file from the project repository. Use this to find information in wiki files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root (e.g., 'wiki/git.md')"
                    }
                },
                "required": ["path"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories in a directory. Use this to discover what files exist in a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path from project root (e.g., 'wiki')"
                    }
                },
                "required": ["path"],
                "additionalProperties": False
            }
        }
    }
]

# Tool choice - let the model decide when to use tools
TOOL_CHOICE = "auto"

# Map tool names to functions
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "list_files": list_files,
}


def call_llm(messages: list, api_key: str, api_base: str, model: str, tools: list = None) -> dict:
    """
    Call the LLM API with messages and optional tools.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        api_key: API key for authentication
        api_base: Base URL of the LLM API
        model: Model name to use
        tools: Optional list of tool definitions
    
    Returns:
        Parsed API response dict
    """
    url = f"{api_base}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    body = {
        "model": model,
        "messages": messages,
    }
    
    if tools:
        body["tools"] = tools
        body["tool_choice"] = TOOL_CHOICE
    
    print(f"Calling LLM at {url}...", file=sys.stderr)
    
    try:
        response = httpx.post(url, headers=headers, json=body, timeout=60.0)
        response.raise_for_status()
    except httpx.TimeoutException:
        print("Error: LLM request timed out (60s)", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Error: Failed to connect to LLM: {e}", file=sys.stderr)
        sys.exit(1)
    
    return response.json()


def execute_tool(tool_call: dict) -> str:
    """
    Execute a tool call and return the result.
    
    Args:
        tool_call: Dict with 'name' and 'arguments' keys
    
    Returns:
        Tool result as string
    """
    tool_name = tool_call["function"]["name"]
    arguments = json.loads(tool_call["function"]["arguments"])
    
    print(f"Executing tool: {tool_name} with args: {arguments}", file=sys.stderr)
    
    if tool_name not in TOOL_FUNCTIONS:
        return f"Error: Unknown tool: {tool_name}"
    
    try:
        result = TOOL_FUNCTIONS[tool_name](**arguments)
        return result
    except Exception as e:
        return f"Error executing tool: {e}"


def extract_source(answer: str, tool_calls_log: list) -> str:
    """
    Extract source reference from the answer or tool calls.
    
    Args:
        answer: The LLM's answer text
        tool_calls_log: List of tool calls made
    
    Returns:
        Source reference string (e.g., 'wiki/git.md#section')
    """
    # Try to find a wiki file reference in the answer
    import re
    
    # Look for patterns like wiki/filename.md or wiki/filename.md#anchor
    pattern = r"(wiki/[\w-]+\.md(?:#[\w-]+)?)"
    match = re.search(pattern, answer)
    
    if match:
        source = match.group(1)
        # Add anchor if not present
        if "#" not in source and tool_calls_log:
            # Try to infer section from the last read file
            last_read = None
            for tc in tool_calls_log:
                if tc["tool"] == "read_file":
                    last_read = tc["args"].get("path", "")
            if last_read:
                source = f"{source}#overview"
        return source
    
    # Fallback: use the last file read
    for tc in reversed(tool_calls_log):
        if tc["tool"] == "read_file":
            return f"{tc['args'].get('path', '')}#overview"
    
    return ""


def run_agent(question: str, api_key: str, api_base: str, model: str) -> dict:
    """
    Run the agentic loop to answer a question.
    
    Args:
        question: User's question
        api_key: LLM API key
        api_base: LLM API base URL
        model: Model name
    
    Returns:
        Dict with answer, source, and tool_calls
    """
    # Initialize messages with system prompt and user question
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    
    tool_calls_log = []
    
    for iteration in range(MAX_ITERATIONS):
        print(f"\n--- Iteration {iteration + 1}/{MAX_ITERATIONS} ---", file=sys.stderr)
        
        # Call LLM with current messages and tool definitions
        response = call_llm(messages, api_key, api_base, model, tools=TOOL_DEFINITIONS)
        
        # Get the assistant message
        assistant_message = response["choices"][0]["message"]
        
        # Check for tool calls
        tool_calls = assistant_message.get("tool_calls", [])

        if tool_calls:
            # First, add the assistant's message with tool_calls to the conversation
            messages.append(assistant_message)
            
            # Execute each tool call
            for tool_call in tool_calls:
                result = execute_tool(tool_call)

                # Log the tool call
                tool_calls_log.append({
                    "tool": tool_call["function"]["name"],
                    "args": json.loads(tool_call["function"]["arguments"]),
                    "result": result
                })

                # Append tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": result
                })

            # Continue the loop - LLM will process tool results
            continue
        else:
            # No tool calls - this is the final answer
            answer = assistant_message.get("content") or ""
            source = extract_source(answer, tool_calls_log)
            
            return {
                "answer": answer,
                "source": source,
                "tool_calls": tool_calls_log
            }
    
    # Hit max iterations
    print("\nMax iterations reached", file=sys.stderr)
    return {
        "answer": "Max iterations reached. Could not find a complete answer.",
        "source": "",
        "tool_calls": tool_calls_log
    }


def main():
    """Main entry point."""
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"Your question here\"", file=sys.stderr)
        sys.exit(1)
    
    question = sys.argv[1]
    
    # Load environment variables
    api_key, api_base, model = load_env()
    
    # Run the agent
    result = run_agent(question, api_key, api_base, model)
    
    # Output JSON to stdout
    print(json.dumps(result))


if __name__ == "__main__":
    main()
