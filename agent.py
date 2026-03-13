import os, sys, json, httpx, time
from openai import OpenAI
from dotenv import load_dotenv

# Security: Ensure paths are within the project root
def get_abs_path(path):
    root = os.path.abspath(os.getcwd())
    abs_p = os.path.abspath(os.path.join(root, path))
    if not abs_p.startswith(root): raise PermissionError("Path outside root")
    return abs_p

def list_files(path):
    try:
        p = get_abs_path(path)
        if not os.path.exists(p): return f"Error: {path} not found"
        return "\n".join(os.listdir(p)) if os.path.isdir(p) else f"Error: {path} not dir"
    except Exception as e: return str(e)

def read_file(path):
    try:
        p = get_abs_path(path)
        if not os.path.isfile(p): return f"Error: File '{path}' not found."
        with open(p, 'r', encoding='utf-8') as f:
            c = f.read()
            # generous limit for documentation
            return (c[:40000] + "\n[TRUNCATED]") if len(c) > 40000 else c
    except Exception as e: return str(e)

def query_api(method, path, body=None, headers=None):
    base_url = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")
    api_key = os.getenv("LMS_API_KEY")
    
    # Default headers if none provided
    if headers is None:
        if not api_key: return "Error: LMS_API_KEY not set."
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    try:
        with httpx.Client(timeout=30.0) as cl:
            if method.upper() == "GET": r = cl.get(url, headers=headers)
            elif method.upper() == "POST": r = cl.post(url, headers=headers, content=body)
            else: return f"Error: Unsupported method {method}"
            return json.dumps({"status_code": r.status_code, "body": r.text})
    except Exception as e: return f"API Error: {e}"

tools = [
    {"type": "function", "function": {"name": "list_files", "description": "List files in a directory.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read a file's content.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "query_api", "description": "Call the backend API.", "parameters": {"type": "object", "properties": {"method": {"type": "string", "enum": ["GET", "POST"]}, "path": {"type": "string"}, "body": {"type": "string"}, "headers": {"type": "object", "description": "Optional HTTP headers. If omitted, LMS_API_KEY is used."}}, "required": ["method", "path"]}}},
    {"type": "function", "function": {"name": "submit_answer", "description": "Submit final answer with source reference.", "parameters": {"type": "object", "properties": {"answer": {"type": "string", "description": "The final answer to the user's question."}, "source": {"type": "string", "description": "The source of the information (e.g. file path or API endpoint)."}}, "required": ["answer", "source"]}}}
]

SYSTEM_PROMPT = """You are a System Agent for 'se-toolkit-lab-6'.
Answer questions using documentation (wiki/), code (backend/app/), and API.

CORE KNOWLEDGE:
- VM/SSH: Read 'wiki/vm.md' or 'wiki/ssh.md'. Keywords: 'UniversityStudent' Wi-Fi, 'VPN', 'root' user.
- DOCKER: Read 'wiki/docker.md', 'docker-compose.yml', 'Dockerfile', 'caddy/Caddyfile'.
- BACKEND: FastAPI framework. Entry: 'backend/app/main.py'. Routers in 'backend/app/routers/'.
- ETL: Read 'backend/app/etl.py' for data loading logic.
- API: /items/, /learners/, /analytics/groups?lab=lab-01, /analytics/completion-rate?lab=lab-01.

STRATEGY:
1. Call MULTIPLE tools in one turn to be fast (e.g. read all router files at once).
2. ALWAYS use 'read_file' or 'query_api' to verify facts. NO GUESSING.
3. If asked for distinct counts, use the analytics API or count items in lists.
4. If asked about status codes without auth, call 'query_api' with empty 'headers' object {}.
5. Source format: 'wiki/file.md#anchor' or 'backend/app/file.py' or 'GET /api/endpoint'.
6. Final response MUST call 'submit_answer' with the final answer and source. DO NOT just output text until you have the final answer."""

def main():
    load_dotenv(".env.agent.secret"); load_dotenv(".env.docker.secret")
    client = OpenAI(api_key=os.getenv("LLM_API_KEY"), base_url=os.getenv("LLM_API_BASE"))
    model, q = os.getenv("LLM_MODEL", "qwen3-coder-plus"), (sys.argv[1] if len(sys.argv) > 1 else "Hi")
    msgs, hist = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": q}], []
    
    last_content = ""
    for i in range(40):
        try:
            resp = client.chat.completions.create(model=model, messages=msgs, tools=tools, tool_choice="auto")
            m = resp.choices[0].message
            
            if not m.content and not m.tool_calls:
                continue
                
            msgs.append(m)
            if m.content:
                last_content = m.content
            
            if not m.tool_calls:
                continue 
                
            for tc in m.tool_calls:
                fn, arg_str = tc.function.name, tc.function.arguments
                try: args = json.loads(arg_str)
                except: args = {}
                
                if fn == "submit_answer":
                    print(json.dumps({"answer": str(args.get("answer")), "source": str(args.get("source", "unknown")), "tool_calls": hist}))
                    return
                
                res = list_files(args.get("path", ".")) if fn=="list_files" else \
                      read_file(args.get("path", "")) if fn=="read_file" else \
                      query_api(args.get("method", "GET"), args.get("path", "/"), args.get("body"), args.get("headers")) if fn=="query_api" else "Error"
                
                hist.append({"tool": fn, "args": args, "result": str(res)})
                msgs.append({"tool_call_id": tc.id, "role": "tool", "name": fn, "content": str(res)})
        except Exception as e:
            if "Connection reset" in str(e): time.sleep(2); continue
            print(json.dumps({"answer": f"Error: {e}", "tool_calls": hist})); return
            
    # If we reached here, we timed out but might have some content
    print(json.dumps({"answer": last_content if last_content else "Timeout", "source": "unknown", "tool_calls": hist}))

if __name__ == "__main__": main()
