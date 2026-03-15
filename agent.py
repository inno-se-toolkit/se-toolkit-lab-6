#!/usr/bin/env python3
"""
Agent CLI with tools (read_file, list_files, query_api) and agentic loop.
"""
import re
import os
import sys
import json
import requests
from dotenv import load_dotenv
import argparse
from pathlib import Path

# Load environment variables
load_dotenv('.env.agent.secret')

# Constants
MAX_TOOL_CALLS = 10
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

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

def query_api(method, path, body=None):
    """Send HTTP request to the backend API."""
    base_url = os.getenv('AGENT_API_BASE_URL', 'http://localhost:42002')
    api_key = os.getenv('LMS_API_KEY')
    
    url = f"{base_url}{path}"
    headers = {}
    
    # Добавляем Authorization ТОЛЬКО если ключ существует и не пустой
    if api_key and api_key.strip():
        headers["Authorization"] = f"Bearer {api_key}"
        debug_log(f"🔑 Using API key for {method} {path}")
    else:
        debug_log(f"🔓 No API key - making UNAUTHENTICATED request to {method} {path}")
    
    try:
        if body:
            headers["Content-Type"] = "application/json"
            request_body = json.loads(body) if isinstance(body, str) else body
            response = requests.request(method, url, headers=headers, json=request_body, timeout=30)
        else:
            response = requests.request(method, url, headers=headers, timeout=30)
        
        debug_log(f"📊 Response status: {response.status_code}")
        
        return json.dumps({
            "status_code": response.status_code,
            "body": response.text
        })
    except requests.exceptions.ConnectionError:
        return json.dumps({
            "status_code": 0,
            "body": f"Error: Could not connect to {base_url}. Is the backend running?"
        })
    except Exception as e:
        return json.dumps({
            "status_code": 500,
            "body": f"Error: {str(e)}"
        })
