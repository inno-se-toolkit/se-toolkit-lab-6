#!/usr/bin/env python3
"""
Task 2: Documentation Agent with agentic loop and tools.

CLI usage:
  uv run agent.py "How do you resolve a merge conflict?"

Output:
  A single JSON line to stdout:
    {"answer": "...", "source": "wiki/git.md#anchor", "tool_calls": [...]}

All debug/progress output goes to stderr.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import httpx


def _load_env_file(path: str) -> None:
    """
    Load KEY=VALUE pairs into os.environ.

    Only sets values for keys that are not already present in os.environ.
    This lets the autochecker safely inject its own credentials.
    """

    if not os.path.exists(path):
        return

    try:
        content = open(path, "r", encoding="utf-8").read()
    except OSError:
        # If the file can't be read, we fall back to environment variables.
        return

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')

        if key and key not in os.environ:
            os.environ[key] = value


def _require_env(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _get_project_root() -> Path:
    """Get the project root directory (assumed to be where agent.py is)."""
    return Path(__file__).resolve().parent


def _validate_path(path: str) -> Path:
    """
    Validate and normalize a path to ensure it's within the project root.
    
    Raises RuntimeError if path escapes the project root or is absolute.
    Returns the validated absolute path.
    """
    # Reject absolute paths
    if os.path.isabs(path):
        raise RuntimeError(f"Absolute paths not allowed: {path}")
    
    # Reject paths with .. components
    if ".." in path:
        raise RuntimeError(f"Path traversal (..) not allowed: {path}")
    
    # Normalize and check it's within project root
    project_root = _get_project_root()
    try:
        abs_path = (project_root / path).resolve()
        if not str(abs_path).startswith(str(project_root)):
            raise RuntimeError(f"Path escapes project root: {path}")
    except (RuntimeError, ValueError) as e:
        raise RuntimeError(f"Invalid path: {path}") from e
    
    return abs_path


def _tool_read_file(path: str) -> str:
    """
    Read a file from the project repository.
    
    Parameters:
      path (string): Relative path from project root
    
    Returns:
      File contents as string, or error message if file doesn't exist
    """
    try:
        abs_path = _validate_path(path)
        content = abs_path.read_text(encoding="utf-8")
        return content
    except FileNotFoundError:
        return f"File not found: {path}"
    except RuntimeError as e:
        return str(e)
    except Exception as e:
        return f"Error reading {path}: {e}"


def _tool_list_files(path: str) -> str:
    """
    List files and directories at a given path.
    
    Parameters:
      path (string): Relative directory path from project root
    
    Returns:
      Newline-separated listing of entries
    """
    try:
        abs_path = _validate_path(path)
        if not abs_path.is_dir():
            return f"Not a directory: {path}"
        
        entries = sorted(abs_path.iterdir())
        result = []
        for entry in entries:
            if entry.is_dir():
                result.append(entry.name + "/")
            else:
                result.append(entry.name)
        return "\n".join(result) if result else ""
    except RuntimeError as e:
        return str(e)
    except Exception as e:
        return f"Error listing {path}: {e}"


def _tool_query_api(method: str, path: str, body: str | None = None) -> str:
    """
    Query the deployed backend API.
    
    Parameters:
      method (string): HTTP method (GET, POST, PUT, DELETE, etc.)
      path (string): API endpoint path (e.g., /items/, /analytics/completion-rate?lab=lab-01)
      body (string, optional): JSON request body for POST/PUT requests
    
    Returns:
      JSON string with status_code and body fields
    """
    try:
        # Get API configuration from environment
        base_url = os.environ.get("AGENT_API_BASE_URL", "http://localhost:42002").rstrip("/")
        api_key = _require_env("LMS_API_KEY")
        
        # Build full URL
        url = f"{base_url}{path}"
        
        # Prepare headers with Bearer token authentication
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        # Prepare request body
        request_kwargs: dict[str, Any] = {
            "headers": headers,
        }
        
        if method.upper() in ("POST", "PUT", "PATCH"):
            if body:
                try:
                    json.loads(body)  # Validate it's valid JSON
                    request_kwargs["content"] = body
                except json.JSONDecodeError:
                    return json.dumps({
                        "status_code": 400,
                        "body": "Invalid JSON in request body",
                    })
            else:
                request_kwargs["content"] = ""
        
        # Make the request
        timeout = httpx.Timeout(timeout=30.0, connect=10.0)
        with httpx.Client(timeout=timeout, trust_env=False) as client:
            if method.upper() == "GET":
                resp = client.get(url, headers=headers)
            elif method.upper() == "POST":
                resp = client.post(url, **request_kwargs)
            elif method.upper() == "PUT":
                resp = client.put(url, **request_kwargs)
            elif method.upper() == "DELETE":
                resp = client.delete(url, headers=headers)
            elif method.upper() == "PATCH":
                resp = client.patch(url, **request_kwargs)
            else:
                return json.dumps({
                    "status_code": 400,
                    "body": f"Unsupported HTTP method: {method}",
                })
        
        # Return response with status code and body
        try:
            body_data = resp.json()
        except Exception:
            body_data = resp.text
        
        return json.dumps({
            "status_code": resp.status_code,
            "body": body_data,
        })
    
    except RuntimeError as e:
        return json.dumps({
            "status_code": 500,
            "body": str(e),
        })
    except Exception as e:
        return json.dumps({
            "status_code": 500,
            "body": f"API request failed: {e}",
        })


def _call_tool(tool_name: str, args: dict[str, Any]) -> str:
    """
    Execute a tool and return the result.
    
    Parameters:
      tool_name: "read_file", "list_files", or "query_api"
      args: Tool arguments dict
    
    Returns:
      Tool result as string
    """
    if tool_name == "read_file":
        path = args.get("path", "")
        return _tool_read_file(path)
    elif tool_name == "list_files":
        path = args.get("path", "")
        return _tool_list_files(path)
    elif tool_name == "query_api":
        method = args.get("method", "GET")
        path = args.get("path", "")
        body = args.get("body")
        return _tool_query_api(method, path, body)
    else:
        return f"Unknown tool: {tool_name}"


def _get_tool_schemas() -> list[dict[str, Any]]:
    """
    Return tool definitions as JSON schemas for function calling.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a file from the project repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path from project root (e.g., 'wiki/git.md')",
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
                "description": "List files and directories at a given path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative directory path from project root (e.g., 'wiki')",
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
                "description": "Query the deployed backend API for live system data (items count, analytics, status codes). Use for framework/tech stack questions and data-dependent queries. Do NOT use for documentation lookups.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "method": {
                            "type": "string",
                            "description": "HTTP method: GET, POST, PUT, DELETE, PATCH",
                        },
                        "path": {
                            "type": "string",
                            "description": "API endpoint path, e.g. '/items/' or '/analytics/completion-rate?lab=lab-01'. Must include query string if needed.",
                        },
                        "body": {
                            "type": "string",
                            "description": "Optional JSON request body for POST/PUT/PATCH requests",
                        },
                    },
                    "required": ["method", "path"],
                },
            },
        },
    ]



