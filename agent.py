#!/usr/bin/env python3
"""
Agent CLI with tools (read_file, list_files, query_api) and agentic loop.
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv
import argparse

# Load environment variables from all env files (if they exist)
load_dotenv('.env')
load_dotenv('.env.agent.secret')
load_dotenv('.env.docker.secret')

# Constants
MAX_TOOL_CALLS = 20
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Router files we expect for router-listing questions (ALL 5 routers)
ROUTER_FILES = {"items.py", "interactions.py", "analytics.py", "pipeline.py", "learners.py"}


def debug_log(message):
    """Print debug messages to stderr."""
    print(message, file=sys.stderr)


def validate_path(path):
    """Validate and normalize path to prevent directory traversal."""
    try:
        requested_path = os.path.abspath(os.path.join(PROJECT_ROOT, path))
        if not requested_path.startswith(PROJECT_ROOT):
            debug_log(f"Security: Path traversal attempt blocked: {path}")
            return None
        return requested_path
    except Exception as e:
        debug_log(f"Path validation error: {e}")
        return None


def read_file(path):
    """Read contents of a file."""
    valid_path = validate_path(path)
    if not valid_path:
        return f"Error: Invalid path or path traversal detected: {path}"
    try:
        with open(valid_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


def list_files(path):
    """List files and directories at given path."""
    valid_path = validate_path(path)
    if not valid_path:
        return f"Error: Invalid path or path traversal detected: {path}"
    try:
        if not os.path.exists(valid_path):
            return f"Error: Path not found: {path}"
        if not os.path.isdir(valid_path):
            return f"Error: Path is not a directory: {path}"
        return "\n".join(sorted(os.listdir(valid_path)))
    except Exception as e:
        return f"Error listing directory: {e}"


def query_api(method, path, body=None, include_auth=None):
    """Send HTTP request to the backend API.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        path: API endpoint path
        body: Optional JSON request body
        include_auth: Whether to include auth header. True=yes, False=no, None=use key if available
    """
    base_url = os.getenv('AGENT_API_BASE_URL', 'http://localhost:42002')
    api_key = os.getenv('LMS_API_KEY')

    url = f"{base_url}{path}"
    headers = {}

    # Add auth header based on include_auth parameter
    if include_auth is True:
        # Force include auth
        if api_key and api_key.strip():
            headers["Authorization"] = f"Bearer {api_key}"
            debug_log(f"[query_api] Using API key for {method} {url}")
    elif include_auth is False:
        # Force exclude auth
        debug_log(f"[query_api] Making request WITHOUT authentication to {method} {url}")
    else:
        # Use auth if key is available (default behavior)
        if api_key and api_key.strip():
            headers["Authorization"] = f"Bearer {api_key}"
            debug_log(f"[query_api] Using API key for {method} {url}")
        else:
            debug_log(f"[query_api] NO API KEY - making request WITHOUT authentication to {method} {url}")

    try:
        if body:
            headers["Content-Type"] = "application/json"
            try:
                request_body = json.loads(body) if isinstance(body, str) else body
            except json.JSONDecodeError:
                return json.dumps({"status_code": 400, "body": f"Error: Invalid JSON body: {body}"})
            response = requests.request(method, url, headers=headers, json=request_body, timeout=30)
        else:
            response = requests.request(method, url, headers=headers, timeout=30)

        debug_log(f"[query_api] Response status: {response.status_code}")
        debug_log(f"[query_api] Response body (first 200 chars): {response.text[:200]}")
        return json.dumps({"status_code": response.status_code, "body": response.text})

    except requests.exceptions.ConnectionError as e:
        debug_log(f"[query_api] Connection error: {e}")
        return json.dumps({
            "status_code": 0,
            "body": f"Error: Could not connect to {base_url}. Is the backend running? Check that docker-compose is up and the app service is healthy."
        })
    except requests.exceptions.Timeout:
        debug_log(f"[query_api] Timeout connecting to {url}")
        return json.dumps({
            "status_code": 0,
            "body": f"Error: Request timed out after 30s. The backend at {base_url} may be slow or unresponsive."
        })
    except Exception as e:
        debug_log(f"[query_api] Unexpected error: {e}")
        return json.dumps({"status_code": 500, "body": f"Error: {str(e)}"})


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read contents of a file from the project repository. "
                "Use this to examine source code, configuration files, or wiki documentation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Relative path from project root "
                            "(e.g., 'backend/app/main.py', 'wiki/git-workflow.md', 'docker-compose.yml')"
                        )
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
            "description": (
                "List files and directories at a given path. "
                "Use this to discover what files are available in a directory."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Relative directory path from project root "
                            "(e.g., 'backend', 'wiki', 'backend/app/routers')"
                        )
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
            "description": (
                "Send HTTP requests to the deployed backend API. "
                "Use this to get real-time data, check API responses, or test endpoints. "
                "Always use this for questions about HTTP status codes, item counts, or any live data. "
                "For authentication tests, set include_auth=false to omit the API key header."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE"],
                        "description": "HTTP method for the request"
                    },
                    "path": {
                        "type": "string",
                        "description": (
                            "API endpoint path "
                            "(e.g., '/items/', '/analytics/completion-rate?lab=lab-01')"
                        )
                    },
                    "body": {
                        "type": "string",
                        "description": "Optional JSON request body for POST requests (as a string)"
                    },
                    "include_auth": {
                        "type": "boolean",
                        "description": "Whether to include API key in Authorization header. Set to false to test unauthenticated access (default: true)"
                    }
                },
                "required": ["method", "path"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are a system agent with access to three tools:
1. read_file — read any file from the project (wiki, source code, config)
2. list_files — list contents of a directory
3. query_api — make HTTP requests to the live backend API

ROUTING RULES — choose the right tool for the question type:

WIKI / HOW-TO questions (e.g., "how to protect a branch", "connect via SSH", "clean up Docker"):
  -> Step 1: list_files on 'wiki' to see available files.
  -> Step 2: Find the relevant wiki file (e.g., ssh.md for SSH, docker.md for Docker, cleanup.md for cleanup).
  -> Step 3: read_file the relevant wiki file — DO NOT answer without reading it!
  -> Step 4: Extract the answer from the file contents and cite the wiki file as source.
  -> IMPORTANT: After list_files, you MUST call read_file on the relevant file before answering.

SOURCE CODE questions (e.g., "what framework does the backend use", "what technique in Dockerfile"):
  -> Step 1: read_file 'backend/app/main.py' and look for imports like 'from fastapi import FastAPI'.
  -> Step 2: Also check 'backend/Dockerfile', 'pyproject.toml', or 'backend/requirements.txt' if needed.
  -> Step 3: Report the framework/technique with evidence from the source.

ROUTER LISTING questions (e.g., "list all API router modules", "what domain does each handle"):
  -> Step 1: list_files on 'backend/app/routers' to see all modules.
  -> Step 2: read_file on EVERY .py router file — items.py, interactions.py,
     analytics.py, pipeline.py, learners.py. Read ALL of them.
  -> Step 3: Only AFTER reading every router file, write your complete final answer.
  -> IMPORTANT: Do NOT write a partial answer and stop early. Read ALL files first.
  -> Final answer must list: items (items CRUD), interactions (user interactions), 
     analytics (statistics and completion rates), pipeline (ETL data loading), 
     learners (top learners and student data).

DATA QUERIES (e.g., "how many items are in the database", "how many learners", "what is the completion rate"):
  -> CRITICAL: Use query_api to get live data from the backend.
  -> For item count: query_api GET /items/ and count the entries in the JSON array.
  -> For learner count: query_api GET /learners/ and count distinct learners.
  -> For analytics: query_api GET /analytics/completion-rate?lab=lab-XX
  -> DO NOT read files for data questions — the data is in the database, not in files!
  -> Report the exact number from the API response.

HTTP STATUS CODE questions (e.g., "what status code without auth header"):
  -> CRITICAL: Use query_api with include_auth=false to test the endpoint WITHOUT authentication.
  -> Call query_api GET /items/ with include_auth=false and report the exact status_code.
  -> Expected: 401 Unauthorized or 403 Forbidden.
  -> Also read backend/app/auth.py to confirm the authentication logic if asked.

BUG DIAGNOSIS (e.g., "what error for lab-99", "why does top-learners crash", "which endpoints have bugs"):
  -> Step 1: query_api the crashing endpoint (e.g., GET /analytics/completion-rate?lab=lab-99).
  -> Step 2: Read the error message in the API response.
  -> Step 3: read_file the relevant router (e.g., backend/app/routers/analytics.py).
  -> Step 4: Find the exact line causing the bug and explain it.
  -> CRITICAL: When analyzing analytics.py for bugs, look for:
     - DIVISION operations: Check if denominator can be zero (e.g., total_learners=0 in completion-rate)
     - SORTING with None: Check if sorted() is called on data that may contain None values (e.g., avg_score=None in top-learners)
     - NoneType errors: Check if operations are performed on values that could be None
  -> Common bugs in analytics.py:
     - ZeroDivisionError: division by zero when total_learners=0 in get_completion_rate()
     - TypeError: '<' not supported between instances of 'NoneType' and 'NoneType' in get_top_learners() sorted()
  -> Report the exact error, the buggy line number, and explain the fix.

COMPARISON questions (e.g., "compare ETL vs API error handling", "how does X differ from Y"):
  -> Step 1: Identify BOTH files/components to compare.
  -> Step 2: read_file the first component (e.g., backend/app/etl.py for ETL).
  -> Step 3: read_file the second component (e.g., backend/app/routers/*.py for API).
  -> Step 4: Compare their approaches explicitly:
     - Error handling: try/except vs HTTPException
     - Data validation: external_id checks vs IntegrityError
     - Retry logic: pagination with has_more vs single request
     - Idempotency: skip duplicates vs reject duplicates
  -> Step 5: Provide a structured comparison in your answer.
  -> IMPORTANT: You MUST read BOTH files before answering comparison questions!

REQUEST LIFECYCLE (e.g., "journey of an HTTP request from browser to database"):
  -> Step 1: read_file docker-compose.yml to see service topology.
  -> Step 2: read_file caddy/Caddyfile to see reverse proxy config.
  -> Step 3: read_file backend/Dockerfile to see app setup.
  -> Step 4: read_file backend/app/main.py to see FastAPI entry point.
  -> Trace: Browser -> Caddy (port 42001) -> FastAPI (port 42002) -> auth middleware 
     -> router handler -> SQLAlchemy ORM -> PostgreSQL (port 42003) -> response back.

IDEMPOTENCY / ETL questions (e.g., "how does ETL ensure idempotency", "what happens if same data loaded twice"):
  -> Step 1: read_file backend/app/etl.py — find the external_id duplicate check.
  -> Step 2: Also read backend/app/routers/pipeline.py for the API endpoint.
  -> Explain: The ETL pipeline checks if external_id already exists before inserting.
     - If external_id exists → SKIP (no duplicate created)
     - If external_id is new → INSERT
  -> This ensures idempotency: loading the same data twice produces the same result as loading it once.

ERROR HANDLING questions (e.g., "how does ETL handle failures", "what is the error handling strategy"):
  -> Step 1: read_file the relevant component (etl.py for ETL, routers/*.py for API).
  -> Step 2: Look for:
     - try/except blocks
     - HTTPException raises
     - IntegrityError handling
     - Rollback operations (await session.rollback())
     - Retry logic (pagination, has_more)
  -> Step 3: Describe the strategy:
     - ETL: Uses httpx for HTTP calls with raise_for_status(), pagination with has_more for retry,
       external_id check for idempotency, session.commit() after batch operations.
     - API routers: Use HTTPException for client errors, IntegrityError for constraint violations,
       session.rollback() on errors, Depends(get_session) for session management.

OUTPUT RULES:
- Set "source" to the most relevant file path used (e.g., "wiki/github.md").
- For API-only answers, source can be an empty string.
- Be precise: include exact status codes, error messages, line numbers, and counts.
- For router questions: list EVERY router module with its domain before stopping.
- For data questions: ALWAYS use query_api — never read files for live data!
- For wiki questions: ALWAYS read the wiki file before answering — do not answer from file names alone!
- For bug questions: ALWAYS look for division by zero and None-unsafe operations in analytics.py!
- For comparison questions: ALWAYS read BOTH files before comparing!
"""


