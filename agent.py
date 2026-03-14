#!/usr/bin/env python3
"""
Lab Assistant Agent - CLI for answering questions using LLM with tools.

Usage:
    uv run agent.py "Your question here"

Output:
    JSON to stdout: {"answer": "...", "source": "...", "tool_calls": [...]}
    Logs to stderr
"""

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env.agent.secret
ENV_FILE = Path(__file__).parent / ".env.agent.secret"
load_dotenv(dotenv_path=ENV_FILE)

# Configuration from environment
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_API_BASE = os.getenv("LLM_API_BASE", "")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen/qwen3-next-80b-a3b-instruct:free")

# Backend API configuration (for query_api tool in Task 3)
LMS_API_KEY = os.getenv("LMS_API_KEY", "")
AGENT_API_BASE_URL = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")

# Retry configuration
MAX_RETRIES = 3
BASE_DELAY = 1.0  # seconds
MAX_DELAY = 10.0  # seconds

# Mock mode for testing without LLM
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

# Cache for tool results (in-memory)
_tool_call_cache: dict[str, Any] = {}

# Project root for file operations
PROJECT_ROOT = Path(__file__).parent

# Maximum tool calls per question
MAX_TOOL_CALLS = 10

# Maximum content length to return to LLM (in characters)
MAX_CONTENT_LENGTH = 8000


def log(message: str) -> None:
    """Log message to stderr."""
    print(f"[agent] {message}", file=sys.stderr)


def should_retry(status_code: int | None, exception_type: str) -> bool:
    """
    Determine if a request should be retried.

    Retry on:
    - 429 (Too Many Requests)
    - 5xx server errors
    - Connection/timeout errors
    """
    if status_code is not None:
        return status_code in (429,) or (500 <= status_code < 600)
    # Retry on connection errors
    return exception_type in ("ConnectionError", "Timeout", "APIConnectionError")


def exponential_backoff(attempt: int) -> float:
    """
    Calculate delay with exponential backoff and jitter.

    Formula: min(BASE_DELAY * 2^attempt + jitter, MAX_DELAY)
    """
    import random

    delay = BASE_DELAY * (2**attempt)
    jitter = random.uniform(0, 0.1 * delay)  # 10% jitter
    return min(delay + jitter, MAX_DELAY)


def _get_cache_key(tool_name: str, args: dict[str, Any]) -> str:
    """Generate a cache key for tool results."""
    args_str = json.dumps(args, sort_keys=True)
    args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
    return f"{tool_name}:{args_hash}"


def _is_safe_path(path: str) -> bool:
    """Check if path is safe (no directory traversal)."""
    # Reject paths with ..
    if ".." in path:
        return False
    # Normalize and verify it's within project root
    try:
        full_path = (PROJECT_ROOT / path).resolve()
        return str(full_path).startswith(str(PROJECT_ROOT.resolve()))
    except (ValueError, OSError):
        return False


# =============================================================================
# Tool Implementations
# =============================================================================

def read_file(path: str) -> str:
    """
    Read a file from the project repository.

    Args:
        path: Relative path from project root (e.g., 'wiki/git-workflow.md')

    Returns:
        File contents as a string, or error message if file doesn't exist.
    """
    log(f"Tool: read_file('{path}')")

    # Security check
    if not _is_safe_path(path):
        return f"Error: Invalid path '{path}' - directory traversal not allowed"

    file_path = PROJECT_ROOT / path

    if not file_path.exists():
        return f"Error: File '{path}' does not exist"

    if not file_path.is_file():
        return f"Error: '{path}' is not a file"

    try:
        content = file_path.read_text()
        # Truncate if too large
        if len(content) > MAX_CONTENT_LENGTH:
            content = content[:MAX_CONTENT_LENGTH] + "\n... [content truncated]"
        log(f"read_file: read {len(content)} characters from '{path}'")
        return content
    except Exception as e:
        return f"Error reading file: {e}"


def list_files(path: str) -> str:
    """
    List files and directories at a given path.

    Args:
        path: Relative directory path from project root (e.g., 'wiki')

    Returns:
        Newline-separated list of entries.
    """
    log(f"Tool: list_files('{path}')")

    # Security check
    if not _is_safe_path(path):
        return f"Error: Invalid path '{path}' - directory traversal not allowed"

    dir_path = PROJECT_ROOT / path

    if not dir_path.exists():
        return f"Error: Directory '{path}' does not exist"

    if not dir_path.is_dir():
        return f"Error: '{path}' is not a directory"

    try:
        entries = sorted(dir_path.iterdir())
        result = []
        for entry in entries:
            # Skip hidden files and common ignored directories
            if entry.name.startswith(".") and entry.name not in (".env", ".envrc"):
                continue
            if entry.name in ("__pycache__", ".venv", ".direnv", "node_modules"):
                continue

            suffix = "/" if entry.is_dir() else ""
            result.append(f"{entry.name}{suffix}")

        output = "\n".join(result)
        log(f"list_files: found {len(result)} entries in '{path}'")
        return output
    except Exception as e:
        return f"Error listing directory: {e}"


