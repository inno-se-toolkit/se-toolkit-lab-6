#!/usr/bin/env python3
"""
Agent CLI - Calls an LLM with tools and returns a structured JSON answer.

Usage:
    uv run agent.py "Your question here"

Output:
    {"answer": "...", "source": "...", "tool_calls": [...]}
"""

import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Maximum number of tool calls per question
MAX_TOOL_CALLS = 10


def load_config() -> dict:
    """Load configuration from environment variables."""
    # Load LLM config from .env.agent.secret
    agent_env_path = os.path.join(os.path.dirname(__file__), ".env.agent.secret")
    load_dotenv(agent_env_path)

    # Load backend API config from .env.docker.secret
    docker_env_path = os.path.join(os.path.dirname(__file__), ".env.docker.secret")
    load_dotenv(docker_env_path)

    api_key = os.getenv("LLM_API_KEY")
    api_base = os.getenv("LLM_API_BASE")
    model = os.getenv("LLM_MODEL")
    lms_api_key = os.getenv("LMS_API_KEY")
    agent_api_base_url = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")

    if not api_key:
        print("Error: LLM_API_KEY not found in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    if not api_base:
        print("Error: LLM_API_BASE not found in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    if not model:
        print("Error: LLM_MODEL not found in .env.agent.secret", file=sys.stderr)
        sys.exit(1)

    return {
        "api_key": api_key,
        "api_base": api_base,
        "model": model,
        "lms_api_key": lms_api_key,
        "agent_api_base_url": agent_api_base_url,
    }


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.resolve()


def validate_path(path: str) -> tuple[bool, str]:
    """
    Validate that a path is safe and within the project directory.
    
    Returns:
        (is_valid, error_message)
    """
    # Check for path traversal attempts
    if ".." in path or path.startswith("/"):
        return False, "Path traversal not allowed"
    
    # Resolve the path
    project_root = get_project_root()
    try:
        full_path = (project_root / path).resolve()
    except Exception as e:
        return False, f"Invalid path: {e}"
    
    # Ensure the resolved path is within project root
    try:
        full_path.relative_to(project_root)
    except ValueError:
        return False, "Path is outside project directory"
    
    return True, ""


def tool_read_file(path: str) -> str:
    """
    Read a file from the project repository.
    
    Args:
        path: Relative path from project root.
    
    Returns:
        File contents as string, or error message.
    """
    is_valid, error = validate_path(path)
    if not is_valid:
        return f"Error: {error}"
    
    project_root = get_project_root()
    full_path = project_root / path
    
    if not full_path.exists():
        return f"Error: File not found: {path}"
    
    if not full_path.is_file():
        return f"Error: Not a file: {path}"
    
    try:
        return full_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"


def tool_list_files(path: str) -> str:
    """
    List files and directories at a given path.

    Args:
        path: Relative directory path from project root.

    Returns:
        Newline-separated listing of entries, or error message.
    """
    is_valid, error = validate_path(path)
    if not is_valid:
        return f"Error: {error}"

    project_root = get_project_root()
    full_path = project_root / path

    if not full_path.exists():
        return f"Error: Directory not found: {path}"

    if not full_path.is_dir():
        return f"Error: Not a directory: {path}"

    try:
        entries = sorted([e.name for e in full_path.iterdir()])
        return "\n".join(entries)
    except Exception as e:
        return f"Error listing directory: {e}"


def tool_query_api(method: str, path: str, body: str = None, config: dict = None, auth: bool = True) -> str:
    """
    Query the backend API.

    Args:
        method: HTTP method (GET, POST, etc.)
        path: API path (e.g., '/items/')
        body: Optional JSON request body
        config: Configuration dict with lms_api_key and agent_api_base_url
        auth: Whether to include authentication header (default: true)

    Returns:
        JSON string with status_code and body, or error message.
    """
    if config is None:
        config = {}

    lms_api_key = config.get("lms_api_key")
    agent_api_base_url = config.get("agent_api_base_url", "http://localhost:42002")

    # Build URL
    base_url = agent_api_base_url.rstrip("/")
    url = f"{base_url}{path}"

    headers = {
        "Content-Type": "application/json",
    }

    # Add authentication only if requested
    if auth and lms_api_key:
        headers["Authorization"] = f"Bearer {lms_api_key}"

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
                return f"Error: Unsupported method: {method}"

            result = {
                "status_code": response.status_code,
                "body": response.json() if response.content else None,
            }
            return json.dumps(result)

    except httpx.TimeoutException:
        return f"Error: Request timed out"
    except httpx.RequestError as e:
        return f"Error: Request failed: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


def get_tool_schemas() -> list[dict]:
    """Return the tool schemas for LLM function calling."""
    return [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a file from the project repository. Use this to read documentation files from the wiki directory.",
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
                "description": "List files and directories in a given directory path within the project.",
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
        },
        {
            "type": "function",
            "function": {
                "name": "query_api",
                "description": "Query the backend API for live data (item counts, scores, analytics) or system information. Use this when asked about current data in the system, not documentation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "method": {
                            "type": "string",
                            "description": "HTTP method (GET, POST, etc.)"
                        },
                        "path": {
                            "type": "string",
                            "description": "API path with optional query parameters (e.g., '/items/', '/analytics/completion-rate?lab=lab-01'). Include query params directly in the path string."
                        },
                        "body": {
                            "type": "string",
                            "description": "Optional JSON request body for POST/PUT requests"
                        },
                        "auth": {
                            "type": "boolean",
                            "description": "Whether to include authentication header (default: true). Set to false to test unauthenticated access."
                        }
                    },
                    "required": ["method", "path"]
                }
            }
        }
    ]


