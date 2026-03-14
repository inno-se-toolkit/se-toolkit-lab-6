#!/usr/bin/env python3
"""
Agent CLI — Call an LLM with tools to navigate the wiki and return structured JSON.

Usage:
    uv run agent.py "Your question here"

Output:
    JSON to stdout: {"answer": "...", "source": "...", "tool_calls": [...]}
    All debug output goes to stderr.
"""

import json
import os
import re
import sys
from pathlib import Path

import httpx
from pydantic_settings import BaseSettings


class AgentSettings(BaseSettings):
    """Settings loaded from environment variables."""

    # LLM configuration (from .env.agent.secret)
    llm_api_key: str
    llm_api_base: str
    llm_model: str

    # Backend API configuration
    # LMS_API_KEY from .env.docker.secret (or environment)
    lms_api_key: str = ""
    # AGENT_API_BASE_URL from environment (default: http://localhost:42002)
    agent_api_base_url: str = "http://localhost:42002"

    model_config = {
        "env_file": Path(__file__).parent / ".env.agent.secret",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # Ignore extra env vars not defined here
    }


def load_settings() -> AgentSettings:
    """Load and validate settings from multiple env files."""
    project_root = Path(__file__).parent

    # Load .env.agent.secret for LLM config
    env_agent_file = project_root / ".env.agent.secret"
    if not env_agent_file.exists():
        print(f"Error: {env_agent_file} not found", file=sys.stderr)
        print("Copy .env.agent.example to .env.agent.secret and fill in your credentials", file=sys.stderr)
        sys.exit(1)

    # Load .env.docker.secret for backend API config (if exists)
    env_docker_file = project_root / ".env.docker.secret"
    if env_docker_file.exists():
        # Manually parse and load .env.docker.secret
        for line in env_docker_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

    settings = AgentSettings()

    # LMS_API_KEY and AGENT_API_BASE_URL can also come from environment
    if not settings.lms_api_key:
        settings.lms_api_key = os.environ.get("LMS_API_KEY", "")
    if settings.agent_api_base_url == "http://localhost:42002":
        settings.agent_api_base_url = os.environ.get("AGENT_API_BASE_URL", "http://localhost:42002")

    print(f"Using LLM: {settings.llm_model} at {settings.llm_api_base}", file=sys.stderr)
    print(f"Backend API: {settings.agent_api_base_url}", file=sys.stderr)
    if settings.lms_api_key:
        print(f"LMS API Key: [configured]", file=sys.stderr)
    else:
        print(f"LMS API Key: [not set - query_api will fail without auth]", file=sys.stderr)

    return settings


def validate_path(relative_path: str) -> Path:
    """
    Validate that the path doesn't escape the project directory.
    
    Args:
        relative_path: Path relative to project root
        
    Returns:
        Absolute Path object
        
    Raises:
        ValueError: If path tries to escape project directory
    """
    project_root = Path(__file__).parent.resolve()
    full_path = (project_root / relative_path).resolve()
    
    # Check for path traversal
    try:
        full_path.relative_to(project_root)
    except ValueError:
        raise ValueError(f"Path traversal not allowed: {relative_path}")
    
    return full_path


def read_file(path: str) -> str:
    """
    Read contents of a file from the project repository.
    
    Args:
        path: Relative path from project root
        
    Returns:
        File contents as string, or error message
    """
    try:
        validated_path = validate_path(path)
        if not validated_path.exists():
            return f"Error: File not found: {path}"
        if not validated_path.is_file():
            return f"Error: Not a file: {path}"
        return validated_path.read_text(encoding="utf-8")
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error reading file: {e}"


def list_files(path: str) -> str:
    """
    List files and directories at a given path.

    Args:
        path: Relative directory path from project root

    Returns:
        Newline-separated listing of entries, or error message
    """
    try:
        validated_path = validate_path(path)
        if not validated_path.exists():
            return f"Error: Directory not found: {path}"
        if not validated_path.is_dir():
            return f"Error: Not a directory: {path}"

        entries = []
        for entry in sorted(validated_path.iterdir()):
            suffix = "/" if entry.is_dir() else ""
            entries.append(f"{entry.name}{suffix}")
        return "\n".join(entries)
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error listing directory: {e}"