def query_api(method: str, path: str, body: str | None = None) -> str:
    """
    Call the backend API.

    Args:
        method: HTTP method (GET, POST, etc.)
        path: API path (e.g., '/items/')
        body: Optional JSON request body for POST/PUT requests

    Returns:
        JSON string with status_code and body.
    """
    import httpx

    log(f"Tool: query_api('{method}' '{path}')")

    url = f"{AGENT_API_BASE_URL.rstrip('/')}{path}"

    headers = {}
    if LMS_API_KEY:
        headers["Authorization"] = f"Bearer {LMS_API_KEY}"
    headers["Content-Type"] = "application/json"

    try:
        with httpx.Client(timeout=30.0) as client:
            if method.upper() == "GET":
                response = client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = client.post(url, headers=headers, content=body or "{}")
            elif method.upper() == "PUT":
                response = client.put(url, headers=headers, content=body or "{}")
            elif method.upper() == "DELETE":
                response = client.delete(url, headers=headers)
            else:
                return json.dumps({"error": f"Unsupported method: {method}"})

        result = {
            "status_code": response.status_code,
            "body": response.text[:MAX_CONTENT_LENGTH],  # Truncate if too large
        }
        log(f"query_api: {method} {path} -> {response.status_code}")
        return json.dumps(result)
    except Exception as e:
        log(f"query_api error: {e}")
        return json.dumps({"error": str(e)})


# =============================================================================
# Tool Schemas for LLM
# =============================================================================

def get_tool_schemas() -> list[dict[str, Any]]:
    """Return the list of tool schemas for the LLM."""
    return [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the contents of a file from the project repository. Use this to read documentation, source code, or configuration files.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path from project root (e.g., 'wiki/git-workflow.md' or 'backend/app/main.py')",
                        },
                    },
                    "required": ["path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List files and directories at a given path. Use this to discover what files exist in a directory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative directory path from project root (e.g., 'wiki', 'backend', 'backend/app')",
                        },
                    },
                    "required": ["path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "query_api",
                "description": "Query the backend API to get data or test endpoints. Use this for questions about the running system, database contents, or API behavior.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "method": {
                            "type": "string",
                            "description": "HTTP method: GET, POST, PUT, DELETE",
                        },
                        "path": {
                            "type": "string",
                            "description": "API endpoint path (e.g., '/items/', '/analytics/completion-rate')",
                        },
                        "body": {
                            "type": "string",
                            "description": "Optional JSON request body for POST/PUT requests",
                        },
                    },
                    "required": ["method", "path"],
                },
            },
        },
    ]


def execute_tool(tool_name: str, args: dict[str, Any]) -> str:
    """
    Execute a tool by name with the given arguments.

    Args:
        tool_name: Name of the tool to execute
        args: Arguments for the tool

    Returns:
        Tool result as a string
    """
    # Check cache first
    cache_key = _get_cache_key(tool_name, args)
    if cache_key in _tool_call_cache:
        log(f"Cache hit for {cache_key}")
        return _tool_call_cache[cache_key]

    # Execute the tool
    if tool_name == "read_file":
        result = read_file(args.get("path", ""))
    elif tool_name == "list_files":
        result = list_files(args.get("path", ""))
    elif tool_name == "query_api":
        result = query_api(
            args.get("method", "GET"),
            args.get("path", ""),
            args.get("body"),
        )
    else:
        result = f"Error: Unknown tool '{tool_name}'"

    # Cache the result
    _tool_call_cache[cache_key] = result
    return result


# =============================================================================
# LLM Interaction
# =============================================================================

# Track mock call count per question to simulate multi-turn conversation
_mock_call_counts: dict[str, int] = {}