def execute_tool(tool_name: str, args: dict, config: dict = None) -> str:
    """
    Execute a tool and return the result.

    Args:
        tool_name: Name of the tool to execute.
        args: Arguments for the tool.
        config: Configuration dict (required for query_api).

    Returns:
        Tool result as string.
    """
    if tool_name == "read_file":
        path = args.get("path", "")
        return tool_read_file(path)
    elif tool_name == "list_files":
        path = args.get("path", "")
        return tool_list_files(path)
    elif tool_name == "query_api":
        method = args.get("method", "GET")
        path = args.get("path", "")
        body = args.get("body")
        use_auth = args.get("auth", True)
        return tool_query_api(method, path, body, config, use_auth)
    else:
        return f"Error: Unknown tool: {tool_name}"


def get_system_prompt() -> str:
    """Return the system prompt for the agent."""
    return """You are a documentation and system assistant with access to three tools:
- list_files: List files in a directory
- read_file: Read contents of a file
- query_api: Query the backend API for live data and API behavior (status codes, responses, errors)

IMPORTANT: You MUST use tools to find information. Do not answer from memory.

Tool selection guide:
- Use list_files to explore directory structures (e.g., wiki/, backend/app/routers/)
- Use read_file to read any file in the project (documentation, source code, configs)
- Use query_api when asked about:
  - Current data in the system (e.g., "How many items...", "What is the completion rate")
  - API behavior (e.g., "What status code...", "Query the /items endpoint", "What does the API return")
  - Live system state

When asked a documentation question:
1. First use list_files to explore the relevant directory (wiki/, backend/, etc.)
2. Then use read_file to read relevant files
3. Find the exact section that answers the question
4. Include the source as "path/to/file#section-anchor" format

When asked a data or API question:
1. Use query_api with the appropriate endpoint
2. Parse the JSON response to extract the answer (including status codes, error messages)

When asked about code structure:
1. Use list_files to explore the codebase directories
2. Use read_file to read source files
3. Summarize what you find

When asked to diagnose a bug or error:
1. First use query_api to reproduce the error and see the error message
2. Note the file path and line number from the error traceback
3. Use read_file to read the source code at that location
4. Identify the bug and explain it

Only answer based on wiki content, source code, or API responses. If you cannot find the answer, say so.
Always provide a source reference when you find an answer."""


