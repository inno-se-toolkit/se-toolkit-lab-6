import os
import sys
import json
import httpx
from openai import OpenAI
from dotenv import load_dotenv

def get_abs_path(path):
    project_root = os.path.abspath(os.getcwd())
    abs_path = os.path.abspath(os.path.join(project_root, path))
    if os.path.commonpath([project_root]) != os.path.commonpath([project_root, abs_path]):
        raise PermissionError(f"Access denied: Path '{path}' is outside the project root.")
    return abs_path

def list_files(path):
    try:
        abs_path = get_abs_path(path)
        if not os.path.isdir(abs_path): return f"Error: '{path}' is not a directory."
        return "\n".join(os.listdir(abs_path))
    except Exception as e: return f"Error: {e}"

def read_file(path):
    try:
        abs_path = get_abs_path(path)
        if not os.path.isfile(abs_path): return f"Error: File '{path}' not found."
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content) > 10000: return content[:10000] + "\n\n[Content truncated...]"
            return content
    except Exception as e: return f"Error: {e}"

def query_api(method, path, body=None):
    base_url = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")
    api_key = os.getenv("LMS_API_KEY")
    if not api_key: return "Error: LMS_API_KEY not set."
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    try:
        with httpx.Client() as client:
            if method.upper() == "GET": resp = client.get(url, headers=headers)
            elif method.upper() == "POST": resp = client.post(url, headers=headers, content=body)
            else: return f"Error: Unsupported method '{method}'."
            return json.dumps({"status_code": resp.status_code, "body": resp.text})
    except Exception as e: return f"Error: {e}"

tools = [
    {"type": "function", "function": {"name": "list_files", "description": "List files in directory.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read file content.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "query_api", "description": "Call project API.", "parameters": {"type": "object", "properties": {"method": {"type": "string"}, "path": {"type": "string"}, "body": {"type": "string"}}, "required": ["method", "path"]}}},
    {"type": "function", "function": {"name": "submit_answer", "description": "Submit final answer.", "parameters": {"type": "object", "properties": {"answer": {"type": "string"}, "source": {"type": "string"}}, "required": ["answer"]}}}
]

def main():
    load_dotenv(".env.agent.secret")
    load_dotenv(".env.docker.secret")
    client = OpenAI(api_key=os.getenv("LLM_API_KEY"), base_url=os.getenv("LLM_API_BASE"))
    model = os.getenv("LLM_MODEL", "qwen3-coder-plus")
    question = sys.argv[1] if len(sys.argv) > 1 else "Hi"
    
    messages = [{"role": "system", "content": "You are a System Agent. ALWAYS use tools to verify facts. Call submit_answer only when finished. Documentation is in wiki/, source code in backend/app/main.py. Source format: 'wiki/filename.md#anchor' or 'unknown'."}, {"role": "user", "content": question}]
    history = []
    
    for _ in range(10):
        resp = client.chat.completions.create(model=model, messages=messages, tools=tools)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            print(json.dumps({"answer": msg.content or "No answer", "tool_calls": history}))
            return
        
        messages.append(msg)
        for tc in msg.tool_calls:
            fn, args = tc.function.name, json.loads(tc.function.arguments)
            if fn == "submit_answer":
                print(json.dumps({"answer": args.get("answer"), "source": args.get("source", "unknown"), "tool_calls": history}))
                return
            
            res = list_files(args.get("path")) if fn == "list_files" else \
                  read_file(args.get("path")) if fn == "read_file" else \
                  query_api(args.get("method"), args.get("path"), args.get("body")) if fn == "query_api" else "Error"
            
            history.append({"tool": fn, "args": args, "result": str(res)})
            messages.append({"tool_call_id": tc.id, "role": "tool", "name": fn, "content": str(res)})

if __name__ == "__main__": main()