def query_api(method: str, path: str, body: str | None = None, settings: AgentSettings | None = None) -> str:
    """
    Send an HTTP request to the backend API.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        path: API endpoint path (e.g., /items/, /analytics/completion-rate)
        body: Optional JSON request body for POST/PUT requests
        settings: Agent settings for API key and base URL

    Returns:
        JSON string with status_code and body, or error message
    """
    if settings is None:
        settings = load_settings()

    base_url = settings.agent_api_base_url.rstrip("/")
    url = f"{base_url}{path}"

    headers = {
        "Content-Type": "application/json",
    }

    # Add authentication header
    if settings.lms_api_key:
        headers["X-API-Key"] = settings.lms_api_key

    print(f"Querying API: {method} {url}", file=sys.stderr)

    try:
        with httpx.Client(timeout=30.0) as client:
            kwargs = {"headers": headers}
            if body:
                kwargs["content"] = body

            response = client.request(method, url, **kwargs)

            result = {
                "status_code": response.status_code,
                "body": response.text,
            }

            # Try to parse JSON response
            try:
                result["body"] = response.json()
            except (json.JSONDecodeError, ValueError):
                pass  # Keep as text

            return json.dumps(result)

    except httpx.HTTPError as e:
        return json.dumps({
            "status_code": getattr(e.response, "status_code", 0) if hasattr(e, "response") else 0,
            "error": str(e),
        })
    except Exception as e:
        return json.dumps({
            "status_code": 0,
            "error": f"Error querying API: {e}",
        })


# Tool definitions for LLM function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file from the project repository",
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
            "description": "List files and directories at a given path",
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
            "description": "Send an HTTP request to the backend API. Use this to query runtime data from the system, such as item counts, scores, analytics, or to check HTTP status codes. Do NOT use for wiki documentation questions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "description": "HTTP method (GET, POST, PUT, DELETE, etc.)"
                    },
                    "path": {
                        "type": "string",
                        "description": "API endpoint path (e.g., '/items/', '/analytics/completion-rate')"
                    },
                    "body": {
                        "type": "string",
                        "description": "Optional JSON request body for POST/PUT requests"
                    }
                },
                "required": ["method", "path"]
            }
        }
    }
]

# Map tool names to actual functions
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "list_files": list_files,
    "query_api": query_api,
}


SYSTEM_PROMPT = """You are a helpful documentation and code assistant. You have access to tools that let you read files, list directories, and query the backend API.

When answering questions:

1. For wiki/documentation questions (e.g., "according to the wiki", "what steps", "how to", "explain"):
   - Use `list_files` to discover what files exist in the wiki directory
   - Use `read_file` to read the contents of relevant wiki files
   - Include a source reference in your answer using the format: `wiki/filename.md#section-anchor`

2. For source code questions (e.g., "what framework", "what does this code do", "what library", "what module"):
   - Use `list_files` to explore the backend directory structure
   - Use `read_file` to read the relevant source code files (e.g., backend/app/main.py, backend/app/*.py)
   - Look for imports (e.g., "from fastapi import", "import flask"), class definitions, function names to identify patterns
   - For framework questions, check backend/app/main.py and backend/app/run.py first
   - Include a source reference in your answer using the format: `backend/app/filename.py`

3. For runtime data questions (e.g., "how many items", "what status code", "query the API", "check the database"):
   - Use `query_api` to send HTTP requests to the backend
   - Specify the correct HTTP method (usually GET for queries)
   - Specify the correct path (e.g., `/items/`, `/analytics/completion-rate`, `/analytics/pass-rates`)
   - For authentication errors, try without auth first to see the status code
   - Authentication is handled automatically when needed

4. For multi-step questions (e.g., "what error", "diagnose the bug"):
   - First use `query_api` to trigger the error and see the response
   - Then use `read_file` to read the relevant source code file mentioned in the error
   - Combine both findings in your answer

Always use tools to find the answer - don't make up information.
Be concise and accurate.
For code and framework questions, ALWAYS read the actual source files before answering.
"""


