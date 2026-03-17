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
import urllib.parse
import socket
import ssl
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
MAX_TOOL_CALLS = 10

SYSTEM_PROMPT = """You are a system agent that answers questions by reading project files and querying the backend API.

CRITICAL RULE: You MUST use tools to gather information. Never answer from your own knowledge.
- For ANY question about this project, use tools to find the answer
- Only provide a final answer after you have used tools and gathered information

You have access to three tools:
1. list_files - List files and directories in a given path
2. read_file - Read the contents of a file
3. query_api - Call the deployed backend API to get real-time data

TOOL SELECTION RULES (follow strictly):

**Wiki/documentation questions** (e.g., "According to the wiki...", "What does the wiki say about..."):
  - Step 1: Use list_files on "wiki" to find relevant files
  - Step 2: Use read_file on the specific wiki file (e.g., "wiki/github.md", "wiki/ssh.md", "wiki/docker.md")
  - Step 3: Find the answer in the file content
  - Key wiki files:
    - wiki/github.md - branch protection, GitHub workflows
    - wiki/ssh.md - SSH connection, keys
    - wiki/docker.md - Docker commands, cleanup
    - wiki/git-workflow.md - merge conflicts, Git workflows

**Source code questions** (e.g., "What framework does the backend use?", "Read the source code"):
  - Use read_file on backend files: "backend/app/main.py" for framework, "backend/app/routers/*.py" for routers
  - Check imports at the top of main.py to identify the framework (look for "from fastapi", "import flask", etc.)
  - For Dockerfile questions: read_file on "Dockerfile"
  - For docker-compose questions: read_file on "docker-compose.yml"
  - For ETL pipeline: read_file on "backend/app/etl.py"
  - For analytics bugs: read_file on "backend/app/routers/analytics.py"
  - For "list all routers" questions:
    1. Use list_files on "backend/app/routers"
    2. Read the docstring (first 10 lines) of each .py file to understand its domain
    3. List all routers with their domains in your answer

**Live data questions** (e.g., "How many items...", "Query the API", "What status code..."):
  - Use query_api with method="GET" and the appropriate path
  - Common endpoints:
    - /items/ - list all items (use for counting items)
    - /learners/ - list all learners (use for counting learners)
    - /analytics/completion-rate?lab=lab-XX - completion rate (may have bugs)
    - /analytics/top-learners?lab=lab-XX - top learners (may have bugs)
  - For status code questions: use query_api without authentication headers to test

**Bug diagnosis questions** (e.g., "What error...", "What is the bug..."):
  - Step 1: Use query_api to trigger the error and see the error message
  - Step 2: Look at the error type (ZeroDivisionError, TypeError, etc.)
  - Step 3: Use read_file on the relevant source file to find the buggy line
  - For analytics bugs: read "backend/app/routers/analytics.py" and look for:
    - Division operations (risk of ZeroDivisionError when denominator is 0)
    - Sorting with None values (risk of TypeError)
    - Operations on potentially None values

**Reasoning questions** (e.g., "Explain the journey...", "Compare how..."):
  - Use read_file on multiple relevant files
  - For request journey: read "docker-compose.yml", "Dockerfile", "backend/app/main.py", "caddy/Caddyfile"
  - For ETL idempotency: read "backend/app/etl.py" and look for external_id checks
  - For error handling comparison: read "backend/app/etl.py" and "backend/app/routers/*.py"
  - Synthesize information from multiple files

IMPORTANT TIPS:
- Start with list_files if you're unsure which files exist
- Wiki files are in "wiki/" directory (e.g., wiki/github.md, wiki/docker.md, wiki/ssh.md)
- Backend code is in "backend/app/" directory
- When asked about branch protection, look in wiki/github.md under "Protect a branch" section
- When asked about SSH, look in wiki/ssh.md
- When asked about Docker cleanup, look in wiki/docker.md
- For framework detection, check imports in backend/app/main.py (look for "from fastapi import")
- For Dockerfile questions about layers or optimization, read the entire Dockerfile
- Always read the actual file content - don't guess
- For bug questions, FIRST query the API to see the error, THEN read the source code
- NEVER answer from your own knowledge - ALWAYS use tools first

When you have enough information to answer, provide your final answer without calling more tools.
Include source references when applicable (e.g., "wiki/github.md", "backend/app/main.py").
"""

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file from the project. Use for: wiki documentation, source code analysis, configuration files (Dockerfile, docker-compose.yml), ETL pipeline, router files. For large files, use limit_lines to read only the first N lines (e.g., docstrings).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root (e.g., 'wiki/github.md', 'backend/app/main.py', 'Dockerfile', 'docker-compose.yml', 'backend/app/etl.py', 'backend/app/routers/analytics.py')"
                    },
                    "limit_lines": {
                        "type": "integer",
                        "description": "Optional: read only first N lines (useful for large files or docstrings). Default: read entire file."
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
            "description": "List files and directories in a directory. Use to discover project structure before reading files. Common paths: 'wiki', 'backend/app', 'backend/app/routers'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path from project root (e.g., 'wiki', 'backend/app', 'backend/app/routers')"
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
            "description": "Call the deployed backend API to get real-time data, test endpoints, or check status codes. Use for: counting items/learners, checking HTTP status codes, testing analytics endpoints, triggering errors to diagnose bugs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "description": "HTTP method (GET, POST, PUT, DELETE). Use GET for reading data.",
                        "enum": ["GET", "POST", "PUT", "DELETE"]
                    },
                    "path": {
                        "type": "string",
                        "description": "API path (e.g., /items/, /learners/, /analytics/completion-rate?lab=lab-99)"
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
    
    # Debug output
    print(f"[DEBUG] Config loaded: LLM_API_KEY present: {bool(config['LLM_API_KEY'])}", file=sys.stderr)
    print(f"[DEBUG] LLM_API_BASE: {config['LLM_API_BASE']}", file=sys.stderr)
    print(f"[DEBUG] LLM_MODEL: {config['LLM_MODEL']}", file=sys.stderr)
    print(f"[DEBUG] LMS_API_KEY present: {bool(config['LMS_API_KEY'])}", file=sys.stderr)
    print(f"[DEBUG] AGENT_API_BASE_URL: {config['AGENT_API_BASE_URL']}", file=sys.stderr)
    
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


def tool_read_file(path: str, limit_lines: int = None) -> str:
    """Read the contents of a file."""
    try:
        safe = safe_path(path)
        if not safe.exists():
            return f"Error: File not found: {path}"
        if not safe.is_file():
            return f"Error: Not a file: {path}"
        
        if limit_lines:
            # Read only first N lines for large files
            with open(safe, 'r') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= limit_lines:
                        break
                    lines.append(line)
            return ''.join(lines)
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

    # Ensure path starts with /
    if not path.startswith('/'):
        path = '/' + path
    
    url = f"{base_url.rstrip('/')}{path}"
    print(f"[DEBUG] API URL: {url}", file=sys.stderr)

    try:
        data = None
        if body:
            if isinstance(body, str):
                # Try to parse as JSON first
                try:
                    # This validates it's proper JSON
                    json.loads(body)
                    data = body.encode('utf-8')
                except json.JSONDecodeError:
                    # Not JSON, send as string
                    data = body.encode('utf-8')
            else:
                data = json.dumps(body).encode('utf-8')

        req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
        
        # Create a context that doesn't verify SSL (for self-signed certs)
        context = ssl._create_unverified_context()
        
        with urllib.request.urlopen(req, context=context, timeout=10) as response:
            response_body = response.read().decode('utf-8')
            return json.dumps({
                "status_code": response.status,
                "body": response_body
            })
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else str(e)
        return json.dumps({
            "status_code": e.code,
            "body": error_body
        })
    except urllib.error.URLError as e:
        return json.dumps({"status_code": 0, "body": f"Connection error: {str(e.reason)}"})
    except socket.timeout:
        return json.dumps({"status_code": 0, "body": "Connection timeout"})
    except Exception as e:
        return json.dumps({"status_code": 0, "body": f"Error: {str(e)}"})


def execute_tool(name: str, args: dict) -> str:
    """Execute a tool with the given arguments."""
    if name == "read_file":
        return tool_read_file(
            args.get("path", ""),
            args.get("limit_lines")
        )
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
             tools: list = None, timeout: int = 30) -> dict:
    """Call the LLM API using urllib and return the response."""
    print(f"\n[DEBUG] Calling LLM with model: {model}", file=sys.stderr)
    print(f"[DEBUG] API Base: {api_base}", file=sys.stderr)

    if not api_base:
        print("[ERROR] LLM_API_BASE is missing", file=sys.stderr)
        return {"content": "Error: Missing API base URL", "tool_calls": []}

    # Handle different API base formats
    base = api_base.rstrip('/')

    # Extract host and port for connectivity check
    try:
        parsed = urllib.parse.urlparse(base)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        print(f"[DEBUG] Checking connectivity to {host}:{port}", file=sys.stderr)
        
        # Quick connectivity check with 3 second timeout
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        if result != 0:
            print(f"[ERROR] Cannot connect to {host}:{port} - {os.strerror(result)}", file=sys.stderr)
            return {"content": f"Error: Cannot connect to LLM API at {host}:{port}", "tool_calls": []}
    except Exception as e:
        print(f"[DEBUG] Connectivity check failed: {e}", file=sys.stderr)
        # Continue anyway, the actual request might work

    # For VM API, the endpoint might be different
    # Try different endpoint patterns
    urls_to_try = [
        f"{base}/chat/completions",      # Without /v1 (common for local APIs)
        f"{base}/v1/chat/completions",  # Standard OpenAI format
        f"{base}/completions",            # Legacy completions
    ]

    # Set up headers - VM API might not need auth
    headers = {
        "Content-Type": "application/json",
    }

    # Only add auth if key exists and doesn't look like a placeholder
    if api_key and api_key not in ["not-needed", "EMPTY", ""]:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000,
    }

    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
        print(f"[DEBUG] Using {len(tools)} tools", file=sys.stderr)

    data = json.dumps(payload).encode('utf-8')
    print(f"[DEBUG] Request payload size: {len(data)} bytes", file=sys.stderr)

    # Try each URL pattern with a shorter per-call timeout
    # This allows multiple attempts within the overall timeout
    per_call_timeout = min(timeout, 20)  # Max 20s per attempt
    last_error = None
    for url in urls_to_try:
        try:
            print(f"[DEBUG] Trying URL: {url}", file=sys.stderr)

            req = urllib.request.Request(url, data=data, headers=headers, method='POST')

            # Create context that doesn't verify SSL
            context = ssl._create_unverified_context()

            with urllib.request.urlopen(req, context=context, timeout=per_call_timeout) as response:
                response_data = json.loads(response.read().decode('utf-8'))

                choices = response_data.get("choices", [])
                if not choices:
                    print("[ERROR] No choices in LLM response", file=sys.stderr)
                    continue

                message = choices[0].get("message", {})
                content = message.get("content")
                if content is None:
                    content = ""

                # Handle tool_calls - might be None, empty list, or not present
                tool_calls = message.get("tool_calls")
                if tool_calls is None:
                    tool_calls = []

                print(f"[DEBUG] Got response with content length: {len(content)}", file=sys.stderr)
                print(f"[DEBUG] Tool calls: {len(tool_calls)}", file=sys.stderr)

                return {
                    "content": content,
                    "tool_calls": tool_calls,
                }

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else str(e)
            print(f"[DEBUG] HTTP {e.code} from {url}: {error_body[:200]}", file=sys.stderr)
            last_error = f"HTTP {e.code}"
            continue

        except urllib.error.URLError as e:
            print(f"[DEBUG] Cannot connect to {url}: {e.reason}", file=sys.stderr)
            last_error = f"Connection error: {e.reason}"
            continue

        except socket.timeout:
            print(f"[DEBUG] Timeout connecting to {url}", file=sys.stderr)
            last_error = "Timeout"
            continue

        except socket.error as e:
            print(f"[DEBUG] Socket error with {url}: {e}", file=sys.stderr)
            last_error = f"Socket error: {e}"
            continue

        except Exception as e:
            print(f"[DEBUG] Unexpected error with {url}: {type(e).__name__}: {e}", file=sys.stderr)
            last_error = f"{type(e).__name__}"
            continue

    # If we get here, all endpoints failed
    error_msg = f"Error: Cannot connect to LLM API - {last_error}"
    print(f"[ERROR] {error_msg}", file=sys.stderr)
    return {"content": error_msg, "tool_calls": []}

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
    has_used_tools = False
    seen_tool_calls = set()  # Prevent infinite loops from duplicate tool calls

    try:
        for iteration in range(MAX_TOOL_CALLS):
            print(f"\n=== Iteration {iteration + 1}/{MAX_TOOL_CALLS} ===", file=sys.stderr)

            # Use shorter timeout per call to stay within 180s total
            # With max 10 iterations, 15s per call = 150s max
            response = call_llm(messages, api_key, api_base, model, tools=TOOL_SCHEMAS, timeout=15)

            # Check if we got an error
            content = response.get("content", "")
            if content.startswith("Error:"):
                last_answer = content
                break

            tool_calls = response.get("tool_calls", [])

            if content:
                print(f"  LLM response: {content[:100]}...", file=sys.stderr)

            if tool_calls:
                print(f"  Tool calls requested: {len(tool_calls)}", file=sys.stderr)
                
                # Check for duplicate tool calls (prevent infinite loops)
                current_calls = tuple(sorted([
                    f"{tc.get('function', {}).get('name', tc.get('name', 'unknown'))}:"
                    f"{tc.get('function', {}).get('arguments', tc.get('arguments', '{}'))}"
                    if isinstance(tc, dict) else str(tc)
                    for tc in tool_calls
                ]))
                if current_calls in seen_tool_calls:
                    print(f"  Duplicate tool calls detected, stopping", file=sys.stderr)
                    last_answer = "Error: LLM returned duplicate tool calls"
                    break
                seen_tool_calls.add(current_calls)
                
                has_used_tools = True

                for tc in tool_calls:
                    try:
                        # Handle different tool call formats
                        if isinstance(tc, dict):
                            if "function" in tc:
                                func = tc["function"]
                            elif "name" in tc and "arguments" in tc:
                                func = {"name": tc["name"], "arguments": tc["arguments"]}
                            else:
                                func = tc
                        else:
                            func = {}

                        name = func.get("name", "unknown")
                        args_str = func.get("arguments", "{}")

                        try:
                            if isinstance(args_str, str):
                                args = json.loads(args_str)
                            else:
                                args = args_str
                        except (json.JSONDecodeError, TypeError):
                            args = {}

                        if not isinstance(args, dict):
                            args = {}

                        print(f"  -> Calling tool: {name}({json.dumps(args)[:100]})", file=sys.stderr)
                        result = execute_tool(name, args)

                        tool_calls_log.append({
                            "tool": name,
                            "args": args,
                            "result": result,
                        })

                        # Get tool call ID
                        tool_call_id = tc.get("id", f"call_{len(tool_calls_log)}")

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": result,
                        })

                        print(f"  <- Tool result: {result[:100]}...", file=sys.stderr)

                    except Exception as e:
                        print(f"  Error processing tool call: {e}", file=sys.stderr)
                        continue
            else:
                # No tool calls - only accept as final answer if we've already used tools
                if has_used_tools:
                    last_answer = content
                    print(f"  Final answer received", file=sys.stderr)
                    break
                else:
                    # No tools used yet - prompt LLM to use tools
                    print(f"  No tool calls - prompting LLM to use tools", file=sys.stderr)
                    messages.append({
                        "role": "assistant",
                        "content": content,
                    })
                    messages.append({
                        "role": "user",
                        "content": "Please use the available tools (list_files, read_file, or query_api) to gather information before answering. Do not answer from your own knowledge.",
                    })
        else:
            print("Max tool calls reached, using last available answer", file=sys.stderr)
            if last_answer is None:
                last_answer = "Unable to complete the task within the tool call limit."
    except Exception as e:
        print(f"Error in agentic loop: {e}", file=sys.stderr)
        if last_answer is None:
            last_answer = f"Error: {e}"

    # Extract source from answer or from tool calls
    source = ""
    try:
        if last_answer and not last_answer.startswith("Error:"):
            # Look for wiki or file paths in the answer
            match = re.search(r'(wiki/[\w-]+\.md(?:#[\w-]+)?)', last_answer)
            if match:
                source = match.group(1)
            
            if not source:
                match = re.search(r'(backend/app/[\w/]+\.py)', last_answer)
                if match:
                    source = match.group(1)

        if not source and tool_calls_log:
            # Look at the last read_file call
            for tc in reversed(tool_calls_log):
                if tc.get("tool") == "read_file":
                    path = tc.get("args", {}).get("path", "")
                    if path:
                        source = path
                    break
    except Exception as e:
        print(f"Error extracting source: {e}", file=sys.stderr)

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
    print(f"[DEBUG] Question: {question}", file=sys.stderr)

    # Get configuration (from env vars or files)
    config = get_config()

    # Run the agentic loop and always output valid JSON
    try:
        response = run_agentic_loop(question, config)
        print(json.dumps(response))
    except Exception as e:
        # Catch any unexpected errors and return valid JSON
        print(f"[ERROR] Unhandled exception: {e}", file=sys.stderr)
        result = {
            "answer": f"Error: {e}",
            "source": "",
            "tool_calls": []
        }
        print(json.dumps(result))
    
    sys.exit(0)


if __name__ == "__main__":
    main()