def call_llm(messages: list[dict], config: dict, tools: list[dict] = None) -> dict:
    """
    Send messages to LLM and return the response.

    Args:
        messages: Conversation history.
        config: LLM configuration.
        tools: Optional tool schemas for function calling.

    Returns:
        LLM response data.
    """
    api_base = config["api_base"]
    api_key = config["api_key"]
    model = config["model"]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000,
    }

    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    url = api_base.rstrip("/") + "/chat/completions"

    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    return data


def extract_source_from_answer(answer: str, tool_calls: list[dict]) -> str:
    """
    Extract source reference from the answer or tool calls.

    Args:
        answer: The LLM's answer text.
        tool_calls: List of tool calls made.

    Returns:
        Source reference string.
    """
    import re

    # Pattern to match any file path (wiki/, backend/, etc.)
    pattern = r'((?:wiki|backend|tests|docs|contributing)/[\w\-/]+\.\w+(?:#[\w\-]+)?)'
    matches = re.findall(pattern, answer)

    if matches:
        return matches[0]

    # If no source found in answer, use the last read_file path
    for call in reversed(tool_calls):
        if call.get("tool") == "read_file":
            path = call.get("args", {}).get("path", "")
            if path:
                return path

    return "unknown"


def run_agentic_loop(question: str, config: dict) -> dict:
    """
    Run the agentic loop to answer a question.
    
    Args:
        question: User's question.
        config: LLM configuration.
    
    Returns:
        Result dict with answer, source, and tool_calls.
    """
    tool_calls_log = []
    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": question}
    ]
    
    tools = get_tool_schemas()
    
    for iteration in range(MAX_TOOL_CALLS):
        print(f"Iteration {iteration + 1}/{MAX_TOOL_CALLS}", file=sys.stderr)
        
        # Call LLM
        response_data = call_llm(messages, config, tools)
        message = response_data["choices"][0]["message"]
        
        # Check for tool calls
        tool_calls = message.get("tool_calls", [])
        
        if not tool_calls:
            # No tool calls - LLM provided final answer
            answer = message.get("content", "")
            source = extract_source_from_answer(answer, tool_calls_log)
            
            return {
                "answer": answer,
                "source": source,
                "tool_calls": tool_calls_log
            }
        
        # Execute tool calls
        for tool_call in tool_calls:
            func = tool_call.get("function", {})
            tool_name = func.get("name", "")
            
            # Parse arguments
            try:
                args = json.loads(func.get("arguments", "{}"))
            except json.JSONDecodeError:
                args = {}
            
            print(f"Executing tool: {tool_name} with args: {args}", file=sys.stderr)

            # Execute tool
            result = execute_tool(tool_name, args, config)
            
            # Log tool call
            tool_calls_log.append({
                "tool": tool_name,
                "args": args,
                "result": result
            })
            
            # Append tool result to messages
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.get("id", ""),
                "content": result
            })
    
    # Max iterations reached
    print("Max tool calls reached, returning partial answer", file=sys.stderr)
    
    # Try to get an answer from the LLM with the collected information
    messages.append({
        "role": "user",
        "content": "Please provide your best answer based on the information gathered so far."
    })
    
    response_data = call_llm(messages, config, tools=[])
    message = response_data["choices"][0]["message"]
    answer = message.get("content", "")
    source = extract_source_from_answer(answer, tool_calls_log)
    
    return {
        "answer": answer,
        "source": source,
        "tool_calls": tool_calls_log
    }


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"<question>\"", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]
    print(f"Question: {question}", file=sys.stderr)

    config = load_config()
    print(f"Using model: {config['model']}", file=sys.stderr)

    result = run_agentic_loop(question, config)
    print(f"Answer received", file=sys.stderr)

    print(json.dumps(result))


if __name__ == "__main__":
    main()
