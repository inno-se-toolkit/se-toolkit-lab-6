import argparse, json, os, sys, re
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(".env.agent.secret")

PROJECT_ROOT = Path(__file__).parent.resolve()
MAX_TOOL_CALLS = 10

def safe_path(path_str):
    path = Path(path_str)
    if ".." in path_str:
        return None
    full = (PROJECT_ROOT / path).resolve()
    if not str(full).startswith(str(PROJECT_ROOT)):
        return None
    return full

def read_file(path):
    safe = safe_path(path)
    if not safe or not safe.exists():
        return f"Error: Cannot read {path}"
    return safe.read_text()

def list_files(path):
    safe = safe_path(path)
    if not safe or not safe.is_dir():
        return f"Error: Cannot list {path}"
    entries = [f.name for f in safe.iterdir()]
    return "\n".join(entries)

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path from project root"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative directory path"}
                },
                "required": ["path"]
            }
        }
    }
]

TOOLS_MAP = {
    "read_file": read_file,
    "list_files": list_files
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    args = parser.parse_args()

    client = OpenAI(
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_API_BASE"),
    )
    model = os.getenv("LLM_MODEL")

    system_prompt = """You are a documentation agent. Use list_files to find wiki files, then read_file to find answers. 
Include source as file path with section anchor (e.g., wiki/git-workflow.md#section).
Answer concisely based only on file contents."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.question}
    ]

    tool_calls_log = []
    tool_call_count = 0

    while tool_call_count < MAX_TOOL_CALLS:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
            timeout=55
        )

        choice = response.choices[0]
        message = choice.message

        if message.content:
            answer = message.content.strip()
            source_match = re.search(r'(\w+/[\w\-]+\.md(?:#[\w\-]+)?)', answer)
            source = source_match.group(1) if source_match else "unknown"
            
            output = {
                "answer": answer,
                "source": source,
                "tool_calls": tool_calls_log
            }
            print(json.dumps(output, ensure_ascii=False))
            sys.exit(0)

        if message.tool_calls:
            for tc in message.tool_calls:
                if tool_call_count >= MAX_TOOL_CALLS:
                    break
                
                func_name = tc.function.name
                func_args = json.loads(tc.function.arguments)
                
                result = TOOLS_MAP.get(func_name, lambda **k: "Unknown tool")(
                    **func_args
                )
                
                tool_calls_log.append({
                    "tool": func_name,
                    "args": func_args,
                    "result": result
                })
                
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tc]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
                
                tool_call_count += 1

    output = {
        "answer": "Max tool calls reached",
        "source": "unknown",
        "tool_calls": tool_calls_log
    }
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)

if __name__ == "__main__":
    main()