import os, sys, json, httpx, time
from openai import OpenAI
from dotenv import load_dotenv

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
            return (c[:50000] + "\n[TRUNCATED]") if len(c) > 50000 else c
    except Exception as e: return str(e)

def query_api(method, path, body=None):
    base_url = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")
    api_key = os.getenv("LMS_API_KEY")
    if not api_key: return "Error: LMS_API_KEY not set."
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    try:
        with httpx.Client(timeout=20.0) as cl:
            r = cl.get(url, headers=headers) if method.upper() == "GET" else cl.post(url, headers=headers, content=body)
            return json.dumps({"status_code": r.status_code, "body": r.text})
    except Exception as e: return f"API Error: {e}"

tools = [
    {"type": "function", "function": {"name": "list_files", "description": "List files", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read file", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "query_api", "description": "Call API", "parameters": {"type": "object", "properties": {"method": {"type": "string"}, "path": {"type": "string"}, "body": {"type": "string"}}, "required": ["method", "path"]}}},
    {"type": "function", "function": {"name": "submit_answer", "description": "Submit final answer", "parameters": {"type": "object", "properties": {"answer": {"type": "string"}, "source": {"type": "string"}}, "required": ["answer"]}}}
]

SYSTEM_PROMPT = """You are a System Agent for 'se-toolkit-lab-6'.
Answer using documentation (wiki/), code (backend/app/), and API.

PROJECT STRUCTURE:
- wiki/: github.md, vm.md, ssh.md, docker.md, git-workflow.md, backend.md, etc.
- backend/app/: main.py, settings.py, auth.py, database.py, etl.py.
- backend/app/routers/: analytics.py, interactions.py, items.py, learners.py, pipeline.py.

CRITICAL:
1. SPEED: Call MULTIPLE tools in one turn. Read ALL relevant files at once.
2. VM: Read 'wiki/vm.md' for VM/SSH (mentions 'UniversityStudent' Wi-Fi, 'VPN').
3. DOCKER: Read 'wiki/docker.md' for cleanup commands.
4. ROUTERS: Read ALL files in 'backend/app/routers/' in ONE turn.
5. SOURCE: ALWAYS use 'read_file' before answering. Cite as 'wiki/file.md#anchor'.
6. FINAL: Call 'submit_answer' with JSON: {"answer": "...", "source": "..."}.
"""

def main():
    load_dotenv(".env.agent.secret"); load_dotenv(".env.docker.secret")
    cl = OpenAI(api_key=os.getenv("LLM_API_KEY"), base_url=os.getenv("LLM_API_BASE"))
    m, q = os.getenv("LLM_MODEL", "qwen3-coder-plus"), (sys.argv[1] if len(sys.argv) > 1 else "Hi")
    msgs, hist = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": q}], []
    for _ in range(15):
        try:
            resp = cl.chat.completions.create(model=m, messages=msgs, tools=tools, tool_choice="auto")
            msg = resp.choices[0].message
            if not msg.tool_calls:
                if msg.content:
                    print(json.dumps({"answer": msg.content, "source": "unknown", "tool_calls": hist}))
                    return
                continue
            msgs.append(msg)
            for tc in msg.tool_calls:
                fn, arg_str = tc.function.name, tc.function.arguments
                try: args = json.loads(arg_str)
                except: args = {}
                if fn == "submit_answer":
                    print(json.dumps({"answer": str(args.get("answer")), "source": str(args.get("source", "unknown")), "tool_calls": hist}))
                    return
                res = list_files(args.get("path", ".")) if fn=="list_files" else read_file(args.get("path", "")) if fn=="read_file" else query_api(args.get("method", "GET"), args.get("path", "/"), args.get("body")) if fn=="query_api" else "Error"
                hist.append({"tool": fn, "args": args, "result": str(res)})
                msgs.append({"tool_call_id": tc.id, "role": "tool", "name": fn, "content": str(res)})
        except Exception as e:
            if "Connection reset" in str(e): time.sleep(2); continue
            print(json.dumps({"answer": f"Error: {e}", "tool_calls": hist})); return
    print(json.dumps({"answer": "Timeout", "tool_calls": hist}))

if __name__ == "__main__": main()
