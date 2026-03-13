import os, sys, json, httpx
from openai import OpenAI
from dotenv import load_dotenv

def get_abs_path(path):
    root = os.path.abspath(os.getcwd())
    abs_p = os.path.abspath(os.path.join(root, path))
    if os.path.commonpath([root]) != os.path.commonpath([root, abs_p]):
        raise PermissionError("Path outside root")
    return abs_p

def list_files(path):
    try:
        p = get_abs_path(path)
        return "\n".join(os.listdir(p)) if os.path.isdir(p) else f"Error: {path} not dir"
    except Exception as e: return str(e)

def read_file(path):
    try:
        p = get_abs_path(path)
        if not os.path.isfile(p): return f"Error: {path} not found"
        with open(p, 'r', encoding='utf-8') as f:
            c = f.read()
            return (c[:15000] + "\n[Truncated]") if len(c) > 15000 else c
    except Exception as e: return str(e)

def query_api(method, path, body=None):
    base = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")
    key = os.getenv("LMS_API_KEY")
    if not key: return "Error: LMS_API_KEY not set"
    h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    u = f"{base.rstrip('/')}/{path.lstrip('/')}"
    try:
        with httpx.Client() as cl:
            r = cl.get(u, headers=h) if method.upper()=="GET" else cl.post(u, headers=h, content=body)
            return json.dumps({"status_code": r.status_code, "body": r.text})
    except Exception as e: return str(e)

tools = [
    {"type": "function", "function": {"name": "list_files", "description": "List files", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read file", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "query_api", "description": "Call API", "parameters": {"type": "object", "properties": {"method": {"type": "string"}, "path": {"type": "string"}, "body": {"type": "string"}}, "required": ["method", "path"]}}}
]

def main():
    load_dotenv(".env.agent.secret")
    load_dotenv(".env.docker.secret")
    cl = OpenAI(api_key=os.getenv("LLM_API_KEY"), base_url=os.getenv("LLM_API_BASE"))
    m = os.getenv("LLM_MODEL", "qwen3-coder-plus")
    q = sys.argv[1] if len(sys.argv) > 1 else "Hi"
    msgs = [{"role": "system", "content": "You are a System Agent. ALWAYS use tools to find info. DO NOT guess. Your final response MUST be ONLY a JSON object with 'answer' (string) and 'source' (string, e.g. 'wiki/git.md#anchor'). No other text."}, {"role": "user", "content": q}]
    hist = []
    for _ in range(15):
        try:
            resp = cl.chat.completions.create(model=m, messages=msgs, tools=tools)
            msg = resp.choices[0].message
            if not msg.tool_calls:
                content = msg.content or ""
                start = content.find('{')
                end = content.rfind('}')
                if start != -1 and end != -1:
                    try:
                        data = json.loads(content[start:end+1])
                        ans = data.get("answer", content)
                        src = data.get("source", "unknown")
                        if isinstance(ans, list): ans = ", ".join(map(str, ans))
                        print(json.dumps({"answer": str(ans), "source": str(src), "tool_calls": history}))
                        return
                    except: pass
                print(json.dumps({"answer": content, "source": "unknown", "tool_calls": history}))
                return
            msgs.append(msg)
            for tc in msg.tool_calls:
                fn = tc.function.name
                try: args = json.loads(tc.function.arguments)
                except: args = {"path": "unknown"}
                res = list_files(args.get("path", ".")) if fn=="list_files" else \
                      read_file(args.get("path", "")) if fn=="read_file" else \
                      query_api(args.get("method", "GET"), args.get("path", ""), args.get("body")) if fn=="query_api" else "Error"
                hist.append({"tool": fn, "args": args, "result": str(res)})
                messages_to_add = {"tool_call_id": tc.id, "role": "tool", "name": fn, "content": str(res)}
                msgs.append(messages_to_add)
        except Exception as e:
            print(json.dumps({"answer": f"Error: {e}", "tool_calls": hist}))
            return

if __name__ == "__main__": main()
