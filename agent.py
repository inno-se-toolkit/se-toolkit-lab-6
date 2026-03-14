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
    """Load LLM and LMS configuration from environment files."""
    # Load LLM config from .env.agent.secret
    llm_env_file = PROJECT_ROOT / ".env.agent.secret"
    load_dotenv(llm_env_file, override=True)
    
    # Load LMS config from .env.docker.secret
    lms_env_file = PROJECT_ROOT / ".env.docker.secret"
    if lms_env_file.exists():
        load_dotenv(lms_env_file, override=True)

    config = {
        "llm_api_key": os.getenv("LLM_API_KEY"),
        "llm_api_base": os.getenv("LLM_API_BASE"),
        "llm_model": os.getenv("LLM_MODEL", "qwen3-coder-plus"),
        "lms_api_key": os.getenv("LMS_API_KEY"),
        "agent_api_base_url": os.getenv("AGENT_API_BASE_URL", "http://localhost:42002"),
    }

    if not config["llm_api_key"]:
        print("Error: LLM_API_KEY not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    if not config["llm_api_base"]:
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


def query_api(method: str, path: str, body: str = None) -> dict:
    """
    Call the backend LMS API.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        path: API endpoint path (e.g., '/items/')
        body: Optional JSON request body for POST/PUT requests
        
    Returns:
        Dict with 'status_code' and 'body' keys, or 'error' key
    """
    # Read LMS API key and base URL from environment
    lms_api_key = os.getenv("LMS_API_KEY")
    agent_api_base_url = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")
    
    if not lms_api_key:
        return {"error": "LMS_API_KEY not set in environment"}
    
    # Construct full URL
    base_url = agent_api_base_url.rstrip("/")
    full_url = f"{base_url}{path}"
    
    print(f"Calling API: {method} {full_url}", file=sys.stderr)
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {lms_api_key}",
        }
        
        with httpx.Client(timeout=30.0) as client:
            if method.upper() == "GET":
                response = client.get(full_url, headers=headers)
            elif method.upper() == "POST":
                json_body = json.loads(body) if body else None
                response = client.post(full_url, headers=headers, json=json_body)
            elif method.upper() == "PUT":
                json_body = json.loads(body) if body else None
                response = client.put(full_url, headers=headers, json=json_body)
            elif method.upper() == "DELETE":
                response = client.delete(full_url, headers=headers)
            else:
                return {"error": f"Unsupported method: {method}"}
        
        result = {
            "status_code": response.status_code,
            "body": response.json() if response.text else None,
        }
        print(f"API response: {response.status_code}", file=sys.stderr)
        return result
        
    except httpx.HTTPError as e:
        return {"error": f"HTTP error: {str(e)}"}
    except json.JSONDecodeError as e:
        return {"error": f"JSON decode error: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to call API: {str(e)}"}


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
    {
        "type": "function",
        "function": {
            "name": "query_api",
            "description": "Call the backend LMS API to query data or check endpoint status. Use this for questions about database contents, API responses, status codes, or analytics. Do NOT use for wiki documentation or source code questions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "description": "HTTP method (GET, POST, PUT, DELETE). Use GET for reading data.",
                    },
                    "path": {
                        "type": "string",
                        "description": "API endpoint path (e.g., '/items/', '/analytics/completion-rate', '/pipeline/sync')",
                    },
                    "body": {
                        "type": "string",
                        "description": "Optional JSON request body for POST/PUT requests (e.g., '{}'). Not needed for GET.",
                    },
                },
                "required": ["method", "path"],
            },
        },
    },
]