def mock_llm_response(messages: list[dict[str, Any]], tool_schemas: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Generate mock LLM responses for testing without API access.

    Returns format: {"content": str, "tool_calls": [{"name": str, "args": dict}, ...]}
    
    Simulates multi-turn conversation:
    - First call: return tool call
    - Second call: return final answer (no tool calls)
    """
    # Create a key from the last user message to track conversation state
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "").lower()
            break

    # Track call count for this conversation
    msg_key = user_message[:50]  # Use first 50 chars as key
    _mock_call_counts[msg_key] = _mock_call_counts.get(msg_key, 0) + 1
    call_count = _mock_call_counts[msg_key]

    # Pattern matching for common questions
    if "merge conflict" in user_message or "resolve" in user_message:
        if call_count == 1:
            # First call: use read_file tool
            return {
                "content": "",
                "tool_calls": [
                    {"name": "read_file", "args": {"path": "wiki/git-workflow.md"}},
                ],
            }
        else:
            # Second call: final answer
            return {
                "content": "To resolve a merge conflict, edit the conflicting file, choose which changes to keep, then stage and commit.",
                "tool_calls": [],
            }

    if "wiki" in user_message and ("files" in user_message or "list" in user_message):
        if call_count == 1:
            return {
                "content": "",
                "tool_calls": [
                    {"name": "list_files", "args": {"path": "wiki"}},
                ],
            }
        else:
            return {
                "content": "The wiki contains documentation files including git-workflow.md, vm.md, docker.md, and more.",
                "tool_calls": [],
            }

    if "rest" in user_message and ("stand" in user_message or "mean" in user_message):
        return {
            "content": "REST stands for Representational State Transfer. It is an architectural style for designing networked applications.",
            "tool_calls": [],
        }

    if "framework" in user_message and ("python" in user_message or "web" in user_message or "backend" in user_message):
        if call_count == 1:
            return {
                "content": "",
                "tool_calls": [
                    {"name": "read_file", "args": {"path": "backend/app/main.py"}},
                ],
            }
        else:
            return {
                "content": "The backend uses FastAPI, a modern Python web framework.",
                "tool_calls": [],
            }

    if "items" in user_message and ("database" in user_message or "count" in user_message or "many" in user_message):
        if call_count == 1:
            return {
                "content": "",
                "tool_calls": [
                    {"name": "query_api", "args": {"method": "GET", "path": "/items/"}},
                ],
            }
        else:
            return {
                "content": "There are 42 items in the database.",
                "tool_calls": [],
            }

    # Default response - no tool calls
    return {
        "content": "I'll help you with that question.",
        "tool_calls": [],
    }


def call_llm_with_retry(
    client: OpenAI | None,
    messages: list[dict[str, Any]],
    tool_schemas: list[dict[str, Any]] | None = None,
    max_retries: int = MAX_RETRIES,
) -> dict[str, Any]:
    """
    Call LLM with exponential backoff retry logic.

    Retries on 429 (rate limit) and 5xx (server errors).
    In mock mode, returns simulated responses.
    """
    # Mock mode - don't call real API
    if MOCK_MODE:
        log("Mock mode - using simulated LLM responses")
        return mock_llm_response(messages, tool_schemas or [])

    if client is None:
        raise Exception("LLM client not initialized and not in mock mode")

    last_exception: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            log(f"Calling LLM (attempt {attempt + 1}/{max_retries + 1})...")

            kwargs: dict[str, Any] = {
                "model": LLM_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1024,
                "timeout": 60,
            }

            if tool_schemas:
                kwargs["tools"] = tool_schemas
                kwargs["tool_choice"] = "auto"

            response = client.chat.completions.create(**kwargs)

            msg = response.choices[0].message
            content = msg.content or ""
            tool_calls = msg.tool_calls or []

            log(f"LLM response received: {len(content)} chars, {len(tool_calls)} tool calls")

            # Parse tool calls
            parsed_tool_calls = []
            for tc in tool_calls:
                if tc.function:
                    try:
                        args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        args = {}
                    parsed_tool_calls.append({
                        "name": tc.function.name,
                        "args": args,
                    })

            return {"content": content, "tool_calls": parsed_tool_calls}

        except Exception as e:
            last_exception = e
            exception_type = type(e).__name__

            # Extract status code if available
            status_code = getattr(e, "status_code", None)

            if attempt < max_retries and should_retry(status_code, exception_type):
                delay = exponential_backoff(attempt)
                log(f"Retryable error ({exception_type}): waiting {delay:.2f}s before retry...")
                time.sleep(delay)
            else:
                log(f"Error: {exception_type}: {e}")
                break

    raise last_exception or Exception("LLM call failed after all retries")


def create_system_prompt() -> str:
    """Create the system prompt for the agent."""
    return """You are a helpful assistant that answers questions about a software engineering project.

You have access to three tools:
1. `read_file` - Read the contents of a file from the project repository
2. `list_files` - List files and directories at a given path
3. `query_api` - Query the backend API to get data or test endpoints

When answering questions:
- Use `list_files` to discover what files exist in a directory
- Use `read_file` to read documentation, source code, or configuration files
- Use `query_api` to query the running backend system for data or to test API behavior
- Think step by step: first discover what files might contain the answer, then read them
- For wiki/documentation questions, always include a source reference (file path and section if possible)
- For system/API questions, use `query_api` to get real data from the running system
- Call tools one at a time, not all at once
- When you have enough information, provide a final answer without calling more tools

Respond in the same language as the question."""


def run_agentic_loop(
    client: OpenAI | None,
    question: str,
    tool_schemas: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Run the agentic loop: LLM → tool calls → execute → feed back → repeat.

    Args:
        client: OpenAI client (or None in mock mode)
        question: User's question
        tool_schemas: Tool schemas for the LLM

    Returns:
        Final response with answer, source, and tool_calls
    """
    # Initialize messages with system prompt
    system_prompt = create_system_prompt()
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    all_tool_calls: list[dict[str, Any]] = []
    final_answer = ""
    final_source = ""

    # Agentic loop
    for iteration in range(MAX_TOOL_CALLS + 1):
        log(f"Agentic loop iteration {iteration + 1}/{MAX_TOOL_CALLS + 1}")

        # Call LLM
        result = call_llm_with_retry(client, messages, tool_schemas)
        content = result.get("content", "")
        tool_calls = result.get("tool_calls", [])

        # If no tool calls, we have the final answer
        if not tool_calls:
            final_answer = content
            log("No tool calls - final answer received")
            break

        # Execute tool calls
        for tc in tool_calls:
            tool_name = tc.get("name", "")
            args = tc.get("args", {})

            # Execute and get result
            tool_result = execute_tool(tool_name, args)

            # Record the tool call
            all_tool_calls.append({
                "tool": tool_name,
                "args": args,
                "result": tool_result,
            })

            # Append tool result to messages
            messages.append({
                "role": "assistant",
                "content": "",
                "tool_calls": [{
                    "id": f"call_{tool_name}_{len(all_tool_calls)}",
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": json.dumps(args),
                    },
                }],
            })

            messages.append({
                "role": "tool",
                "tool_call_id": f"call_{tool_name}_{len(all_tool_calls)}",
                "content": tool_result,
            })

        log(f"Executed {len(tool_calls)} tool calls, total: {len(all_tool_calls)}")

    # Extract source from answer if present
    # The LLM may include a source reference in the content
    # For now, we'll leave it empty and let the LLM include it in the answer
    # Advanced: parse the answer to extract source

    return {
        "answer": final_answer,
        "source": final_source,
        "tool_calls": all_tool_calls,
    }


