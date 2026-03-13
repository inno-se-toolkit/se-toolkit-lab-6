import os, sys, json, httpx, time
from openai import OpenAI
from dotenv import load_dotenv

def get_abs_path(path):
    root = os.path.abspath(os.getcwd())
    abs_p = os.path.abspath(os.path.join(root, path))
    if not abs_p.startswith(root):
        raise PermissionError("Path outside root")
    return abs_p

def list_files(path):
    try:
        p = get_abs_path(path)
        if not os.path.exists(p): return f"Error: {path} not found"
        if os.path.isdir(p):
            return "\n".join(os.listdir(p))
        return f"Error: {path} is not a directory"
    except Exception as e: return str(e)

def read_file(path):
    try:
        p = get_abs_path(path)
        if not os.path.isfile(p): return f"Error: File '{path}' not found."
        with open(p, 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content) > 50000:
                return content[:50000] + "\n\n[TRUNCATED]"
            return content
    except Exception as e: return str(e)

def query_api(method, path, body=None):
    base_url = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")
    api_key = os.getenv("LMS_API_KEY")
    if not api_key: return "Error: LMS_API_KEY not set."
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    try:
        with httpx.Client(timeout=20.0) as client:
            if method.upper() == "GET": resp = client.get(url, headers=headers)
            else: resp = client.post(url, headers=headers, content=body)
            return json.dumps({"status_code": resp.status_code, "body": resp.text})
    except Exception as e: return f"API Error: {e}"

tools = [
    {"type": "function", "function": {"name": "list_files", "description": "List files in a directory.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read a file's content.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "query_api", "description": "Call the backend API.", "parameters": {"type": "object", "properties": {"method": {"type": "string", "enum": ["GET", "POST"]}, "path": {"type": "string"}, "body": {"type": "string"}}, "required": ["method", "path"]}}},
    {"type": "function", "function": {"name": "submit_answer", "description": "Submit final answer.", "parameters": {"type": "object", "properties": {"answer": {"type": "string"}, "source": {"type": "string"}}, "required": ["answer"]}}}
]

SYSTEM_PROMPT = """You are a System Agent for 'se-toolkit-lab-6'.
Answer questions using documentation (wiki/), code (backend/app/), and API.

RULES:
1. Use 'list_files' to discover files.
2. Use 'read_file' to get content. ALWAYS read the file before answering questions about its content.
3. For VM or SSH questions, look for 'wiki/vm.md' or 'wiki/ssh.md'.
4. For Docker questions, look for 'wiki/docker.md'.
5. For framework/code questions, check 'backend/app/main.py' or 'pyproject.toml'.
6. Use 'query_api' for data (e.g., item counts).
7. Submit answer ONLY via 'submit_answer' tool.
8. Source MUST be 'wiki/filename.md#anchor' if from wiki, or 'backend/app/file.py' if from code. Use 'unknown' only if no file applies.

OUTPUT: MUST call 'submit_answer' with valid JSON fields."""

def main():
    load_dotenv(".env.agent.secret")
    load_dotenv(".env.docker.secret")
    client = OpenAI(api_key=os.getenv("LLM_API_KEY"), base_url=os.getenv("LLM_API_BASE"))
    model = os.getenv("LLM_MODEL", "qwen3-coder-plus")
    question = sys.argv[1] if len(sys.argv) > 1 else "Hi"
    
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": question}]
    history = []
    
    for i in range(15):
        try:
            resp = client.chat.completions.create(model=model, messages=msgs, tools=tools, tool_choice="auto")
            m = resp.choices[0].message
            if not m.tool_calls:
                if m.content:
                    # Robust fallback if it didn't call submit_answer but gave text
                    print(json.dumps({"answer": m.content, "source": "unknown", "tool_calls": history}))
                    return
                continue
            
            msgs.append(m)
            for tc in m.tool_calls:
                fn, arg_str = tc.function.name, tc.function.arguments
                try: args = json.loads(arg_str)
                except: args = {}
                
                if fn == "submit_answer":
                    print(json.dumps({"answer": str(args.get("answer")), "source": str(args.get("source", "unknown")), "tool_calls": history}))
                    return
                
                res = list_files(args.get("path", ".")) if fn == "list_files" else \
                      read_file(args.get("path", "")) if fn == "read_file" else \
                      query_api(args.get("method", "GET"), args.get("path", "/"), args.get("body")) if fn == "query_api" else "Error"
                
                history.append({"tool": fn, "args": args, "result": str(res)})
                msgs.append({"tool_call_id": tc.id, "role": "tool", "name": fn, "content": str(res)})
        except Exception as e:
            if "Connection reset" in str(e): time.sleep(2); continue
            print(json.dumps({"answer": f"Error: {e}", "tool_calls": history}))
            return
    print(json.dumps({"answer": "Timeout", "tool_calls": history}))

if __name__ == "__main__": main()