# System prompt for the system agent
SYSTEM_PROMPT = """You are a system assistant that helps users find information in the project wiki, source code, and live backend API.

You have access to three tools:
1. `list_files` - List files in a directory (use to discover wiki files or source modules)
2. `read_file` - Read the contents of a file (use for wiki documentation, source code, config files)
3. `query_api` - Call the backend LMS API (use for database queries, API status, analytics, status codes)

## Tool Selection Guide - BE SPECIFIC

### Use `list_files` + `read_file` for:

**Wiki documentation questions:**
- "How do you protect a branch?" → list_files("wiki"), find git-related file, read_file
- "How to clean up Docker?" → list_files("wiki"), find docker-related file, read_file
- "SSH connection steps?" → list_files("wiki"), find ssh/vm file, read_file

**Source code questions:**
- "What framework does the backend use?" → read_file("backend/app/main.py") - check imports
- "What technique in Dockerfile?" → read_file("Dockerfile") - look for FROM statements (note: Dockerfile is at project root, NOT backend/Dockerfile)
- "Error handling in code?" → read_file the specific file mentioned

**Configuration questions:**
- "Request lifecycle?" → read_file("docker-compose.yml"), read_file("caddy/Caddyfile"), read_file("Dockerfile"), read_file("backend/app/main.py")
- "ETL vs API error handling?" → read_file("backend/app/routers/pipeline.py") for ETL, read_file("backend/app/routers/analytics.py") for API - compare try/except patterns

**Important file paths:**
- Dockerfile: "Dockerfile" (at project root)
- Caddyfile: "caddy/Caddyfile"
- Main backend: "backend/app/main.py"
- Routers: "backend/app/routers/items.py", "backend/app/routers/analytics.py", "backend/app/routers/pipeline.py"
- ETL pipeline: "backend/app/routers/pipeline.py"

### Use `query_api` for:

**Database queries (COUNT, HOW MANY):**
- "How many items in database?" → query_api("GET", "/items/") - count the array
- "How many learners?" → query_api("GET", "/learners/") - count the array
- "Top learner?" → query_api("GET", "/analytics/top-learners")

**API status checks:**
- "What status code?" → query_api("GET", "/items/") - check status_code in response
- "Endpoint error?" → query_api("GET", "/analytics/completion-rate?lab=lab-99")

**Analytics data:**
- "Completion rate?" → query_api("GET", "/analytics/completion-rate?lab=lab-X")

### For Bug Diagnosis Questions:

**Division errors:**
1. query_api to reproduce: query_api("GET", "/analytics/completion-rate?lab=lab-99")
2. Look for "ZeroDivisionError" or "division by zero" in error
3. read_file("backend/app/routers/analytics.py") - find division operations
4. Identify the line with division that has no zero check

**None/TypeError:**
1. query_api to reproduce: query_api("GET", "/analytics/top-learners?lab=lab-X")
2. Look for "TypeError" or "NoneType" in error
3. read_file("backend/app/routers/analytics.py") - find sorted() or operations on potentially None values
4. Identify where None is not handled

## Step-by-Step Process

1. **Analyze the question type:**
   - "How many", "count", "how much" → query_api
   - "what steps", "how to" → wiki (list_files + read_file)
   - "what framework", "what technique" → source code (read_file)
   - "what error", "why does it crash" → query_api first, then read_file

2. **Execute tools systematically:**
   - For wiki: list_files("wiki") first, then read the relevant file
   - For source: read_file directly if you know the path
   - For data: query_api with the correct endpoint

3. **Extract the answer:**
   - From API: count items in the response array
   - From files: quote the relevant section
   - From errors: describe the error type and location

4. **Include source reference:**
   - For wiki: "wiki/git-workflow.md#protecting-a-branch"
   - For source: "backend/app/main.py" or "Dockerfile"
   - For API: "GET /items/" endpoint

## Critical Reminders

- ALWAYS use list_files FIRST for wiki questions to discover the right file
- For "how many items" - query_api("GET", "/items/") and COUNT the returned array
- For Dockerfile questions - read_file("Dockerfile") and look for multi-stage builds (multiple FROM)
- For bug questions - reproduce with query_api FIRST, then read the source code
- When you see division in code, check if there's a zero check - if not, that's the bug
- When you see sorted() or operations on API data, check if None is handled

## IMPORTANT: When to Stop and Give Final Answer

After you have read 2-3 relevant files OR gotten API responses:
1. STOP calling tools
2. Synthesize the information you have gathered
3. Provide a COMPLETE final answer based on what you found
4. Do NOT keep reading more files unless you truly cannot answer

**Example flow for "request lifecycle" question:**
1. read_file("docker-compose.yml") - see caddy, app, postgres services
2. read_file("caddy/Caddyfile") - see reverse proxy config
3. read_file("Dockerfile") - see FastAPI app
4. read_file("backend/app/main.py") - see routers and database
5. **STOP** - you have enough info, now EXPLAIN the full journey

**DO NOT:** Keep reading files indefinitely. After 3-4 files, you MUST provide an answer.

## Handling Errors

If a tool returns an error (e.g., "File not found"):
1. Try an alternative path (e.g., "Dockerfile" instead of "backend/Dockerfile")
2. If still not found, continue with other files you CAN read
3. Provide the best answer you can with available information
4. Do NOT give up after one error - adapt and continue

## Comparing Error Handling (ETL vs API)

When asked to compare error handling between ETL and API:
1. Read ETL code: read_file("backend/app/routers/pipeline.py") - look for try/except blocks
2. Read API code: read_file("backend/app/routers/analytics.py") - look for error responses
3. Compare:
   - ETL: Does it catch exceptions? Does it return error details?
   - API: Does it return 4xx/5xx status codes? Does it log errors?
4. Explain the difference: ETL may fail silently vs API returns HTTP errors
"""


def execute_tool(name: str, args: dict) -> dict:
    """
    Execute a tool and return the result.

    Args:
        name: Tool name ('read_file', 'list_files', or 'query_api')
        args: Tool arguments

    Returns:
        Tool result dict
    """
    if name == "read_file":
        return read_file(args.get("path", ""))
    elif name == "list_files":
        return list_files(args.get("path", ""))
    elif name == "query_api":
        return query_api(
            args.get("method", "GET"),
            args.get("path", ""),
            args.get("body"),
        )
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
    url = f"{config['llm_api_base']}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['llm_api_key']}",
    }
    payload = {
        "model": config["llm_model"],
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto",
    }

    print(f"Calling LLM at {url}...", file=sys.stderr)

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        print(f"Got response from LLM", file=sys.stderr)
        return data
    except httpx.HTTPError as e:
        print(f"LLM API error: {e}", file=sys.stderr)
        # Return a mock response for testing when API is unavailable
        return {
            "choices": [{
                "message": {
                    "content": f"LLM API unavailable: {e}",
                    "tool_calls": [],
                }
            }]
        }


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
    print(f"Using model: {config['llm_model']}", file=sys.stderr)

    # Run agentic loop
    result = run_agentic_loop(question, config)

    # Output structured JSON
    print(json.dumps(result))


if __name__ == "__main__":
    main()
