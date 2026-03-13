#!/usr/bin/env python3
"""
Agent CLI — Call an LLM with tools to navigate the wiki and return structured JSON.

Usage:
    uv run agent.py "Your question here"

Output:
    JSON to stdout: {"answer": "...", "source": "...", "tool_calls": [...]}
    All debug output goes to stderr.
"""

import json
import os
import sys
from pathlib import Path

import httpx
from pydantic_settings import BaseSettings


class AgentSettings(BaseSettings):
    """Settings loaded from .env.agent.secret."""

    llm_api_key: str
    llm_api_base: str
    llm_model: str

    model_config = {
        "env_file": Path(__file__).parent / ".env.agent.secret",
        "env_file_encoding": "utf-8",
    }


def load_settings() -> AgentSettings:
    """Load and validate settings."""
    env_file = Path(__file__).parent / ".env.agent.secret"
    if not env_file.exists():
        print(f"Error: {env_file} not found", file=sys.stderr)
        print("Copy .env.agent.example to .env.agent.secret and fill in your credentials", file=sys.stderr)
        sys.exit(1)

    return AgentSettings()


def validate_path(relative_path: str) -> Path:
    """
    Validate that the path doesn't escape the project directory.
    
    Args:
        relative_path: Path relative to project root
        
    Returns:
        Absolute Path object
        
    Raises:
        ValueError: If path tries to escape project directory
    """
    project_root = Path(__file__).parent.resolve()
    full_path = (project_root / relative_path).resolve()
    
    # Check for path traversal
    try:
        full_path.relative_to(project_root)
    except ValueError:
        raise ValueError(f"Path traversal not allowed: {relative_path}")
    
    return full_path


def read_file(path: str) -> str:
    """
    Read contents of a file from the project repository.
    
    Args:
        path: Relative path from project root
        
    Returns:
        File contents as string, or error message
    """
    try:
        validated_path = validate_path(path)
        if not validated_path.exists():
            return f"Error: File not found: {path}"
        if not validated_path.is_file():
            return f"Error: Not a file: {path}"
        return validated_path.read_text(encoding="utf-8")
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error reading file: {e}"


def list_files(path: str) -> str:
    """
    List files and directories at a given path.
    
    Args:
        path: Relative directory path from project root
        
    Returns:
        Newline-separated listing of entries, or error message
    """
    try:
        validated_path = validate_path(path)
        if not validated_path.exists():
            return f"Error: Directory not found: {path}"
        if not validated_path.is_dir():
            return f"Error: Not a directory: {path}"
        
        entries = []
        for entry in sorted(validated_path.iterdir()):
            suffix = "/" if entry.is_dir() else ""
            entries.append(f"{entry.name}{suffix}")
        return "\n".join(entries)
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error listing directory: {e}"


# Tool definitions for LLM function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file from the project repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root (e.g., 'wiki/git-workflow.md')"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at a given path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path from project root (e.g., 'wiki')"
                    }
                },
                "required": ["path"]
            }
        }
    }
]

# Map tool names to actual functions
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "list_files": list_files,
}


SYSTEM_PROMPT = """You are a helpful documentation assistant. You have access to tools that let you read files and list directories in a project wiki.

When answering questions:
1. Use `list_files` to discover what files exist in the wiki
2. Use `read_file` to read the contents of relevant files
3. Find the specific section that answers the question
4. Include a source reference in your answer using the format: `wiki/filename.md#section-anchor`
5. Be concise and accurate

Always use tools to find the answer - don't make up information.
"""


def call_llm(
    messages: list[dict],
    tools: list[dict] | None = None,
    settings: AgentSettings | None = None,
) -> dict:
    """
    Call the LLM API and return the parsed response.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        tools: Optional list of tool definitions for function calling
        settings: Agent settings
        
    Returns:
        Parsed response dict with 'content' and optionally 'tool_calls'
    """
    url = f"{settings.llm_api_base}/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "temperature": 0.7,
    }
    
    if tools:
        payload["tools"] = tools

    print(f"Calling LLM at {url}...", file=sys.stderr)

    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()

    data = response.json()
    message = data["choices"][0]["message"]
    
    result = {
        "content": message.get("content"),
        "tool_calls": message.get("tool_calls"),
    }
    
    return result


def execute_tool(tool_call: dict) -> str:
    """
    Execute a tool call and return the result.
    
    Args:
        tool_call: Dict with 'function' containing 'name' and 'arguments'
        
    Returns:
        Tool result as string
    """
    function = tool_call["function"]
    name = function["name"]
    args = json.loads(function["arguments"])
    
    print(f"Executing tool: {name}({args})", file=sys.stderr)
    
    if name not in TOOL_FUNCTIONS:
        return f"Error: Unknown tool: {name}"
    
    try:
        result = TOOL_FUNCTIONS[name](**args)
        return result
    except Exception as e:
        return f"Error executing tool: {e}"


def run_agentic_loop(question: str, settings: AgentSettings) -> tuple[str, str, list[dict]]:
    """
    Run the agentic loop to answer a question using tools.
    
    Args:
        question: User's question
        settings: Agent settings
        
    Returns:
        Tuple of (answer, source, tool_calls_list)
    """
    # Initialize message history
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    
    tool_calls_log = []
    max_tool_calls = 10
    
    for iteration in range(max_tool_calls):
        print(f"\n--- Iteration {iteration + 1} ---", file=sys.stderr)
        
        # Call LLM
        response = call_llm(messages, tools=TOOLS, settings=settings)
        
        # Check for tool calls
        if response["tool_calls"]:
            for tool_call in response["tool_calls"]:
                # Execute the tool
                result = execute_tool(tool_call)
                
                # Log the tool call
                tool_call_entry = {
                    "tool": tool_call["function"]["name"],
                    "args": json.loads(tool_call["function"]["arguments"]),
                    "result": result,
                }
                tool_calls_log.append(tool_call_entry)
                
                # Append tool result to message history
                # Format tool result as a simple message for compatibility
                messages.append({
                    "role": "user",
                    "content": f"[Tool result from {tool_call['function']['name']}]: {result}",
                })
        else:
            # No tool calls - we have the final answer
            answer = response["content"]
            
            # Extract source from answer (look for wiki/... pattern)
            source = ""
            import re
            source_match = re.search(r'(wiki/[\w\-/]+\.md(?:#[\w\-]+)?)', answer)
            if source_match:
                source = source_match.group(1)
            
            return answer, source, tool_calls_log
    
    # Hit max tool calls - return whatever we have
    print("Warning: Hit maximum tool calls limit", file=sys.stderr)
    return "I couldn't find a complete answer within the tool call limit.", "", tool_calls_log


def main() -> None:
    """Main entry point."""
    # Parse command-line arguments
    if len(sys.argv) != 2:
        print("Usage: uv run agent.py \"Your question here\"", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    # Load settings
    settings = load_settings()
    print(f"Using model: {settings.llm_model}", file=sys.stderr)

    # Run agentic loop
    answer, source, tool_calls = run_agentic_loop(question, settings)
    
    print(f"\nReceived answer from LLM", file=sys.stderr)

    # Output JSON to stdout
    result = {
        "answer": answer,
        "source": source,
        "tool_calls": tool_calls,
    }

    # Output only valid JSON to stdout
    print(json.dumps(result))


if __name__ == "__main__":
    main()
