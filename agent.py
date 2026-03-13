import os
import sys
import json
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
    }
]

def main():
    load_dotenv(".env.agent.secret")
    
    api_key = os.getenv("LLM_API_KEY")
    api_base = os.getenv("LLM_API_BASE")
    model = os.getenv("LLM_MODEL", "qwen3-coder-plus")
    
    if not api_key or not api_base:
        print("Error: LLM_API_KEY or LLM_API_BASE not set in .env.agent.secret", file=sys.stderr)
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
                "You are a Documentation Agent. Your goal is to answer questions about the project using the wiki. "
                "Use `list_files('wiki')` to discover documentation files and `read_file` to read their content. "
                "Always provide a concise answer and cite your source exactly as 'wiki/filename.md#section-anchor'. "
                "If you can't find the answer, say you don't know and don't cite a source. "
                "Your final response to the user must be a JSON object with 'answer' and 'source' fields."
            )
        },
        {"role": "user", "content": question}
    ]
    
    all_tool_calls_history = []
    
    for _ in range(10):  # Maximum 10 tool calls
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
                # Final answer from LLM
                content = response_message.content
                # Attempt to parse the content as JSON to extract answer and source
                try:
                    # Clean up the LLM's response if it wrapped JSON in markdown code blocks
                    json_str = content.strip()
                    if json_str.startswith("```json"):
                        json_str = json_str[len("```json"):].strip()
                    if json_str.endswith("```"):
                        json_str = json_str[:-3].strip()
                    
                    final_data = json.loads(json_str)
                    answer = final_data.get("answer", content)
                    source = final_data.get("source", "unknown")
                except:
                    answer = content
                    source = "unknown"
                
                output = {
                    "answer": answer,
                    "source": source,
                    "tool_calls": all_tool_calls_history
                }
                print(json.dumps(output))
                return
            
            # Execute tool calls
            messages.append(response_message)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "list_files":
                    result = list_files(function_args.get("path"))
                elif function_name == "read_file":
                    result = read_file(function_args.get("path"))
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
            
    # If we reached 10 calls without a final answer
    print(json.dumps({
        "answer": "Reached maximum tool calls without finding a definitive answer.",
        "source": "unknown",
        "tool_calls": all_tool_calls_history
    }))

if __name__ == "__main__":
    main()
