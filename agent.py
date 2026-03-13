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
            return f.read()
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
            "description": "List files and directories at a given path relative to the project root. Useful for discovering documentation in 'wiki/' or source code in 'backend/'.",
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
            "description": "Read the content of a file given its relative path from the project root. Use this to find answers in documentation or to inspect source code for system facts.",
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
                "1. For documentation or code questions, use `list_files` and `read_file`. "
                "2. For data-dependent or live system questions, use `query_api`. "
                "3. For bug diagnosis, query the API, read the error message, and then inspect the relevant source code files. "
                "Always provide a concise answer. If you used a file from the wiki, you MUST cite your source as 'wiki/filename.md#section-anchor'. "
                "CRITICAL: YOUR FINAL RESPONSE MUST BE ONLY A JSON OBJECT. NO MARKDOWN, NO EXPLANATIONS. "
                "Format: {\"answer\": \"your concise answer here\", \"source\": \"wiki/filename.md#section-anchor\"}"
            )
        },
        {"role": "user", "content": question}
    ]
    
    all_tool_calls_history = []
    
    for _ in range(10):
        try:
            # For the first call, we can suggest tools, but for subsequent calls,
            # we want the LLM to either use a tool or provide the FINAL answer in JSON.
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            if not tool_calls:
                content = response_message.content or ""
                # Attempt to parse the content as JSON
                try:
                    # Robust parsing: find the first '{' and last '}'
                    start_idx = content.find('{')
                    end_idx = content.rfind('}')
                    if start_idx != -1 and end_idx != -1:
                        json_str = content[start_idx:end_idx+1]
                        final_data = json.loads(json_str)
                    else:
                        raise ValueError("No JSON found")
                    
                    answer = final_data.get("answer", content)
                    source = final_data.get("source")
                except:
                    # Fallback: create JSON if LLM failed to do so
                    answer = content
                    source = None
                
                output = {
                    "answer": answer,
                    "tool_calls": all_tool_calls_history
                }
                if source:
                    output["source"] = source
                    
                print(json.dumps(output))
                return
            
            messages.append(response_message)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
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
                
        except Exception as e:
            print(f"Error in agent loop: {e}", file=sys.stderr)
            sys.exit(1)
            
    print(json.dumps({
        "answer": "Reached maximum tool calls without finding a definitive answer.",
        "tool_calls": all_tool_calls_history
    }))

if __name__ == "__main__":
    main()
