#!/usr/bin/env python3
"""
Agent CLI - Calls an LLM with tools to answer questions.

Usage:
    uv run agent.py "Your question here"

Output:
    JSON with 'answer', 'source', and 'tool_calls' fields to stdout.
    All debug/logging output goes to stderr.
"""

import json
import os
import sys
from pathlib import Path

import httpx


# Project root directory (where agent.py is located)
PROJECT_ROOT = Path(__file__).parent.resolve()

# Maximum tool calls per question
MAX_TOOL_CALLS = 10


def load_env_vars() -> dict[str, str]:
    """Load LLM configuration from environment variables."""
    required_vars = ["LLM_API_KEY", "LLM_API_BASE", "LLM_MODEL"]
    env_vars = {}

    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            print(
                f"Error: Missing required environment variable: {var}", file=sys.stderr
            )
            print(
                "Make sure .env.agent.secret exists and is loaded (e.g., via direnv or export)",
                file=sys.stderr,
            )
            sys.exit(1)
        env_vars[var] = value

    return env_vars


def is_safe_path(path: str) -> bool:
    """
    Check if a path is within the project directory.
    Prevents directory traversal attacks (../).
    """
    # Normalize and resolve the path
    abs_path = os.path.normpath(os.path.join(PROJECT_ROOT, path))
    # Check that it starts with the project root
    return abs_path.startswith(str(PROJECT_ROOT))


def tool_read_file(path: str) -> str:
    """
    Read the contents of a file from the project repository.

    Args:
        path: Relative path from project root

    Returns:
        File contents as string, or error message
    """
    # Security check
    if not is_safe_path(path):
        return f"Error: Access denied. Path '{path}' is outside project directory."

    # Construct absolute path
    abs_path = os.path.normpath(os.path.join(PROJECT_ROOT, path))

    # Check if file exists
    if not os.path.isfile(abs_path):
        return f"Error: File not found: {path}"

    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


def tool_list_files(path: str) -> str:
    """
    List files and directories at a given path.

    Args:
        path: Relative directory path from project root

    Returns:
        Newline-separated listing of files and directories
    """
    # Security check
    if not is_safe_path(path):
        return f"Error: Access denied. Path '{path}' is outside project directory."

    # Construct absolute path
    abs_path = os.path.normpath(os.path.join(PROJECT_ROOT, path))

    # Check if directory exists
    if not os.path.isdir(abs_path):
        return f"Error: Directory not found: {path}"

    try:
        entries = os.listdir(abs_path)
        # Filter out hidden files and sort
        entries = sorted([e for e in entries if not e.startswith(".")])
        return "\n".join(entries)
    except Exception as e:
        return f"Error listing directory: {e}"


# Map tool names to functions
TOOLS = {
    "read_file": tool_read_file,
    "list_files": tool_list_files,
}


def get_gemini_tool_schema() -> list[dict]:
    """Get tool schema for Google Gemini API."""
    return [
        {
            "functionDeclarations": [
                {
                    "name": "read_file",
                    "description": "Read the contents of a file from the project repository. Use this to read documentation files.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "path": {
                                "type": "STRING",
                                "description": "Relative path from project root (e.g., wiki/git-workflow.md)",
                            }
                        },
                        "required": ["path"],
                    },
                },
                {
                    "name": "list_files",
                    "description": "List files and directories at a given path. Use this to explore the project structure.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "path": {
                                "type": "STRING",
                                "description": "Relative directory path from project root (e.g., wiki)",
                            }
                        },
                        "required": ["path"],
                    },
                },
            ]
        }
    ]


def get_openai_tool_schema() -> list[dict]:
    """Get tool schema for OpenAI-compatible APIs."""
    return [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the contents of a file from the project repository. Use this to read documentation files.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path from project root (e.g., wiki/git-workflow.md)",
                        }
                    },
                    "required": ["path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List files and directories at a given path. Use this to explore the project structure.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative directory path from project root (e.g., wiki)",
                        }
                    },
                    "required": ["path"],
                },
            },
        },
    ]


def call_llm_gemini_with_tools(
    question: str, api_key: str, model: str, tool_calls_log: list[dict]
) -> tuple[str | None, list[dict] | None, str | None]:
    """
    Call Google Gemini API with tool support.

    Returns:
        Tuple of (answer, tool_calls, error)
        - If tool_calls: answer is None, tool_calls is list of tool calls to execute
        - If final answer: answer is the response, tool_calls is None
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json",
    }

    # Build system instruction
    system_instruction = """You are a documentation assistant with access to two tools:
- list_files: List files in a directory
- read_file: Read the contents of a file

When answering questions about the project:
1. Use list_files to explore the wiki directory structure
2. Use read_file to read relevant documentation files
3. Find the answer and cite the source (file path)
4. Only give a final answer when you have found the information

