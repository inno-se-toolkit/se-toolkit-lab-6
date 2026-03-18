import requests
import dotenv
import sys
import os
import json
import traceback
from colorama import init, Fore, Style

from agent.tools import *

global LLM_API_KEY
global LLM_API_BASE
global LLM_MODEL
global LLM_TEMPERATURE
global LLM_TOOLS

chat_history = []
tool_calls_log = []
system_prompt = """You are a helpful documentation assistant. You have access to tools to read files and list directories in the project wiki.

When answering questions:
1. Use list_files to discover what files exist in the wiki directory
2. Use read_file_content to read relevant files and find the answer
3. Include the source reference in your answer (format: wiki/filename.md#section-anchor)
4. Be concise and accurate

Always use tools to find answers - do not rely on your pre-trained knowledge.""" 

# get prompt from command line
def get_user_input():
    if len(sys.argv) < 2:
        raise Exception("No user input")
    return sys.argv[1]

# load environment variables
def get_env():

    dotenv.load_dotenv(".env.agent.secret")

    global LLM_API_KEY
    global LLM_API_BASE
    global LLM_MODEL
    global LLM_TEMPERATURE

    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_API_BASE = os.getenv("LLM_API_BASE")
    LLM_MODEL = os.getenv("LLM_MODEL")
    LLM_TEMPERATURE = os.getenv("LLM_TEMPERATURE")

    if not LLM_API_KEY:
        raise Exception("LLM_API_KEY is not set")
    if not LLM_API_BASE:
        raise Exception("LLM_API_BASE is not set")
    if not LLM_MODEL:
        raise Exception("LLM_MODEL is not set")
    if not LLM_TEMPERATURE:
        raise Exception("LLM_TEMPERATURE is not set")

# parse tools from tools.json
def parse_tools():
    global LLM_TOOLS
    with open("agent/tools.json") as f:
        tools = json.load(f)
        LLM_TOOLS = tools

# send request to the LLM API
def send_request():
    global LLM_API_KEY
    global LLM_API_BASE
    global LLM_MODEL
    global LLM_TEMPERATURE
    global LLM_TOOLS
    global chat_history
    global system_prompt

    # Prepend system prompt as first user message
    messages = [{"role": "user", "content": system_prompt}] + chat_history

    response = requests.post(
        f"{LLM_API_BASE}/messages",
        headers={
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": LLM_MODEL,
            "messages": messages,
            "tools": LLM_TOOLS,
            "max_tokens": 512,
            "temperature": float(LLM_TEMPERATURE),
        },
    )

    if not response.ok:
        raise Exception(f"LLM API error: {response.status_code}, response: {response.json()}")

    chat_history.append({
        "role": "assistant",
        "content": response.json()['content']
    })

    return response.json()

# run the agentic loop
def agentic_loop(prompt: str):
    global tool_calls_log
    
    chat_history.append({"role": "user", "content": prompt})
    final_answer = None
    
    while True:
        try:
            response = send_request()

            blocks = response['content']
            tool_results = []
            has_tools = False

            for block in blocks:
                if block['type'] == 'text':
                    print(f"{Fore.GREEN}{Style.BRIGHT}Assistant:\n{Style.RESET_ALL}{Fore.GREEN}{block['text']}{Style.RESET_ALL}\n", file=sys.stderr)
                    final_answer = block['text']

                elif block['type'] == 'tool_use':
                    has_tools = True
                    print(f"{Fore.YELLOW}{Style.BRIGHT}Executing tool: {block['name']}{Style.RESET_ALL}", file=sys.stderr)

                    result_data = globals()[block['name']](block['input'])
                    result_str = result_data.stdout if hasattr(result_data, 'stdout') else str(result_data)

                    print(f"{Fore.BLUE}Tool output: {result_str}{Style.RESET_ALL}\n", file=sys.stderr)

                    tool_calls_log.append({
                        "tool": block['name'],
                        "args": block['input'],
                        "result": result_str
                    })

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block['id'],
                        "content": result_str
                    })

            if has_tools:
                chat_history.append({
                    "role": "user",
                    "content": tool_results
                })
            else:
                break

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            exit(1)
    
    return final_answer

if __name__ == "__main__":
    try:
        get_env()
        parse_tools()
        prompt = get_user_input()
        final_answer = agentic_loop(prompt)

        # Extract source from the last read_file_content call
        source = ""
        for call in reversed(tool_calls_log):
            if call["tool"] == "read_file_content":
                file_path = call["args"].get("file_path", "")
                if file_path:
                    source = file_path
                    break

        output = {
            "answer": final_answer,
            "source": source,
            "tool_calls": tool_calls_log
        }
        print(json.dumps(output))

        exit(0)

    except requests.exceptions.ConnectionError as e:
        print(f"Network error occurred: {e}", file=sys.stderr)

    except requests.exceptions.Timeout as e:
        print(f"The request timed out: {e}", file=sys.stderr)

    except requests.exceptions.HTTPError as e:
        print(f"The API returned an error: {e}", file=sys.stderr)

    except requests.exceptions.RequestException as e:
        print(f"An ambiguous error occurred: {e}", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        exit(1)