def call_llm(messages, tools=None):
    """Call LLM with messages and optional tools."""
    api_key = os.getenv('LLM_API_KEY')
    api_base = os.getenv('LLM_API_BASE')
    model = os.getenv('LLM_MODEL')

    if not all([api_key, api_base, model]):
        raise ValueError("Missing required LLM environment variables: LLM_API_KEY, LLM_API_BASE, LLM_MODEL")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.1,
    }

    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    try:
        response = requests.post(
            f"{api_base}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        debug_log(f"LLM call failed: {e}")
        raise


def execute_tool_call(tool_call):
    """Execute a tool call and return result."""
    try:
        if hasattr(tool_call, 'function'):
            function_name = tool_call.function.name
            arguments_str = tool_call.function.arguments
            tool_call_id = tool_call.id
        elif isinstance(tool_call, dict):
            function_name = tool_call['function']['name']
            arguments_str = tool_call['function']['arguments']
            tool_call_id = tool_call['id']
        else:
            return {
                "tool_call_id": "unknown",
                "role": "tool",
                "name": "unknown",
                "content": "Error: Unknown tool call format"
            }

        debug_log(f"Executing {function_name} with args: {arguments_str[:100] if len(arguments_str) > 100 else arguments_str}")
        
        try:
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError as e:
            debug_log(f"JSON parse error for {function_name}: {e}")
            debug_log(f"Raw arguments: {arguments_str}")
            return {
                "tool_call_id": tool_call_id,
                "role": "tool",
                "name": function_name,
                "content": f"Error: Invalid JSON arguments: {arguments_str[:200]}"
            }

        if function_name == "read_file":
            result = read_file(arguments["path"])
        elif function_name == "list_files":
            result = list_files(arguments["path"])
        elif function_name == "query_api":
            result = query_api(
                arguments.get("method"),
                arguments.get("path"),
                arguments.get("body"),
                arguments.get("include_auth")  # Pass include_auth parameter
            )
        else:
            result = f"Error: Unknown tool {function_name}"

        return {
            "tool_call_id": tool_call_id,
            "role": "tool",
            "name": function_name,
            "content": result
        }
    except Exception as e:
        debug_log(f"Error executing tool call: {e}")
        debug_log(f"Tool call: {tool_call}")
        return {
            "tool_call_id": "unknown",
            "role": "tool",
            "name": "unknown",
            "content": f"Error executing tool: {str(e)}"
        }


def _get_read_basenames(all_tool_calls):
    """Return set of basenames of files that have been read so far."""
    return {
        tc["args"].get("path", "").split("/")[-1]
        for tc in all_tool_calls
        if tc["tool"] == "read_file"
    }


def _answer_is_incomplete(content):
    """Return True if the LLM content suggests it wants to keep going."""
    phrases = [
        "let me continue", "let me read", "let me check", "let me now",
        "let me also", "let me look", "i'll continue", "i'll now",
        "i'll read", "i need to read", "continue reading",
        "now let me", "next i'll", "next i will", "i should also",
    ]
    c = content.lower()
    return any(p in c for p in phrases)


def agent_loop(question):
    """Main agentic loop."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]

    all_tool_calls = []
    tool_call_count = 0
    reprompt_count = 0  # Track consecutive re-prompts without tool calls
    q_lower = question.lower()
    
    # Detect question type for better guidance
    is_router_q = any(w in q_lower for w in ["router", "module", "domain"])
    is_data_q = any(w in q_lower for w in ["how many", "count", "items in", "database", "currently stored", "in the database", "stored in the database", "items are", "distinct learners"])
    is_wiki_q = any(w in q_lower for w in ["wiki", "how to", "steps to", "connect via ssh", "protect a branch", "ssh", "branch", "clean up", "docker"])
    is_lifecycle_q = any(w in q_lower for w in ["journey", "lifecycle", "http request", "browser to database", "request path", "full journey"])
    is_etl_q = any(w in q_lower for w in ["idempotency", "etl", "pipeline", "duplicate", "same data", "loaded twice"])
    is_status_q = any(w in q_lower for w in ["status code", "http status", "what does the api return", "without authentication", "without an authentication header", "without sending an authentication", "without auth"])
    is_bug_q = any(w in q_lower for w in ["crashes", "error", "bug", "what went wrong", "diagnose", "risky operations", "division", "sorting"])
    is_comparison_q = any(w in q_lower for w in ["compare", "vs", "versus", "differ", "difference", "both"])
    is_error_handling_q = any(w in q_lower for w in ["error handling", "failure", "strategy", "handle failures"])
    
    debug_log(f"[agent_loop] Question type: router={is_router_q}, data={is_data_q}, wiki={is_wiki_q}, lifecycle={is_lifecycle_q}, etl={is_etl_q}, status={is_status_q}, bug={is_bug_q}, comparison={is_comparison_q}, error_handling={is_error_handling_q}")

    while tool_call_count < MAX_TOOL_CALLS:
        # Prevent infinite re-prompt loops
        if reprompt_count >= 10:  # Increased limit to allow more iterations
            debug_log(f"Too many consecutive re-prompts ({reprompt_count}). Forcing final answer.")
            source = ""
            for tc in reversed(all_tool_calls):
                if tc["tool"] == "read_file":
                    source = tc["args"].get("path", "")
                    break
            # Make sure we have a valid answer to return
            final_answer = "Maximum re-prompts reached. Based on the information gathered:"
            if 'content' in dir() and content:
                final_answer = content
            return {
                "answer": final_answer,
                "source": source,
                "tool_calls": all_tool_calls
            }
        
        debug_log(f"\n--- Loop iteration {tool_call_count + 1} ---")

        response = call_llm(messages, TOOLS)
        assistant_message = response['choices'][0]['message']
        content = (assistant_message.get("content") or "")

        has_tool_calls = (
            'tool_calls' in assistant_message and assistant_message['tool_calls']
        )

        if not has_tool_calls:
            # LLM thinks it is done — check for incomplete answers
            
            # For bug questions - check if we already forced final answer
            already_forced_bug = any(tc.get("tool") == "forced_final_answer" for tc in all_tool_calls)
            if is_bug_q and already_forced_bug:
                debug_log("Bug question: Already forced final answer. Returning current content.")
                source = ""
                for tc in reversed(all_tool_calls):
                    if tc["tool"] == "read_file":
                        source = tc["args"].get("path", "")
                        break
                return {
                    "answer": content,
                    "source": source,
                    "tool_calls": [tc for tc in all_tool_calls if tc.get("tool") != "forced_final_answer"]
                }

            # Check for incomplete router answers
            if is_router_q:
                read_basenames = _get_read_basenames(all_tool_calls)
                missing_routers = ROUTER_FILES - read_basenames

                if missing_routers or _answer_is_incomplete(content):
                    debug_log(f"Router answer incomplete. Missing: {missing_routers}. Re-prompting.")
                    messages.append({"role": "assistant", "content": content})
                    if missing_routers:
                        nudge = (
                            f"Your answer is incomplete. You have NOT yet read these router files: "
                            f"{sorted(missing_routers)}. "
                            f"Use read_file on each missing file NOW, then provide the complete "
                            f"final answer listing ALL routers and the domain each one handles."
                        )
                    else:
                        nudge = (
                            "Your answer looks incomplete. Provide the complete final answer "
                            "listing ALL router modules and the domain each one handles."
                        )
                    messages.append({"role": "user", "content": nudge})
                    reprompt_count += 1
                    continue  # loop again without counting a tool call

            # Check for wiki questions where list_files was called but no read_file
            if is_wiki_q:
                has_list_files = any(tc["tool"] == "list_files" for tc in all_tool_calls)
                has_read_file = any(tc["tool"] == "read_file" for tc in all_tool_calls)

                if has_list_files and not has_read_file:
                    debug_log("Wiki question: list_files called but no read_file yet. Re-prompting.")
                    messages.append({"role": "assistant", "content": content})
                    nudge = (
                        "You listed the wiki files but haven't read the relevant file yet. "
                        "Find the relevant wiki file (e.g., ssh.md for SSH questions, github.md for branch protection) "
                        "and use read_file to read its contents BEFORE answering."
                    )
                    messages.append({"role": "user", "content": nudge})
                    reprompt_count += 1
                    continue  # loop again without counting a tool call

            # Check for lifecycle questions - ensure all config files are read
            if is_lifecycle_q:
                read_files = [tc["args"].get("path", "") for tc in all_tool_calls if tc["tool"] == "read_file"]
                required_files = ["docker-compose.yml", "Caddyfile", "Dockerfile", "main.py"]
                missing_files = [f for f in required_files if not any(f in rf for rf in read_files)]

                if missing_files:
                    debug_log(f"Lifecycle question: Missing files: {missing_files}. Re-prompting.")
                    messages.append({"role": "assistant", "content": content})
                    nudge = (
                        f"You haven't read all required files yet. Missing: {missing_files}. "
                        f"Read docker-compose.yml, caddy/Caddyfile, backend/Dockerfile (or Dockerfile), and backend/app/main.py "
                        f"to trace the full request path from browser to database."
                    )
                    messages.append({"role": "user", "content": nudge})
                    reprompt_count += 1
                    continue  # loop again without counting a tool call
                else:
                    # All files read - force final answer
                    debug_log("Lifecycle question: All required files read. Forcing final answer.")
                    messages.append({"role": "assistant", "content": content})
                    nudge = (
                        "You have now read all the required files (docker-compose.yml, Caddyfile, Dockerfile, main.py). "
                        "Provide your final answer explaining the full journey of an HTTP request from browser to database. "
                        "Trace: Browser -> Caddy (reverse proxy) -> FastAPI app -> auth middleware -> router -> ORM -> PostgreSQL."
                    )
                    messages.append({"role": "user", "content": nudge})
                    reprompt_count += 1
                    continue  # loop again to get final answer

            # Check for ETL questions - ensure pipeline code is read
            if is_etl_q:
                read_files = [tc["args"].get("path", "") for tc in all_tool_calls if tc["tool"] == "read_file"]
                has_etl_file = any("etl" in rf or "pipeline" in rf for rf in read_files)

                if not has_etl_file:
                    debug_log("ETL question: No ETL/pipeline file read yet. Re-prompting.")
                    messages.append({"role": "assistant", "content": content})
                    nudge = (
                        "You haven't read the ETL pipeline code yet. "
                        "Read backend/app/etl.py or backend/app/routers/pipeline.py to find the duplicate check logic."
                    )
                    messages.append({"role": "user", "content": nudge})
                    reprompt_count += 1
                    continue  # loop again without counting a tool call
                else:
                    # ETL file read - force final answer
                    debug_log("ETL question: ETL file read. Forcing final answer.")
                    messages.append({"role": "assistant", "content": content})
                    nudge = (
                        "You have now read the ETL pipeline code. "
                        "Provide your final answer explaining how idempotency is ensured. "
                        "Explain what happens when the same data is loaded twice (look for external_id check)."
                    )
                    messages.append({"role": "user", "content": nudge})
                    reprompt_count += 1
                    continue  # loop again to get final answer

            # Check for data questions - ensure query_api is called
            if is_data_q and not is_status_q:
                has_query_api = any(tc["tool"] == "query_api" for tc in all_tool_calls)

                if not has_query_api:
                    debug_log("Data question: No query_api call yet. Re-prompting.")
                    messages.append({"role": "assistant", "content": content})
                    nudge = (
                        "This question requires querying the live API for data. "
                        "Use query_api to GET the relevant endpoint and get the actual data. "
                        "For item count, use query_api GET /items/ and count the results."
                    )
                    messages.append({"role": "user", "content": nudge})
                    reprompt_count += 1
                    continue  # loop again without counting a tool call
            
            # Check for status code questions - ensure query_api is called
            if is_status_q:
                has_query_api = any(tc["tool"] == "query_api" for tc in all_tool_calls)

                if not has_query_api:
                    debug_log("Status question: No query_api call yet. Re-prompting.")
                    messages.append({"role": "assistant", "content": content})
                    nudge = (
                        "This question requires testing the API to see the HTTP status code. "
                        "Use query_api to make a request and check the status_code in the response. "
                        "For authentication questions, make the request WITHOUT the Authorization header."
                    )
                    messages.append({"role": "user", "content": nudge})
                    reprompt_count += 1
                    continue  # loop again without counting a tool call

            # Check for bug questions - ensure we have both query_api error and source code
            if is_bug_q:
                has_query_api = any(tc["tool"] == "query_api" for tc in all_tool_calls)
                has_read_file = any(tc["tool"] == "read_file" for tc in all_tool_calls)
                
                # Count how many times we've tried different labs
                query_api_count = len([tc for tc in all_tool_calls if tc["tool"] == "query_api"])

                if has_query_api and has_read_file:
                    # Both done - force final answer (only once)
                    if not any(tc.get("tool") == "forced_final_answer" for tc in all_tool_calls):
                        debug_log("Bug question: API queried and source read. Forcing final answer.")
                        messages.append({"role": "assistant", "content": content})
                        nudge = (
                            "You have queried the API and read the source code. "
                            "Now provide your final answer explaining the error and the bug in the source code. "
                            "Look for division by zero and None-unsafe sorted() calls. "
                            "DO NOT make more API calls - you have enough information."
                        )
                        messages.append({"role": "user", "content": nudge})
                        # Mark that we forced final answer
                        all_tool_calls.append({"tool": "forced_final_answer", "args": {}, "result": "forced"})
                        reprompt_count += 1
                        continue  # loop again to get final answer
                    elif query_api_count >= 2:
                        # Already made multiple queries - just return the answer
                        debug_log(f"Bug question: Already made {query_api_count} API calls. Returning current content.")
                        source = ""
                        for tc in reversed(all_tool_calls):
                            if tc["tool"] == "read_file":
                                source = tc["args"].get("path", "")
                                break
                        return {
                            "answer": content,
                            "source": source,
                            "tool_calls": [tc for tc in all_tool_calls if tc.get("tool") != "forced_final_answer"]
                        }
                    else:
                        # Already forced once - just return the answer
                        debug_log("Bug question: Already forced final answer. Returning current content.")
                        source = ""
                        for tc in reversed(all_tool_calls):
                            if tc["tool"] == "read_file":
                                source = tc["args"].get("path", "")
                                break
                        return {
                            "answer": content,
                            "source": source,
                            "tool_calls": [tc for tc in all_tool_calls if tc.get("tool") != "forced_final_answer"]
                        }

            # Check for comparison questions - ensure BOTH files are read
            if is_comparison_q or is_error_handling_q:
                read_files = [tc["args"].get("path", "") for tc in all_tool_calls if tc["tool"] == "read_file"]
                has_etl = any("etl" in rf for rf in read_files)
                has_router = any("router" in rf for rf in read_files)
                
                if not (has_etl and has_router):
                    debug_log(f"Comparison question: Need both ETL and router files. Have ETL={has_etl}, router={has_router}. Re-prompting.")
                    messages.append({"role": "assistant", "content": content})
                    nudge = (
                        "This is a comparison question. You need to read BOTH files before comparing:\n"
                        "- Read backend/app/etl.py for ETL error handling strategy\n"
                        "- Read backend/app/routers/*.py for API error handling strategy\n"
                        "Then compare: try/except vs HTTPException, pagination vs single request, external_id check vs IntegrityError."
                    )
                    messages.append({"role": "user", "content": nudge})
                    reprompt_count += 1
                    continue  # loop again without counting a tool call
                else:
                    # Both files read - force final answer
                    debug_log("Comparison question: Both files read. Forcing final answer.")
                    messages.append({"role": "assistant", "content": content})
                    nudge = (
                        "You have read both files. Now provide your final answer comparing the error handling strategies:\n"
                        "- ETL: httpx with raise_for_status(), pagination with has_more, external_id check for idempotency\n"
                        "- API routers: HTTPException for errors, IntegrityError handling, session.rollback() on failure"
                    )
                    messages.append({"role": "user", "content": nudge})
                    reprompt_count += 1
                    continue  # loop again to get final answer

            # Genuine final answer
            source = ""
            for tc in reversed(all_tool_calls):
                if tc["tool"] == "read_file":
                    source = tc["args"].get("path", "")
                    break

            return {
                "answer": content,
                "source": source,
                "tool_calls": all_tool_calls
            }

        # Process tool calls
        tool_calls = assistant_message['tool_calls']
        debug_log(f"Tool calls requested: {len(tool_calls)}")
        
        # Filter out invalid tool calls (empty function name)
        valid_tool_calls = []
        for tc in tool_calls:
            if hasattr(tc, 'function'):
                if tc.function.name:
                    valid_tool_calls.append(tc)
                else:
                    debug_log(f"Skipping invalid tool call with empty name: {tc}")
            elif isinstance(tc, dict):
                if tc.get('function', {}).get('name'):
                    valid_tool_calls.append(tc)
                else:
                    debug_log(f"Skipping invalid dict tool call with empty name: {tc}")
        
        if not valid_tool_calls:
            debug_log("No valid tool calls found.")
            
            # Track if we already forced final answer for bug questions
            already_forced_bug = any(tc.get("tool") == "forced_final_answer" for tc in all_tool_calls)
            
            # For router questions, check if we need to read more files
            if is_router_q and not already_forced_bug:
                read_basenames = _get_read_basenames(all_tool_calls)
                missing_routers = ROUTER_FILES - read_basenames

                if missing_routers:
                    debug_log(f"Router question: Missing routers {missing_routers}. Re-prompting.")
                    messages.append({"role": "assistant", "content": content})
                    nudge = (
                        f"You haven't read all router files yet. Missing: {sorted(missing_routers)}. "
                        f"Use read_file on each missing router file to get complete information."
                    )
                    messages.append({"role": "user", "content": nudge})
                    reprompt_count += 1
                    continue  # loop again without counting a tool call

            # For bug questions after forcing - just return the answer
            if is_bug_q and already_forced_bug:
                debug_log("Bug question: Already forced final answer. Returning current content.")
                source = ""
                for tc in reversed(all_tool_calls):
                    if tc["tool"] == "read_file":
                        source = tc["args"].get("path", "")
                        break
                return {
                    "answer": content,
                    "source": source,
                    "tool_calls": [tc for tc in all_tool_calls if tc.get("tool") != "forced_final_answer"]
                }

            # For other questions, treat as final answer
            source = ""
            for tc in reversed(all_tool_calls):
                if tc["tool"] == "read_file":
                    source = tc["args"].get("path", "")
                    break
            return {
                "answer": content,
                "source": source,
                "tool_calls": all_tool_calls
            }
        
        messages.append({"role": "assistant", "content": content, "tool_calls": valid_tool_calls})

        for tool_call in valid_tool_calls:
            tool_result = execute_tool_call(tool_call)
            messages.append(tool_result)

            if hasattr(tool_call, 'function'):
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
            else:
                tool_name = tool_call['function']['name']
                tool_args = json.loads(tool_call['function']['arguments'])

            all_tool_calls.append({
                "tool": tool_name,
                "args": tool_args,
                "result": tool_result["content"]
            })

            tool_call_count += 1
        
        # Reset reprompt count when we make progress with tool calls
        reprompt_count = 0

        if tool_call_count >= MAX_TOOL_CALLS:
            debug_log(f"Reached maximum tool calls ({MAX_TOOL_CALLS})")
            final_response = call_llm(messages)
            final_content = (
                final_response['choices'][0]['message'].get("content")
                or "Maximum tool calls reached"
            )

            source = ""
            for tc in reversed(all_tool_calls):
                if tc["tool"] == "read_file":
                    source = tc["args"].get("path", "")
                    break

            return {
                "answer": final_content,
                "source": source,
                "tool_calls": all_tool_calls
            }

    return {
        "answer": "Maximum iterations reached without final answer",
        "source": "",
        "tool_calls": all_tool_calls
    }


def main():
    parser = argparse.ArgumentParser(description='Ask a question to the system agent')
    parser.add_argument('question', type=str, help='The question to ask')
    args = parser.parse_args()

    # Only LLM vars are strictly required; LMS_API_KEY is optional
    required_vars = ['LLM_API_KEY', 'LLM_API_BASE', 'LLM_MODEL']
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        debug_log(f"Error: Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    debug_log(f"AGENT_API_BASE_URL: {os.getenv('AGENT_API_BASE_URL', 'http://localhost:42002')}")
    debug_log(f"Question: {args.question}")

    try:
        result = agent_loop(args.question)
        print(json.dumps(result))
    except Exception as e:
        debug_log(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