Always include the file path where you found the answer."""

    # Build conversation history
    contents = []

    # Add system instruction as first user message
    contents.append({"parts": [{"text": system_instruction}]})

    # Add user question
    contents.append({"parts": [{"text": question}]})

    # Add tool results from previous iterations
    for tool_call in tool_calls_log:
        contents.append(
            {
                "parts": [
                    {
                        "text": f"Tool result for {tool_call['tool']}({tool_call['args']}):\n{tool_call['result']}"
                    }
                ]
            }
        )

    payload = {
        "contents": contents,
        "tools": get_gemini_tool_schema(),
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000,
        },
    }

    print(f"Calling Gemini API with tools...", file=sys.stderr)

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # Check for function calls
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                content = candidate.get("content", {})

                # Check for function calls
                parts = content.get("parts", [])
                for part in parts:
                    if "functionCall" in part:
                        func_call = part["functionCall"]
                        tool_name = func_call.get("name")
                        args = func_call.get("args", {})

                        print(f"LLM wants to call tool: {tool_name}", file=sys.stderr)

                        # Execute the tool
                        if tool_name in TOOLS:
                            result = TOOLS[tool_name](**args)
                            return (
                                None,
                                [{"tool": tool_name, "args": args, "result": result}],
                                None,
                            )
                        else:
                            return (
                                None,
                                [
                                    {
                                        "tool": tool_name,
                                        "args": args,
                                        "result": f"Error: Unknown tool '{tool_name}'",
                                    }
                                ],
                                None,
                            )

                # No function calls - this is the final answer
                if "text" in parts[0]:
                    answer = parts[0]["text"]
                    return answer, None, None

            return "No answer found", None, None

    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        print(f"Response: {e.response.text}", file=sys.stderr)
        return None, None, f"HTTP error: {e}"
    except httpx.RequestError as e:
        print(f"Request error: {e}", file=sys.stderr)
        return None, None, f"Request error: {e}"
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return None, None, f"Unexpected error: {e}"


def extract_source_from_tool_calls(tool_calls: list[dict]) -> str:
    """Extract source reference from tool calls."""
    # Find the last read_file call
    for call in reversed(tool_calls):
        if call["tool"] == "read_file":
            path = call["args"].get("path", "")
            # Try to find a section in the result
            result = call.get("result", "")
            section = ""

            # Look for markdown headers in the result
            lines = result.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("#"):
                    # Extract section title and create anchor
                    section_title = line.lstrip("#").strip()
                    section = f"#{section_title.lower().replace(' ', '-')}"
                    break

            return f"{path}{section}"

    # Default to wiki directory if no read_file found
    return "wiki"


def run_agentic_loop(question: str, api_key: str, model: str) -> dict:
    """
    Run the agentic loop: call LLM, execute tools, repeat until answer.

    Returns:
        Dict with answer, source, and tool_calls
    """
    tool_calls_log: list[dict] = []
    answer = None
    max_iterations = MAX_TOOL_CALLS

    print(f"Starting agentic loop for question: {question}", file=sys.stderr)

    for iteration in range(max_iterations):
        print(f"\n--- Iteration {iteration + 1} ---", file=sys.stderr)

        # Call LLM with tools
        result_answer, tool_calls, error = call_llm_gemini_with_tools(
            question, api_key, model, tool_calls_log
        )

        if error:
            print(f"Error: {error}", file=sys.stderr)
            break

        if tool_calls:
            # Execute tool and add to log
            for tool_call in tool_calls:
                print(
                    f"Executed {tool_call['tool']}({tool_call['args']})",
                    file=sys.stderr,
                )
                tool_calls_log.append(tool_call)

            # Continue loop - LLM will use tool result
            continue

        if result_answer:
            answer = result_answer
            print(f"Got final answer", file=sys.stderr)
            break

    # If no answer after all iterations, use what we have
    if not answer:
        answer = "Unable to find a complete answer after maximum iterations."

    # Extract source
    source = extract_source_from_tool_calls(tool_calls_log)

    return {
        "answer": answer,
        "source": source,
        "tool_calls": tool_calls_log,
    }


def main() -> None:
    """Main entry point for the agent CLI."""
    # Check command-line arguments
    if len(sys.argv) != 2:
        print('Usage: uv run agent.py "<question>"', file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    # Load environment variables
    env_vars = load_env_vars()
    api_key = env_vars["LLM_API_KEY"]
    api_base = env_vars["LLM_API_BASE"]
    model = env_vars["LLM_MODEL"]

    print(f"Question: {question}", file=sys.stderr)
    print(f"Using model: {model}", file=sys.stderr)
    print(f"Project root: {PROJECT_ROOT}", file=sys.stderr)

    # Run agentic loop (Gemini only for now)
    if "googleapis.com" in api_base:
        result = run_agentic_loop(question, api_key, model)
    else:
        # Fallback to simple LLM call without tools
        print("Warning: Tools only supported for Google Gemini API", file=sys.stderr)
        result = {
            "answer": "Tools only supported for Google Gemini API",
            "source": "",
            "tool_calls": [],
        }

    # Output valid JSON to stdout
    print(json.dumps(result))

    print("\nDone.", file=sys.stderr)


if __name__ == "__main__":
    main()
