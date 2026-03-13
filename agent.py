import os
import sys
import json
import httpx
from openai import OpenAI
from dotenv import load_dotenv

def get_abs_path(path):
    # Security check: Ensure path is within the current project directory
    project_root = os.path.abspath(os.getcwd())
    abs_path = os.path.abspath(os.path.join(project_root, path))
    
    if os.path.commonpath([project_root]) != os.path.commonpath([project_root, abs_path]):
        raise PermissionError(f"Access denied: Path '{path}' is outside the project root.")
    
    return abs_path

def list_files(path):
    try:
        abs_path = get_abs_path(path)
        if not os.path.isdir(abs_path):
            return f"Error: '{path}' is not a directory."
        return "\n".join(os.listdir(abs_path))
    except Exception as e:
        return f"Error: {e}"

def read_file(path):
    try:
        abs_path = get_abs_path(path)
        if not os.path.isfile(abs_path):
            return f"Error: File '{path}' not found."
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Truncate if too large to avoid context blowing up, but keep enough for answers
            if len(content) > 10000:
                return content[:10000] + "\n\n[Content truncated...]"
            return content
    except Exception as e:
        return f"Error: {e}"

def query_api(method, path, body=None):
    base_url = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")
    api_key = os.getenv("LMS_API_KEY")
    
    if not api_key:
        return "Error: LMS_API_KEY not set in environment."
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    
    try:
        with httpx.Client() as client:
            if method.upper() == "GET":
                response = client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = client.post(url, headers=headers, content=body)
            elif method.upper() == "PUT":
                response = client.put(url, headers=headers, content=body)
            elif method.upper() == "DELETE":
                response = client.delete(url, headers=headers)
            else:
                return f"Error: Unsupported HTTP method '{method}'."
            
            return json.dumps({
                "status_code": response.status_code,
                "body": response.text
            })
    except Exception as e:
        return f"Error calling API: {e}"

# Tool definitions for OpenAI
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at a given path relative to the project root.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The relative path to the directory (e.g., 'wiki')."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the content of a file given its relative path from the project root.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The relative path to the file (e.g., 'wiki/git.md')."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_api",
            "description": "Call the project's backend API to retrieve real-time system data, analytics, or perform actions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"], "description": "The HTTP method to use."},
                    "path": {"type": "string", "description": "The API endpoint path (e.g., '/items/')."},
                    "body": {"type": "string", "description": "Optional JSON request body as a string."}
                },
                "required": ["method", "path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "submit_answer",
            "description": "Submit your final answer once you have gathered enough information from tools.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string", "description": "The concise answer to the user's question."},
                    "source": {"type": "string", "description": "The source file and section anchor (e.g. 'wiki/git.md#merge-conflict'). Use 'unknown' or omit if no file source applies."}
                },
                "required": ["answer"]
            }
        }
    }
]

def main():
    # Load environment variables for local development
    load_dotenv(".env.agent.secret")
    load_dotenv(".env.docker.secret")
    
    api_key = os.getenv("LLM_API_KEY")
    api_base = os.getenv("LLM_API_BASE")
    model = os.getenv("LLM_MODEL", "qwen3-coder-plus")
    
    if not api_key or not api_base:
        print("Error: LLM_API_KEY or LLM_API_BASE not set.", file=sys.stderr)
        sys.exit(1)
        
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py <question>", file=sys.stderr)
        sys.exit(1)
        
    question = sys.argv[1]
    
    client = OpenAI(api_key=api_key, base_url=api_base)
    
    messages = [
        {
            "role": "system", 
            "content": (
                "You are a System Agent. Your goal is to answer questions about the project using documentation, source code, and the live API. "
                "1. For documentation, search in the 'wiki/' directory. "
                "2. For source code, search in the 'backend/' directory (e.g., 'backend/app/main.py'). "
                "3. For data-dependent or live system questions, use `query_api`. "
                "4. For bug diagnosis, query the API, read the error message, and then inspect the relevant source code files. "
                "CRITICAL: ALWAYS use `list_files` first to explore directories, and then `read_file` to read the content. "
                "DO NOT provide an answer without using `read_file` on a relevant file if the question is about specific content. "
                "To provide a final answer, you MUST call the `submit_answer` tool. "
                "Before submitting, ensure you have used `list_files` and `read_file` to verify facts from the repository."
            )
        },
        {"role": "user", "content": question}
    ]
    
    all_tool_calls_history = []
    final_output = None
    
    for _ in range(10):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            if not tool_calls:
                if response_message.content:
                    final_output = {"answer": response_message.content, "tool_calls": all_tool_calls_history}
                    break
                continue
            
            messages.append(response_message)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "submit_answer":
                    final_output = {
                        "answer": function_args.get("answer"),
                        "source": function_args.get("source", "unknown"),
                        "tool_calls": all_tool_calls_history
                    }
                    break

                if function_name == "list_files":
                    result = list_files(function_args.get("path"))
                elif function_name == "read_file":
                    result = read_file(function_args.get("path"))
                elif function_name == "query_api":
                    result = query_api(
                        function_args.get("method"),
                        function_args.get("path"),
                        function_args.get("body")
                    )
                else:
                    result = f"Error: Tool '{function_name}' not found."
                
                all_tool_calls_history.append({
                    "tool": function_name,
                    "args": function_args,
                    "result": str(result)
                })
                
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(result),
                })
            
            if final_output:
                break
                
        except Exception as e:
            print(f"Error in agent loop: {e}", file=sys.stderr)
            sys.exit(1)
            
    if not final_output:
        final_output = {
            "answer": "Reached maximum tool calls without finding a definitive answer.",
            "tool_calls": all_tool_calls_history
        }
        
    print(json.dumps(final_output))

if __name__ == "__main__":
    main()
