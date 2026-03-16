#!/usr/bin/env python3
"""System agent that answers questions by reading files and querying the backend API.

This agent uses an agentic loop with three tools (read_file, list_files, query_api)
to discover information and provide answers with source references.
"""
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
MAX_TOOL_CALLS = 10

SYSTEM_PROMPT = """You are a system agent that answers questions by reading project files and querying the backend API.

You have access to three tools:
1. list_files - List files and directories in a given path
2. read_file - Read the contents of a file
3. query_api - Call the deployed backend API to get real-time data

Tool selection guide:
- Use list_files to discover project structure
- Use read_file for: wiki questions, source code analysis, configuration files, documentation
- Use query_api for: live data queries, testing endpoints, status codes, item counts, analytics

When using query_api:
- GET /items/ to list all items
- GET /items/{id} to get a specific item
- GET /analytics/completion-rate?lab=lab-XX for analytics
- GET /analytics/top-learners?lab=lab-XX for top learners
- The API key is automatically included

To answer questions:
1. Use list_files to discover relevant files (start with "wiki" or "backend" directories)
2. Use read_file to read file contents
3. Use query_api for live data or endpoint testing
4. Find the specific section that answers the question
5. Include the source as: wiki/filename.md#section-anchor or backend/path/file.py

Always provide accurate source references based on what you read.
When you have enough information, provide your final answer without calling more tools.
"""

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file from the project",
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
            "description": "List files and directories in a directory",
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
            "description": "Call the deployed backend API to get real-time data or test endpoints",
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "description": "HTTP method (GET, POST, PUT, DELETE)",
                        "enum": ["GET", "POST", "PUT", "DELETE"]
                    },
                    "path": {
                        "type": "string",
                        "description": "API path (e.g., /items/, /analytics/completion-rate)"
                    },
                    "body": {
                        "type": "string",
                        "description": "Optional JSON request body for POST/PUT"
                    }
                },
                "required": ["method", "path"]
            }
        }
    }
]


def load_env_file(filepath: Path) -> dict:
    """Load environment variables from a file."""
    env_vars = {}
    if not filepath.exists():
        return env_vars
    for line in filepath.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            env_vars[key] = value
    return env_vars


def get_config() -> dict:
    """Get configuration from environment variables or files.
    
    Environment variables take precedence over file values.
    This allows the autochecker to inject its own credentials.
    """
    # Load from files
    agent_env = load_env_file(PROJECT_ROOT / ".env.agent.secret")
    docker_env = load_env_file(PROJECT_ROOT / ".env.docker.secret")
    
    # Merge config, with environment variables taking precedence
    config = {
        "LLM_API_KEY": os.environ.get("LLM_API_KEY", agent_env.get("LLM_API_KEY", "")),
        "LLM_API_BASE": os.environ.get("LLM_API_BASE", agent_env.get("LLM_API_BASE", "")),
        "LLM_MODEL": os.environ.get("LLM_MODEL", agent_env.get("LLM_MODEL", "qwen3-coder-plus")),
        "LMS_API_KEY": os.environ.get("LMS_API_KEY", docker_env.get("LMS_API_KEY", "")),
        "AGENT_API_BASE_URL": os.environ.get("AGENT_API_BASE_URL", docker_env.get("AGENT_API_BASE_URL", "http://localhost:42002")),
    }
    
    return config


def safe_path(relative_path: str) -> Path:
    """Validate and resolve a relative path within the project root."""
    if not relative_path:
        raise ValueError("Path cannot be empty")

    if relative_path.startswith('/'):
        raise ValueError("Absolute paths not allowed")

    if '..' in relative_path:
        raise ValueError("Parent directory traversal not allowed")

    full_path = (PROJECT_ROOT / relative_path).resolve()

    try:
        full_path.relative_to(PROJECT_ROOT)
    except ValueError:
        raise ValueError(f"Path outside project root: {relative_path}")

    return full_path


def tool_read_file(path: str) -> str:
    """Read the contents of a file."""
    try:
        safe = safe_path(path)
        if not safe.exists():
            return f"Error: File not found: {path}"
        if not safe.is_file():
            return f"Error: Not a file: {path}"
        return safe.read_text()
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error reading file: {e}"


def tool_list_files(path: str) -> str:
    """List files and directories in a directory."""
    try:
        safe = safe_path(path)
        if not safe.exists():
            return f"Error: Directory not found: {path}"
        if not safe.is_dir():
            return f"Error: Not a directory: {path}"

        entries = sorted([e.name for e in safe.iterdir()])
        return "\n".join(entries)
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error listing directory: {e}"


