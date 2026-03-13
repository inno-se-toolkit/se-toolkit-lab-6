#!/usr/bin/env python3
"""Agent CLI - calls an LLM with tools and returns a structured JSON answer."""

import json
import os
import re
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv


# Maximum number of tool calls per question
MAX_TOOL_CALLS = 10


def load_env():
    """Load environment variables from .env.agent.secret if it exists.

    Environment variables can also be set directly (e.g., by the autochecker).
    """
    # Get the directory where agent.py is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, ".env.agent.secret")

    # Load from file if it exists, otherwise rely on system environment
    if os.path.exists(env_path):
        load_dotenv(env_path)


def get_llm_config():
    """Get LLM configuration from environment variables."""
    api_key = os.getenv("LLM_API_KEY")
    api_base = os.getenv("LLM_API_BASE")
    model = os.getenv("LLM_MODEL")

    if not api_key:
        print("Error: LLM_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    if not api_base:
        print("Error: LLM_API_BASE not set", file=sys.stderr)
        sys.exit(1)
    if not model:
        print("Error: LLM_MODEL not set", file=sys.stderr)
        sys.exit(1)

    return api_key, api_base, model


def get_project_root():
    """Get the project root directory (where agent.py is located)."""
    return os.path.dirname(os.path.abspath(__file__))


def is_safe_path(path: str) -> bool:
    """Check if a path is safe (no traversal outside project root)."""
    # Reject paths with traversal
    if ".." in path:
        return False
    # Reject absolute paths
    if os.path.isabs(path):
        return False
    # Reject paths starting with /
    if path.startswith("/"):
        return False

    # Resolve and verify within project root
    project_root = get_project_root()
    resolved = os.path.normpath(os.path.join(project_root, path))
    return resolved.startswith(project_root)


def read_file(path: str) -> str:
    """Read contents of a file from the project repository.

    Args:
        path: Relative path from project root (e.g., 'wiki/git-workflow.md')

    Returns:
        File contents as a string, or an error message if the file doesn't exist.
    """
    # Security check
    if not is_safe_path(path):
        return f"Error: Invalid path '{path}' - path traversal not allowed"

    project_root = get_project_root()
    full_path = os.path.normpath(os.path.join(project_root, path))

    # Check if file exists
    if not os.path.isfile(full_path):
        return f"Error: File not found: {path}"

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


def list_files(path: str) -> str:
    """List files and directories at a given path.

    Args:
        path: Relative directory path from project root (e.g., 'wiki')

    Returns:
        Newline-separated listing of entries, or an error message.
    """
    # Security check
    if not is_safe_path(path):
        return f"Error: Invalid path '{path}' - path traversal not allowed"

    project_root = get_project_root()
    full_path = os.path.normpath(os.path.join(project_root, path))

    # Check if directory exists
    if not os.path.isdir(full_path):
        return f"Error: Directory not found: {path}"

    try:
        entries = os.listdir(full_path)
        # Sort entries: directories first, then files
        dirs = sorted([e for e in entries if os.path.isdir(os.path.join(full_path, e))])
        files = sorted([e for e in entries if os.path.isfile(os.path.join(full_path, e))])
        result = "\n".join(dirs + files)
        return result
    except Exception as e:
        return f"Error listing directory: {e}"


def get_tool_schemas():
    """Return the tool schemas for LLM function calling."""
    return [
        {
            "name": "read_file",
            "description": "Read contents of a file from the project repository. Use this to read documentation files to find answers.",
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
        },
        {
            "name": "list_files",
            "description": "List files and directories at a given path. Use this to discover what files exist in a directory.",
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
    ]


def execute_tool(tool_name: str, args: dict) -> str:
    """Execute a tool and return its result.

    Args:
        tool_name: Name of the tool to execute
        args: Arguments for the tool

    Returns:
        Tool result as a string
    """
    if tool_name == "read_file":
        path = args.get("path", "")
        return read_file(path)
    elif tool_name == "list_files":
        path = args.get("path", "")
        return list_files(path)
    else:
        return f"Error: Unknown tool '{tool_name}'"


def get_system_prompt():
    """Return the system prompt for the documentation agent."""
    return """You are a documentation assistant for a software engineering lab. You have access to tools that can read files from the project repository.

When answering questions:
1. First use list_files to explore relevant directories (like 'wiki')
2. Then use read_file to read specific files that might contain the answer
3. Look for section headings in the files to identify the exact source
4. Provide a clear answer and cite the source

For the source reference:
- Use the format: wiki/filename.md#section-anchor
- The section anchor is the heading text converted to lowercase with spaces replaced by hyphens
- For example, "## Resolving Merge Conflicts" becomes "#resolving-merge-conflicts"

Always include the source reference at the end of your answer in this format:
Source: wiki/filename.md#section-anchor

If you cannot find the answer in the files, say so honestly."""


def call_llm(messages: list, api_key: str, api_base: str, model: str, tools: list = None, timeout: int = 120) -> dict:
    """Call the LLM API and return the full response.

    Args:
        messages: List of message dicts for the conversation
        api_key: API key for authentication
        api_base: Base URL for the API
        model: Model name to use
        tools: Optional list of tool schemas for function calling
        timeout: Request timeout in seconds

    Returns:
        Parsed response dict with 'content' and 'tool_calls' keys
    """
    url = f"{api_base}/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
    }

    if tools:
        payload["tools"] = tools

    print(f"Calling LLM at {url}...", file=sys.stderr)

    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()

        data = response.json()
        message = data["choices"][0]["message"]

        result = {
            "content": message.get("content"),
            "tool_calls": message.get("tool_calls"),
        }

        return result

    except httpx.TimeoutException:
        print(f"Error: LLM request timed out after {timeout} seconds", file=sys.stderr)
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        print(f"Error: HTTP {e.response.status_code}", file=sys.stderr)
        print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Error: Request failed - {e}", file=sys.stderr)
        sys.exit(1)
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error: Invalid response from LLM - {e}", file=sys.stderr)
        print(f"Response: {response.text}", file=sys.stderr)
        sys.exit(1)


def extract_source_from_response(response_text: str, tool_calls: list) -> str:
    """Extract the source reference from the LLM response.

    Args:
        response_text: The text response from the LLM
        tool_calls: List of tool calls made during the conversation

    Returns:
        Source reference string (e.g., 'wiki/git-workflow.md#section')
    """
    # Try to find explicit source reference in the response
    # Pattern: Source: wiki/filename.md#anchor or wiki/filename.md#anchor
    patterns = [
        r"Source:\s*(wiki/[\w-]+\.md#[\w-]+)",
        r"(wiki/[\w-]+\.md#[\w-]+)",
        r"Source:\s*(wiki/[\w-]+\.md)",
        r"(wiki/[\w-]+\.md)",
    ]

    for pattern in patterns:
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            return match.group(1)

    # Fallback: use the last file read via read_file
    for tc in reversed(tool_calls):
        if tc.get("tool") == "read_file":
            path = tc.get("args", {}).get("path", "")
            if path.startswith("wiki/"):
                return path

    return "wiki/unknown.md"


def run_agentic_loop(question: str, api_key: str, api_base: str, model: str) -> dict:
    """Run the agentic loop to answer a question.

    Args:
        question: The user's question
        api_key: API key for authentication
        api_base: Base URL for the API
        model: Model name to use

    Returns:
        Dict with 'answer', 'source', and 'tool_calls' keys
    """
    tools = get_tool_schemas()
    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": question},
    ]

    all_tool_calls = []
    tool_call_count = 0

    while tool_call_count < MAX_TOOL_CALLS:
        print(f"\n--- Iteration {tool_call_count + 1} ---", file=sys.stderr)

        # Call LLM
        response = call_llm(messages, api_key, api_base, model, tools)

        # Check for tool calls
        if response.get("tool_calls"):
            # Add assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": response.get("content"),
                "tool_calls": response["tool_calls"],
            })

            # Execute each tool call
            for tool_call in response["tool_calls"]:
                tool_name = tool_call.get("name")
                # Handle both 'arguments' (string JSON) and 'args' (dict) formats
                args_raw = tool_call.get("arguments", "{}")
                if isinstance(args_raw, str):
                    try:
                        args = json.loads(args_raw)
                    except json.JSONDecodeError:
                        args = {}
                else:
                    args = args_raw

                tool_call_id = tool_call.get("id", f"call_{tool_call_count}")

                print(f"Executing tool: {tool_name} with args: {args}", file=sys.stderr)

                # Execute the tool
                result = execute_tool(tool_name, args)

                # Record the tool call for output
                all_tool_calls.append({
                    "tool": tool_name,
                    "args": args,
                    "result": result,
                })

                # Add tool result as a message
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": result,
                })

                tool_call_count += 1
                print(f"Tool result (truncated): {result[:200]}...", file=sys.stderr)
        else:
            # No tool calls - this is the final answer
            print(f"Final answer received", file=sys.stderr)
            answer = response.get("content") or ""
            source = extract_source_from_response(answer, all_tool_calls)

            return {
                "answer": answer,
                "source": source,
                "tool_calls": all_tool_calls,
            }

    # Max tool calls reached
    print(f"Maximum tool calls ({MAX_TOOL_CALLS}) reached", file=sys.stderr)

    # Try to extract an answer from the last response
    answer = response.get("content") or "Maximum tool calls reached without a final answer."
    source = extract_source_from_response(answer, all_tool_calls)

    return {
        "answer": answer,
        "source": source,
        "tool_calls": all_tool_calls,
    }


def main():
    """Main entry point."""
    # Check command-line arguments
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"<your question>\"", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    # Load configuration
    load_env()
    api_key, api_base, model = get_llm_config()

    print(f"Question: {question}", file=sys.stderr)

    # Run agentic loop
    result = run_agentic_loop(question, api_key, api_base, model)

    # Output JSON result
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