# =============================================================================
# Response Formatting
# =============================================================================

def create_agent_response(answer: str, source: str = "", tool_calls: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """
    Create the structured JSON response.

    Format: {"answer": "...", "source": "...", "tool_calls": [...]}
    """
    return {
        "answer": answer,
        "source": source,
        "tool_calls": tool_calls or [],
    }


# =============================================================================
# Main Entry Point
# =============================================================================

def main() -> int:
    """Main entry point."""
    # Mock mode - skip API key validation
    if not MOCK_MODE:
        # Validate configuration
        if not LLM_API_KEY or LLM_API_KEY == "your-llm-api-key-here":
            log("Error: LLM_API_KEY not configured in .env.agent.secret")
            print(json.dumps({"error": "LLM API key not configured", "answer": "", "source": "", "tool_calls": []}), file=sys.stdout)
            return 1

        if not LLM_API_BASE or LLM_API_BASE == "your-api-base-here":
            log("Error: LLM_API_BASE not configured in .env.agent.secret")
            print(json.dumps({"error": "LLM API base not configured", "answer": "", "source": "", "tool_calls": []}), file=sys.stdout)
            return 1

    # Parse command line arguments
    if len(sys.argv) < 2:
        log("Error: No question provided")
        print(
            json.dumps({"error": "No question provided. Usage: agent.py \"question\"", "answer": "", "source": "", "tool_calls": []}),
            file=sys.stdout,
        )
        return 1

    question = sys.argv[1]
    log(f"Received question: {question}")

    # Initialize LLM client (None in mock mode)
    client = None
    if not MOCK_MODE:
        client = OpenAI(
            api_key=LLM_API_KEY,
            base_url=LLM_API_BASE,
        )

    # Get tool schemas
    tool_schemas = get_tool_schemas()

    try:
        # Run agentic loop
        result = run_agentic_loop(client, question, tool_schemas)

        # Create and output response
        response = create_agent_response(
            result["answer"],
            result.get("source", ""),
            result["tool_calls"],
        )
        print(json.dumps(response))

        log("Response sent successfully")
        return 0

    except Exception as e:
        log(f"Fatal error: {e}")
        print(json.dumps({"error": str(e), "answer": "", "source": "", "tool_calls": []}), file=sys.stdout)
        return 1


if __name__ == "__main__":
    sys.exit(main())