def _extract_answer(payload: dict[str, Any]) -> str:
    """
    Extract a plain text answer from an OpenAI-compatible response.
    """

    choices = payload.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content")
    if content is None:
        return ""
    return str(content).strip()


def _call_llm(
    question: str,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Call the LLM with the given messages and optional tools.
    
    Returns the full response object (not just the answer).
    """
    api_base = _require_env("LLM_API_BASE").rstrip("/")
    api_key = _require_env("LLM_API_KEY")
    model = _require_env("LLM_MODEL")

    url = f"{api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    request_body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": 0,
    }
    
    if tools:
        request_body["tools"] = tools

    # Keep this well below the 60s end-to-end limit for the CLI.
    timeout = httpx.Timeout(timeout=50.0, connect=10.0)

    # Disable proxy auto-detection to keep local tests deterministic.
    with httpx.Client(timeout=timeout, trust_env=False) as client:
        resp = client.post(url, headers=headers, json=request_body)
        resp.raise_for_status()
        data = resp.json()

    if not isinstance(data, dict):
        raise RuntimeError("LLM response was not a JSON object")

    return data



def _extract_source_from_answer(answer: str, tool_calls: list[dict[str, Any]]) -> str:
    """
    Extract a source reference from the answer or tool calls.
    
    Looks for wiki file references in the answer text.
    Returns a string like "wiki/git.md#section" or empty string if not found.
    """
    # Look for wiki file references in the answer
    import re
    
    # Match patterns like "wiki/filename.md" or "wiki/filename.md#section"
    pattern = r"(wiki/[\w\-]+\.md(?:#[\w\-]+)?)"
    matches = re.findall(pattern, answer)
    
    if matches:
        return matches[0]
    
    # If no explicit reference in answer, try to infer from read_file tool calls
    for tool_call in tool_calls:
        if tool_call.get("tool") == "read_file":
            path = tool_call.get("args", {}).get("path", "")
            if path.startswith("wiki/"):
                return path
    
    return ""


def _run_agentic_loop(question: str) -> dict[str, Any]:
    """
    Run the agentic loop: send question, execute tools until answer found.
    
    Returns dict with:
      - answer: final text answer
      - source: wiki reference
      - tool_calls: list of all tool calls made
    """
    system_prompt = """You are a helpful system agent. Your role is to answer questions about the project by using available tools.

TOOL SELECTION RULES:

1. **read_file / list_files** — Use for DOCUMENTATION and SOURCE CODE lookups:
   - Questions about how to do something ("How do you resolve a merge conflict?")
   - Process documentation ("What are the steps to protect a branch?")
   - Code examples or implementation details (read source code)
   - Always look in wiki/ directory first for process docs

2. **query_api** — Use for LIVE SYSTEM DATA and FRAMEWORK/TECH FACTS:
   - "How many items are in the database?" → GET /items/
   - "What framework does this project use?" → Check framework from API or docs
   - "What are the status codes?" → Check API documentation or responses
   - "What's the completion rate for lab-99?" → GET /analytics/completion-rate?lab=lab-99
   - Any analytics/metrics queries → GET /analytics/*

3. **Never hardcode answers** — Always query the API for data-dependent questions.

WORKFLOW:
- Start by listing wiki/ files to understand available documentation
- For data questions, immediately call query_api with the right endpoint
- Combine tools as needed (e.g., read docs to understand framework, then query API)

FINAL ANSWER:
- Include a source reference when possible (e.g., "wiki/git.md#section" or "API: /items/")
- Be concise and cite your tools/sources"""

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    
    tools = _get_tool_schemas()
    tool_calls_log: list[dict[str, Any]] = []
    max_iterations = 10
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"[agent] Iteration {iteration}", file=sys.stderr)
        
        # Call LLM
        response = _call_llm(question, messages, tools)
        
        # Extract message from response
        choices = response.get("choices") or []
        if not choices:
            break
        
        message = choices[0].get("message") or {}
        
        # Check for tool calls
        tool_calls = message.get("tool_calls") or []
        
        if not tool_calls:
            # No more tool calls, we have the answer
            answer = message.get("content", "").strip()
            source = _extract_source_from_answer(answer, tool_calls_log)
            return {
                "answer": answer,
                "source": source,
                "tool_calls": tool_calls_log,
            }
        
        # Execute tool calls and collect results
        assistant_message: dict[str, Any] = {
            "role": "assistant",
            "content": message.get("content") or "",
        }
        if tool_calls:
            assistant_message["tool_calls"] = tool_calls
        
        messages.append(assistant_message)
        
        # Execute each tool call
        tool_results: list[dict[str, Any]] = []
        for tool_call in tool_calls:
            tool_name = tool_call.get("function", {}).get("name", "")
            tool_args_str = tool_call.get("function", {}).get("arguments", "{}")
            
            try:
                tool_args = json.loads(tool_args_str)
            except json.JSONDecodeError:
                tool_args = {}
            
            print(f"[agent] Calling tool: {tool_name}({tool_args})", file=sys.stderr)
            
            # Execute the tool
            result = _call_tool(tool_name, tool_args)
            
            # Log this tool call
            tool_calls_log.append({
                "tool": tool_name,
                "args": tool_args,
                "result": result,
            })
            
            # Add tool result to messages
            tool_results.append({
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": tool_args_str,
                },
                "id": tool_call.get("id", f"call_{len(tool_calls_log)}"),
                "content": result,
            })
        
        # Add tool results to messages as a tool role message
        if tool_results:
            messages.append({
                "role": "tool",
                "content": json.dumps(tool_results),
            })
    
    # Max iterations reached, return best answer we have
    answer = ""
    if messages:
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                answer = msg.get("content", "").strip()
                if answer:
                    break
    
    source = _extract_source_from_answer(answer, tool_calls_log)
    return {
        "answer": answer,
        "source": source,
        "tool_calls": tool_calls_log,
    }




def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: uv run agent.py "Your question here"', file=sys.stderr)
        sys.exit(2)

    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print("Question cannot be empty", file=sys.stderr)
        sys.exit(2)

    # Local convenience for development; autochecker injects env vars.
    _load_env_file(".env.agent.secret")
    _load_env_file(".env.docker.secret")

    try:
        result = _run_agentic_loop(question)
    except Exception as e:
        print(f"Agent error: {e}", file=sys.stderr)
        sys.exit(1)

    # Ensure source field is present
    if "source" not in result:
        result["source"] = ""
    
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

