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
MAX_TOOL_CALLS = 20


def load_env():
    """Load environment variables from .env.agent.secret and .env.docker.secret.

    Environment variables can also be set directly (e.g., by the autochecker).
    """
    # Get the directory where agent.py is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load from .env.agent.secret for LLM credentials
    agent_env_path = os.path.join(script_dir, ".env.agent.secret")
    if os.path.exists(agent_env_path):
        load_dotenv(agent_env_path)
    
    # Load from .env.docker.secret for LMS_API_KEY (backend authentication)
    docker_env_path = os.path.join(script_dir, ".env.docker.secret")
    if os.path.exists(docker_env_path):
        # Use override=False to not overwrite already set variables
        load_dotenv(docker_env_path, override=False)


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


def get_api_config():
    """Get backend API configuration from environment variables."""
    lms_api_key = os.getenv("LMS_API_KEY")
    api_base_url = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")

    if not lms_api_key:
        print("Error: LMS_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    return lms_api_key, api_base_url


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


def query_api(method: str, path: str, body: str = None) -> str:
    """Query the deployed backend API.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        path: API endpoint path (e.g., '/items/', '/analytics/completion-rate')
        body: Optional JSON request body for POST/PUT requests

    Returns:
        JSON string with status_code and response body, or an error message.
    """
    try:
        lms_api_key, api_base_url = get_api_config()
    except SystemExit:
        return "Error: LMS_API_KEY not configured"

    # Build full URL (strip trailing slashes to avoid double slashes)
    base_url = api_base_url.rstrip("/")
    path = path.lstrip("/")
    url = f"{base_url}/{path}"

    # Prepare headers
    headers = {
        "Authorization": f"Bearer {lms_api_key}",
        "Content-Type": "application/json",
    }

    print(f"Querying API: {method} {url}", file=sys.stderr)

    try:
        # Send HTTP request
        if method.upper() == "GET":
            response = httpx.get(url, headers=headers, timeout=30)
        elif method.upper() == "POST":
            data = json.loads(body) if body else {}
            response = httpx.post(url, headers=headers, json=data, timeout=30)
        elif method.upper() == "PUT":
            data = json.loads(body) if body else {}
            response = httpx.put(url, headers=headers, json=data, timeout=30)
        elif method.upper() == "DELETE":
            response = httpx.delete(url, headers=headers, timeout=30)
        else:
            return f"Error: Unsupported HTTP method '{method}'"

        # Build response with status_code and body
        result = {
            "status_code": response.status_code,
            "body": response.text,
        }
        return json.dumps(result)

    except httpx.TimeoutException:
        return f"Error: API request timed out to {url}"
    except httpx.ConnectError as e:
        return f"Error: Cannot connect to API at {url} - {e}"
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code} - {e.response.text}"
    except httpx.RequestError as e:
        return f"Error: Request failed - {e}"
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON in body - {e}"
    except Exception as e:
        return f"Error: Unexpected error - {e}"