def call_llm(
    messages: list[dict],
    tools: list[dict] | None = None,
    settings: AgentSettings | None = None,
) -> dict:
    """
    Call the LLM API and return the parsed response.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        tools: Optional list of tool definitions for function calling
        settings: Agent settings
        
    Returns:
        Parsed response dict with 'content' and optionally 'tool_calls'
    """
    url = f"{settings.llm_api_base}/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "temperature": 0.7,
    }
    
    if tools:
        payload["tools"] = tools

    print(f"Calling LLM at {url}...", file=sys.stderr)

    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()

    data = response.json()
    message = data["choices"][0]["message"]
    
    result = {
        "content": message.get("content"),
        "tool_calls": message.get("tool_calls"),
    }
    
    return result


def execute_tool(tool_call: dict, settings: AgentSettings) -> str:
    """
    Execute a tool call and return the result.

    Args:
        tool_call: Dict with 'function' containing 'name' and 'arguments'
        settings: Agent settings (needed for query_api authentication)

    Returns:
        Tool result as string
    """
    function = tool_call["function"]
    name = function["name"]
    args = json.loads(function["arguments"])

    print(f"Executing tool: {name}({args})", file=sys.stderr)

    if name not in TOOL_FUNCTIONS:
        return f"Error: Unknown tool: {name}"

    try:
        # Pass settings for query_api which needs authentication
        if name == "query_api":
            result = TOOL_FUNCTIONS[name](settings=settings, **args)
        else:
            result = TOOL_FUNCTIONS[name](**args)
        return result
    except Exception as e:
        return f"Error executing tool: {e}"


def run_agentic_loop(question: str, settings: AgentSettings) -> tuple[str, str, list[dict]]:
    """
    Run the agentic loop to answer a question using tools.
    
    Args:
        question: User's question
        settings: Agent settings
        
    Returns:
        Tuple of (answer, source, tool_calls_list)
    """
    # Initialize message history
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    
    tool_calls_log = []
    max_tool_calls = 10
    
    for iteration in range(max_tool_calls):
        print(f"\n--- Iteration {iteration + 1} ---", file=sys.stderr)
        
        # Call LLM
        response = call_llm(messages, tools=TOOLS, settings=settings)
        
        # Check for tool calls
        if response["tool_calls"]:
            for tool_call in response["tool_calls"]:
                # Execute the tool
                result = execute_tool(tool_call, settings)

                # Log the tool call
                tool_call_entry = {
                    "tool": tool_call["function"]["name"],
                    "args": json.loads(tool_call["function"]["arguments"]),
                    "result": result,
                }
                tool_calls_log.append(tool_call_entry)
                
                # Append tool result to message history
                # Format tool result as a simple message for compatibility
                messages.append({
                    "role": "user",
                    "content": f"[Tool result from {tool_call['function']['name']}]: {result}",
                })
        else:
            # No tool calls - we have the final answer
            answer = response["content"]

            # Extract source from answer (look for wiki/..., backend/..., or root files pattern)
            source = ""
            # Try to find wiki source first
            source_match = re.search(r'(wiki/[\w\-/]+\.md(?:#[\w\-]+)?)', answer)
            if source_match:
                source = source_match.group(1)
            else:
                # Try to find backend source file
                source_match = re.search(r'(backend/[\w\-/]+\.py)', answer)
                if source_match:
                    source = source_match.group(1)
                else:
                    # Try to find root level files (Dockerfile, docker-compose.yml, pyproject.toml, etc.)
                    source_match = re.search(r'\b((?:Dockerfile|docker-compose\.yml|pyproject\.toml|uv\.lock)(?:\.[\w\-]+)?)\b', answer)
                    if source_match:
                        source = source_match.group(1)

            return answer, source, tool_calls_log
    
    # Hit max tool calls - return whatever we have
    print("Warning: Hit maximum tool calls limit", file=sys.stderr)
    return "I couldn't find a complete answer within the tool call limit.", "", tool_calls_log


def main() -> None:
    """Main entry point."""
    # Parse command-line arguments
    if len(sys.argv) != 2:
        print("Usage: uv run agent.py \"Your question here\"", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    # Load settings
    settings = load_settings()
    print(f"Using model: {settings.llm_model}", file=sys.stderr)

    # Run agentic loop
    answer, source, tool_calls = run_agentic_loop(question, settings)
    
    print(f"\nReceived answer from LLM", file=sys.stderr)

    # Output JSON to stdout
    result = {
        "answer": answer,
        "source": source,
        "tool_calls": tool_calls,
    }

    # Output only valid JSON to stdout
    print(json.dumps(result))


if __name__ == "__main__":
    main()