# Tool definitions for function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a file from the project repository. Use this to examine source code, configuration files, or wiki documentation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root (e.g., 'backend/main.py', 'wiki/git-workflow.md', 'docker-compose.yml')"
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
            "description": "List files and directories at a given path. Use this to discover what files are available in a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path from project root (e.g., 'backend', 'wiki', 'backend/app/routers')"
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
            "description": "Send HTTP requests to the deployed backend API. Use this to get real-time data, check API responses, or test endpoints.",
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
                        "description": "API endpoint path (e.g., '/items/', '/analytics/completion-rate?lab=lab-01', '/health')"
                    },
                    "body": {
                        "type": "string",
                        "description": "Optional JSON request body for POST requests (as a string)"
                    }
                },
                "required": ["method", "path"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are a system agent with access to:
1. Wiki documentation (via list_files + read_file)
2. Source code (via read_file)
3. Live backend API (via query_api)

Choose the right tool based on the question:

- For **how-to questions** (e.g., "how to protect a branch", "how to connect via SSH"): 
  Use list_files on 'wiki' then read_file on relevant wiki files.

- For **code structure questions** (e.g., "what framework", "what routers exist"):
  First check backend/main.py for imports (look for 'from fastapi import', 'from flask import', etc.)
  Then check pyproject.toml or requirements.txt for dependencies
  Common frameworks: FastAPI, Flask, Django. Look for 'fastapi' in imports or dependencies.
  If you find imports like 'from fastapi import FastAPI', the framework is FastAPI.
  
  For **router questions** specifically:
  1. Use list_files on 'backend/app/routers' to see all router modules
  2. Then use read_file on EACH router file to understand what domain it handles:
     - items.py: handles item management (labs, tasks, items) - GET /items/, POST /items/, etc.
     - interactions.py: handles user interactions with the system
     - learners.py: handles learner/student data and enrollment
     - analytics.py: handles analytics endpoints (completion rates, timelines, scores, groups, pass rates)
     - pipeline.py: handles ETL pipeline operations (/pipeline/sync)
  3. Make sure to read ALL router files (items.py, interactions.py, learners.py, analytics.py, pipeline.py) before giving the final answer
  4. Summarize each router's domain based on the code comments, function names, and endpoints
  5. If you've only read some routers, continue until you've read all of them

- For **system facts** (e.g., "what status code", "what ports"):
  Use query_api to test endpoints and see responses.
  Try endpoints like /docs, /openapi.json, or /health to discover information.

- For **data queries** (e.g., "how many items", "what's the score"):
  Use query_api on appropriate endpoints:
  - /items/ - list all items
  - /analytics/completion-rate?lab=lab-01 - completion rates
  - /analytics/timeline?lab=lab-01 - timeline data
  - /analytics/scores?lab=lab-01 - score distribution
  - /analytics/groups?lab=lab-01 - group performance
  - /analytics/pass-rates?lab=lab-01 - pass rates

- For **bug diagnosis** (e.g., "why does it crash for lab-99"):
  First use query_api to see the error:
  - GET /analytics/completion-rate?lab=lab-99
  - GET /analytics/top-learners?lab=lab-99
  Then read_file on the relevant source code to find the bug:
  - backend/app/routers/analytics.py
  - backend/app/services/analytics_service.py
  Look for division by zero, NoneType errors, or sorting issues.

- For **authentication questions** (e.g., "what status code without auth header"):
  The query_api tool will NOT send an Authorization header if LMS_API_KEY is not set.
  Make a GET request to /items/ WITHOUT using an API key and check the status_code.
  The endpoint should return 401 Unauthorized when no API key is provided.
  Important: The LMS_API_KEY environment variable controls whether the request is authenticated.

- For **request lifecycle questions**:
  Read docker-compose.yml to understand services
  Read backend/Dockerfile and caddy/Caddyfile
  Trace the path: Caddy (reverse proxy) → FastAPI (backend) → auth → routers → ORM → PostgreSQL

- For **idempotency questions**:
  Read backend/app/etl.py to find the external_id check
  Look for how duplicate data is handled in the ETL pipeline

When using query_api:
- Always include the Authorization header automatically (LMS_API_KEY)
- For GET requests, just provide method and path
- For POST requests, provide JSON body as a string
- Base URL is configured via AGENT_API_BASE_URL

Always include source references when possible:
- For wiki answers: include the file path (e.g., wiki/github.md#protect-a-branch)
- For code answers: include the file path (e.g., backend/main.py)
- For router answers: include the file path for each router (e.g., backend/app/routers/items.py)
- For API answers: include the endpoint (e.g., /items/)

Be thorough and systematic. If you don't find information in one place, try another.
Make sure to read ALL relevant files before giving the final answer - don't stop after reading just one or two files."""

def call_llm(messages, tools=None):
    """Call LLM with messages and optional tools."""
    api_key = os.getenv('LLM_API_KEY')
    api_base = os.getenv('LLM_API_BASE')
    model = os.getenv('LLM_MODEL')
    
    if not all([api_key, api_base, model]):
        raise ValueError("Missing required LLM environment variables")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7
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
    # Handle different formats of tool_call
    if hasattr(tool_call, 'function'):
        # Object format (like from OpenAI SDK)
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        tool_call_id = tool_call.id
    elif isinstance(tool_call, dict):
        # Dict format (from API response)
        function_name = tool_call['function']['name']
        arguments = json.loads(tool_call['function']['arguments'])
        tool_call_id = tool_call['id']
    else:
        return {
            "tool_call_id": "unknown",
            "role": "tool",
            "name": "unknown",
            "content": "Error: Unknown tool call format"
        }
    
    debug_log(f"Executing {function_name} with args: {arguments}")
    
    if function_name == "read_file":
        result = read_file(arguments["path"])
    elif function_name == "list_files":
        result = list_files(arguments["path"])
    elif function_name == "query_api":
        method = arguments.get("method")
        path = arguments.get("path")
        body = arguments.get("body")
        result = query_api(method, path, body)
    else:
        result = f"Error: Unknown tool {function_name}"
    
    return {
        "tool_call_id": tool_call_id,
        "role": "tool",
        "name": function_name,
        "content": result
    }

def agent_loop(question):
    """Main agentic loop."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    
    all_tool_calls = []
    tool_call_count = 0
    
    while tool_call_count < MAX_TOOL_CALLS:
        debug_log(f"\n--- Loop iteration {tool_call_count + 1} ---")
        
        response = call_llm(messages, TOOLS)
        assistant_message = response['choices'][0]['message']
        
        # Handle null content (common when tool calls are present)
        content = assistant_message.get("content")
        if content is None:
            content = ""
        
        if 'tool_calls' not in assistant_message or not assistant_message['tool_calls']:
            # No tool calls - check if this is a router question and we need more files
            if "router" in question.lower() and "all" in question.lower():
                # For router questions, make sure we read all files
                routers_read = [tc for tc in all_tool_calls if tc["tool"] == "read_file" and "routers" in tc["args"].get("path", "")]
                router_files = ["items.py", "interactions.py", "learners.py", "analytics.py", "pipeline.py"]
                
                # Check which routers we've read
                read_files = [tc["args"].get("path", "").split('/')[-1] for tc in routers_read]
                missing_files = [f for f in router_files if f not in read_files]
                
                # If we haven't read all routers, continue the loop
                if missing_files:
                    debug_log(f"Only read {len(read_files)}/{len(router_files)} routers. Missing: {missing_files}")
                    # Add a message to remind the LLM to read remaining routers
                    messages.append({
                        "role": "user", 
                        "content": f"You've only read {len(read_files)} router files: {read_files}. Please continue reading the remaining router modules: {missing_files} to complete the list."
                    })
                    continue
            
            # Normal answer - return with source
            # Try to extract source from the last read_file tool call
            source = ""
            if all_tool_calls:
                # Look for the last read_file tool call
                for tc in reversed(all_tool_calls):
                    if tc["tool"] == "read_file":
                        file_path = tc["args"].get("path", "")
                        # Try to find section anchor in the answer
                        section = ""
                        # Look for markdown headers in the answer
                        import re
                        headers = re.findall(r'#+\s+([^\n]+)', content)
                        if headers:
                            # Use the first header as section anchor
                            section = headers[0].lower().replace(' ', '-').replace(':', '').replace('.', '')
                        
                        if section:
                            source = f"{file_path}#{section}"
                        else:
                            source = file_path
                        break
            
            return {
                "answer": content,
                "source": source,
                "tool_calls": all_tool_calls
            }
        
        # Handle tool calls
        tool_calls = assistant_message['tool_calls']
        debug_log(f"Tool calls requested: {len(tool_calls)}")
        
        # Add assistant message to history
        messages.append({"role": "assistant", "content": content, "tool_calls": tool_calls})
        
        # Execute each tool call
        for tool_call in tool_calls:
            tool_result = execute_tool_call(tool_call)
            messages.append(tool_result)
            
            # Record for output - с правильной обработкой формата
            if hasattr(tool_call, 'function'):
                # Object format
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
            else:
                # Dict format
                tool_name = tool_call['function']['name']
                tool_args = json.loads(tool_call['function']['arguments'])
            
            all_tool_calls.append({
                "tool": tool_name,
                "args": tool_args,
                "result": tool_result["content"]
            })
            
            tool_call_count += 1
        
        if tool_call_count >= MAX_TOOL_CALLS:
            debug_log(f"Reached maximum tool calls ({MAX_TOOL_CALLS})")
            final_response = call_llm(messages)
            final_content = final_response['choices'][0]['message'].get("content", "Maximum tool calls reached")
            
            # Try to extract source even on max calls
            source = ""
            if all_tool_calls:
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
    
    # Validate required environment variables
    required_vars = ['LLM_API_KEY', 'LLM_API_BASE', 'LLM_MODEL', 'LMS_API_KEY']
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