def tool_query_api(method: str, path: str, body: str = None) -> str:
    """Call the deployed backend API using urllib."""
    config = get_config()
    api_key = config.get("LMS_API_KEY", "")
    base_url = config.get("AGENT_API_BASE_URL", "http://localhost:42002")

    headers = {
        "Content-Type": "application/json",
    }

    if api_key:
        headers["X-API-Key"] = api_key

    url = f"{base_url.rstrip('/')}{path.lstrip('/')}"

    try:
        data = None
        if body:
            try:
                data = json.loads(body).encode('utf-8')
            except json.JSONDecodeError:
                data = body.encode('utf-8') if isinstance(body, str) else body

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            response_body = response.read().decode('utf-8')
            return json.dumps({
                "status_code": response.status,
                "body": response_body
            })
            
    except urllib.error.HTTPError as e:
        return json.dumps({
            "status_code": e.code,
            "body": e.read().decode('utf-8') if e.fp else str(e)
        })
    except urllib.error.URLError as e:
        return json.dumps({"status_code": 0, "body": f"Error: {str(e.reason)}"})
    except Exception as e:
        return json.dumps({"status_code": 0, "body": f"Error: {str(e)}"})


def execute_tool(name: str, args: dict) -> str:
    """Execute a tool with the given arguments."""
    if name == "read_file":
        return tool_read_file(args.get("path", ""))
    elif name == "list_files":
        return tool_list_files(args.get("path", ""))
    elif name == "query_api":
        return tool_query_api(
            args.get("method", "GET"),
            args.get("path", ""),
            args.get("body")
        )
    else:
        return f"Error: Unknown tool: {name}"


def call_llm(messages: list, api_key: str, api_base: str, model: str,
             tools: list = None, timeout: int = 60) -> dict:
    """Call the LLM API using urllib and return the response."""
    # Normalize URL
    base = api_base.rstrip('/')
    if base.endswith('/v1'):
        base = base[:-3]
    url = f"{base}/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000,
    }

    if tools:
        payload["tools"] = tools

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            
            choices = response_data.get("choices", [])
            if not choices:
                return {"content": "", "tool_calls": []}

            message = choices[0].get("message", {})
            return {
                "content": message.get("content") or "",
                "tool_calls": message.get("tool_calls", []),
            }

    except urllib.error.HTTPError as e:
        return {"content": "", "tool_calls": []}
    except urllib.error.URLError:
        return {"content": "", "tool_calls": []}
    except Exception:
        return {"content": "", "tool_calls": []}


def run_agentic_loop(question: str, config: dict) -> dict:
    """Run the agentic loop to answer a question."""
    api_key = config.get("LLM_API_KEY", "")
    api_base = config.get("LLM_API_BASE", "")
    model = config.get("LLM_MODEL", "qwen3-coder-plus")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    tool_calls_log = []
    last_answer = None

    for iteration in range(MAX_TOOL_CALLS):
        print(f"Iteration {iteration + 1}/{MAX_TOOL_CALLS}...", file=sys.stderr)

        response = call_llm(messages, api_key, api_base, model, tools=TOOL_SCHEMAS)

        tool_calls = response.get("tool_calls", [])

        if tool_calls:
            for tc in tool_calls:
                func = tc.get("function", {})
                name = func.get("name", "unknown")
                args_str = func.get("arguments", "{}")

                try:
                    args = json.loads(args_str) if isinstance(args_str, str) else args_str
                except (json.JSONDecodeError, TypeError):
                    args = {}

                print(f"  Calling tool: {name}({args})", file=sys.stderr)
                result = execute_tool(name, args)

                tool_calls_log.append({
                    "tool": name,
                    "args": args,
                    "result": result,
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id", ""),
                    "content": result,
                })
        else:
            last_answer = response.get("content") or ""
            print(f"Final answer received", file=sys.stderr)
            break
    else:
        print("Max tool calls reached, using last available answer", file=sys.stderr)
        if last_answer is None:
            last_answer = "Unable to complete the task within the tool call limit."

    # Extract source from answer or from tool calls
    source = ""
    if last_answer:
        match = re.search(r'(wiki/[\w-]+\.md(?:#[\w-]+)?)', last_answer)
        if match:
            source = match.group(1)

    if not source and tool_calls_log:
        for tc in reversed(tool_calls_log):
            if tc["tool"] == "read_file":
                path = tc["args"].get("path", "")
                if path:
                    source = path
                break

    return {
        "answer": last_answer or "",
        "source": source,
        "tool_calls": tool_calls_log,
    }


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python agent.py \"<question>\"", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    # Get configuration (from env vars or files)
    config = get_config()

    # Run the agentic loop and always output valid JSON
    try:
        response = run_agentic_loop(question, config)
        print(json.dumps(response))
    except Exception as e:
        # Catch any unexpected errors and return valid JSON
        result = {
            "answer": f"Error: {e}",
            "source": "",
            "tool_calls": []
        }
        print(json.dumps(result))
    
    sys.exit(0)


if __name__ == "__main__":
    main()
