"""CLI agent that sends a question to an LLM and returns a JSON answer."""

import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(".env.agent.secret")
load_dotenv(".env.docker.secret")

API_KEY = os.environ.get("LLM_API_KEY", "")
API_BASE = os.environ.get("LLM_API_BASE", "").rstrip("/")
MODEL = os.environ.get("LLM_MODEL", "qwen3-coder-plus")
LMS_API_KEY = os.environ.get("LMS_API_KEY", "")
AGENT_API_BASE_URL = os.environ.get("AGENT_API_BASE_URL", "http://localhost:42002").rstrip("/")

PROJECT_ROOT = Path(__file__).resolve().parent

MAX_TOOL_CALLS = 10

SYSTEM_PROMPT = """\
You are a system agent for a Learning Management Service project. \
You can read project files, list directories, and query the deployed backend API.

Choose the right tool for each question:

- **Wiki / documentation questions** → call list_files("wiki") to discover files, \
then read_file on the relevant wiki file.
- **Source code questions** (framework, architecture, routers, code structure) → \
call list_files on backend directories (e.g., "backend/app", "backend/app/routers"), \
then read_file on relevant source files. Also read pyproject.toml or docker-compose.yml if needed.
- **Data questions** (counts, scores, items in the database) → call query_api with the appropriate endpoint. \
Common endpoints: GET /items/, GET /learners/, GET /analytics/completion-rate?lab=LAB_ID, \
GET /analytics/top-learners?lab=LAB_ID.
- **Status code / auth questions** → call query_api to test the endpoint and observe the response.
- **Bug diagnosis** → first call query_api to trigger the error and see the response, \
then use list_files and read_file to find and read the relevant source code to identify the bug.
- **Architecture / request lifecycle** → read docker-compose.yml, Dockerfile, caddy config, \
and backend source code to trace the full path.
- **ETL / pipeline questions** → read the ETL pipeline source code (backend/app/etl.py or similar).

When answering:
- Be concise and specific.
- If you read a file, include a source reference: file_path#section-anchor.
- For data questions, include the actual numbers from the API response.
- For bug diagnosis, identify the specific error type and the buggy line of code.
- Always use the tools to get real data — never guess or make up answers.\
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the project repository. Use for wiki pages, source code, config files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root (e.g., 'wiki/git-workflow.md', 'backend/app/main.py').",
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
            "description": "List files and directories at a given path in the project repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path from project root (e.g., 'wiki', 'backend/app/routers').",
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
            "description": "Send an HTTP request to the deployed backend API. Use for data queries, testing endpoints, checking status codes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "description": "HTTP method (GET, POST, PUT, DELETE).",
                    },
                    "path": {
                        "type": "string",
                        "description": "API path (e.g., '/items/', '/analytics/completion-rate?lab=lab-1').",
                    },
                    "body": {
                        "type": "string",
                        "description": "Optional JSON request body.",
                    },
                },
                "required": ["method", "path"],
            },
        },
    },
]


def _safe_resolve(path_str: str) -> Path | None:
    """Resolve a relative path safely, rejecting traversal outside the project."""
    resolved = (PROJECT_ROOT / path_str).resolve()
    if not str(resolved).startswith(str(PROJECT_ROOT)):
        return None
    return resolved


def tool_read_file(path: str) -> str:
    resolved = _safe_resolve(path)
    if resolved is None:
        return "Error: path traversal outside project directory is not allowed."
    if not resolved.is_file():
        return f"Error: file not found: {path}"
    return resolved.read_text(encoding="utf-8")


def tool_list_files(path: str) -> str:
    resolved = _safe_resolve(path)
    if resolved is None:
        return "Error: path traversal outside project directory is not allowed."
    if not resolved.is_dir():
        return f"Error: directory not found: {path}"
    entries = sorted(e.name for e in resolved.iterdir() if not e.name.startswith("."))
    return "\n".join(entries)


def tool_query_api(method: str, path: str, body: str | None = None) -> str:
    url = f"{AGENT_API_BASE_URL}{path}"
    headers: dict[str, str] = {}
    if LMS_API_KEY:
        headers["X-API-Key"] = LMS_API_KEY
    try:
        response = httpx.request(
            method=method.upper(),
            url=url,
            headers=headers,
            content=body.encode() if body else None,
            timeout=30,
        )
        response_body = response.text
        return json.dumps({"status_code": response.status_code, "body": response_body})
    except Exception as e:
        return json.dumps({"status_code": 0, "body": f"Error: {e}"})


TOOL_DISPATCH: dict[str, object] = {
    "read_file": tool_read_file,
    "list_files": tool_list_files,
    "query_api": tool_query_api,
}


def call_llm(messages: list[dict]) -> dict:
    response = httpx.post(
        f"{API_BASE}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": MODEL,
            "messages": messages,
            "tools": TOOLS,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py <question>", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    if not API_KEY or not API_BASE:
        print("Error: LLM_API_KEY and LLM_API_BASE must be set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)

    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    tool_call_log: list[dict] = []
    total_tool_calls = 0

    while True:
        print(f"Calling {MODEL}... (tool calls so far: {total_tool_calls})", file=sys.stderr)
        data = call_llm(messages)
        choice = data["choices"][0]
        message = choice["message"]

        # Add assistant message to conversation
        messages.append(message)

        # Check if the LLM wants to call tools
        if message.get("tool_calls") and total_tool_calls < MAX_TOOL_CALLS:
            for tc in message["tool_calls"]:
                func_name = tc["function"]["name"]
                func_args = json.loads(tc["function"]["arguments"])
                tool_call_id = tc["id"]

                print(f"  Tool: {func_name}({func_args})", file=sys.stderr)

                handler = TOOL_DISPATCH.get(func_name)
                if handler is None:
                    result_str = f"Error: unknown tool: {func_name}"
                else:
                    result_str = handler(**func_args)

                tool_call_log.append({
                    "tool": func_name,
                    "args": func_args,
                    "result": result_str[:500],
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": result_str,
                })

                total_tool_calls += 1
                if total_tool_calls >= MAX_TOOL_CALLS:
                    print("  Max tool calls reached.", file=sys.stderr)
                    break
        else:
            # Final text answer
            answer_text = (message.get("content") or "")
            break

    # Extract source from read_file calls
    source = ""
    for log_entry in tool_call_log:
        if log_entry["tool"] == "read_file":
            source = log_entry["args"].get("path", "")
            break

    result = {
        "answer": answer_text,
        "source": source,
        "tool_calls": tool_call_log,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