def get_tool_schemas():
    """Return the tool schemas for LLM function calling."""
    return [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read contents of a file from the project repository. Use this to read documentation files (wiki/*.md) or source code to find answers about system architecture, framework, ports, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path from project root (e.g., 'wiki/git-workflow.md', 'backend/app/main.py')"
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
                "description": "List files and directories at a given path. Use this to discover what files exist in a directory (e.g., 'wiki' to find documentation files).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative directory path from project root (e.g., 'wiki', 'backend/app')"
                        }
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_api",
                "description": "Query the live backend API to get current data from the system. Use this for questions about item counts, scores, analytics, or any data that requires the current system state. Do NOT use for static facts like framework or ports.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "method": {
                            "type": "string",
                            "description": "HTTP method (GET, POST, PUT, DELETE). Use GET for retrieving data."
                        },
                        "path": {
                            "type": "string",
                            "description": "API endpoint path (e.g., '/items/', '/analytics/completion-rate', '/learners/')"
                        },
                        "body": {
                            "type": "string",
                            "description": "Optional JSON request body for POST/PUT requests (e.g., '{\"key\": \"value\"}')"
                        }
                    },
                    "required": ["method", "path"]
                }
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
    elif tool_name == "query_api":
        method = args.get("method", "GET")
        path = args.get("path", "")
        body = args.get("body")
        return query_api(method, path, body)
    else:
        return f"Error: Unknown tool '{tool_name}'"


def get_system_prompt():
    """Return the system prompt for the system agent."""
    return """You are a documentation and system assistant for a software engineering lab. You have access to tools that can read files and query the live backend API.

Available tools:
1. list_files - Discover what files exist in a directory
2. read_file - Read documentation or source code files  
3. query_api - Query the live backend API for current data

When to use each tool:

**Use list_files and read_file for:**
- Questions about documentation (git workflow, merge conflicts, lab procedures)
- Questions about system architecture (framework, ports, status codes)
- Questions about source code structure or implementation
- Static facts that don't change

**Use query_api for:**
- Questions about live data (how many items, what's the score, etc.)
- Questions that require current system state
- Analytics and statistics
- Any question asking "how many", "what is the count", "show me data"

Critical rules:
- NEVER output partial thoughts like "Let me check..." - either use a tool OR give a complete answer
- When asked to "list all X" or describe multiple things, you MUST read ALL relevant files before answering
- For router/file exploration: list the directory, then read EVERY file in that directory in subsequent tool calls
- Only return a final text answer when you have gathered ALL information and can provide a COMPLETE answer
- Your final answer should include all items/files requested, not partial lists

For source references:
- For wiki files: use format wiki/filename.md#section-anchor
- Section anchors are heading text in lowercase with hyphens instead of spaces
- Example: "## Resolving Merge Conflicts" becomes "#resolving-merge-conflicts"
- For API queries: mention the endpoint used (e.g., "GET /items/")
- For source code: use path/to/file.py:function_name

Always include the source reference at the end of your answer:
- For wiki: "Source: wiki/filename.md#section-anchor"
- For API: "Source: API endpoint GET /items/"
- For source code: "Source: backend/app/main.py"

If you cannot find the answer after thorough exploration, say so honestly and explain what you tried."""


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

        # Parse tool calls from OpenAI format
        tool_calls = message.get("tool_calls")
        parsed_tool_calls = None
        if tool_calls:
            parsed_tool_calls = []
            for tc in tool_calls:
                # OpenAI format: tool_call has 'function' with 'name' and 'arguments'
                func = tc.get("function", {})
                parsed_tool_calls.append({
                    "id": tc.get("id"),
                    "name": func.get("name"),
                    "arguments": func.get("arguments", "{}"),
                })

        result = {
            "content": message.get("content"),
            "tool_calls": parsed_tool_calls,
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
        Source reference string (e.g., 'wiki/git-workflow.md#section' or 'API: GET /items/')
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

    # Check for API source reference
    api_pattern = r"Source:\s*API\s*(?:endpoint)?\s*(GET|POST|PUT|DELETE)\s*([\w/-]+)"
    api_match = re.search(api_pattern, response_text, re.IGNORECASE)
    if api_match:
        method = api_match.group(1).upper()
        path = api_match.group(2)
        return f"API: {method} {path}"

    # Fallback: use the last file read via read_file
    for tc in reversed(tool_calls):
        if tc.get("tool") == "read_file":
            path = tc.get("args", {}).get("path", "")
            if path.startswith("wiki/"):
                return path
        elif tc.get("tool") == "query_api":
            method = tc.get("args", {}).get("method", "GET")
            path = tc.get("args", {}).get("path", "")
            return f"API: {method} {path}"

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
            # Convert our internal format to OpenAI format for the message
            openai_tool_calls = []
            for tc in response["tool_calls"]:
                openai_tool_calls.append({
                    "id": tc.get("id"),
                    "type": "function",
                    "function": {
                        "name": tc.get("name"),
                        "arguments": tc.get("arguments", "{}"),
                    },
                })

            # Add assistant message with tool calls (in OpenAI format)
            messages.append({
                "role": "assistant",
                "content": response.get("content"),
                "tool_calls": openai_tool_calls,
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
            # No tool calls - check if this is a complete answer
            answer = response.get("content") or ""
            
            # Detect incomplete answers that indicate more work is needed
            incomplete_indicators = [
                "let me check",
                "let me see",
                "let me continue",
                "let me examine",
                "i'll check",
                "i need to check",
                "i should check",
                "now let me",
                "next i'll",
                "continue checking",
            ]
            
            answer_lower = answer.lower()
            is_incomplete = any(indicator in answer_lower for indicator in incomplete_indicators)
            
            # Also check if answer ends with colon (indicating more to come)
            ends_with_colon = answer.strip().endswith(":")
            
            if is_incomplete or ends_with_colon:
                # Force more tool calls by adding a prompt to continue
                print(f"Incomplete answer detected, forcing more exploration...", file=sys.stderr)
                messages.append({
                    "role": "assistant",
                    "content": answer,
                })
                messages.append({
                    "role": "user",
                    "content": "Please continue using tools to gather more information. Only provide a final answer when you have completed the task.",
                })
                tool_call_count += 1  # Count this as an iteration
                continue
            
            # This is a complete final answer
            print(f"Final answer received", file=sys.stderr)
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
