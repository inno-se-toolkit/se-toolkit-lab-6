import sys
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(".env.agent.secret")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the project repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path from project root."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at a given path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative directory path from project root."}
                },
                "required": ["path"]
            }
        }
    }
]

def is_safe_path(path):
    full_path = os.path.realpath(os.path.join(PROJECT_ROOT, path))
    return full_path.startswith(PROJECT_ROOT)

def read_file(path):
    if not is_safe_path(path):
        return "Error: path traversal not allowed."
    full_path = os.path.join(PROJECT_ROOT, path)
    if not os.path.isfile(full_path):
        return f"Error: file not found: {path}"
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()

def list_files(path):
    if not is_safe_path(path):
        return "Error: path traversal not allowed."
    full_path = os.path.join(PROJECT_ROOT, path)
    if not os.path.isdir(full_path):
        return f"Error: directory not found: {path}"
    return "\n".join(os.listdir(full_path))

def execute_tool(name, args):
    if name == "read_file":
        return read_file(args["path"])
    elif name == "list_files":
        return list_files(args["path"])
    return "Error: unknown tool."

def main():
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py <question>", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    client = OpenAI(
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_API_BASE"),
    )

    messages = [
        {"role": "system", "content": (
            "You are a helpful documentation assistant. "
            "Use list_files to discover wiki files, then read_file to find the answer. "
            "Always include the source as a file path and section anchor (e.g. wiki/git-workflow.md#resolving-merge-conflicts). "
            "Answer concisely based on the wiki content."
        )},
        {"role": "user", "content": question}
    ]

    all_tool_calls = []
    max_tool_calls = 10
    tool_call_count = 0
    answer = ""
    source = ""

    while tool_call_count < max_tool_calls:
        print(f"Calling LLM...", file=sys.stderr)
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL"),
            messages=messages,
            tools=TOOLS,
            timeout=60,
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for tc in msg.tool_calls:
                tool_call_count += 1
                name = tc.function.name
                args = json.loads(tc.function.arguments)
                print(f"Tool call: {name}({args})", file=sys.stderr)
                result = execute_tool(name, args)
                all_tool_calls.append({"tool": name, "args": args, "result": result})
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
        else:
            answer = msg.content.strip()
            break

    lines = answer.split("\n")
    source = ""
    for line in lines:
        if "wiki/" in line:
            parts = line.split("wiki/")
            if len(parts) > 1:
                source = "wiki/" + parts[1].strip().strip(".")
                break

    result = {"answer": answer, "source": source, "tool_calls": all_tool_calls}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
