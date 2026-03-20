#!/usr/bin/env python3
"""Agent CLI — answers questions using an LLM with tools.

Usage:
    uv run agent.py "How do you resolve a merge conflict?"

Output (JSON to stdout):
    {
      "answer": "...",
      "source": "wiki/git-workflow.md#resolving-merge-conflicts",
      "tool_calls": [...]
    }

All debug output goes to stderr.
"""

import json
import os
import re
import sys
from pathlib import Path

import httpx

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Load environment variables from .env.agent.secret
env_file = Path(__file__).parent / ".env.agent.secret"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

LLM_API_KEY = os.environ.get("LLM_API_KEY")
LLM_API_BASE = os.environ.get("LLM_API_BASE")
LLM_MODEL = os.environ.get("LLM_MODEL")

# Project root directory
PROJECT_ROOT = Path(__file__).parent.resolve()

# Maximum tool calls per question
MAX_TOOL_CALLS = 10

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


def read_file(path: str) -> str:
    """Read a file from the project repository.

    Args:
        path: Relative path from project root.

    Returns:
        File contents as string, or error message.
    """
    # Security: validate path
    if ".." in path:
        return "Error: Path traversal not allowed"

    if path.startswith("/"):
        return "Error: Absolute paths not allowed"

    # Resolve to absolute path
    try:
        full_path = (PROJECT_ROOT / path).resolve()
    except Exception as e:
        return f"Error: Invalid path: {e}"

    # Security: ensure path is within project root
    try:
        full_path.relative_to(PROJECT_ROOT)
    except ValueError:
        return "Error: Path outside project directory"

    # Read file
    try:
        content = full_path.read_text(encoding="utf-8")
        return content
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except Exception as e:
        return f"Error: {e}"


def list_files(path: str) -> str:
    """List files and directories at a given path.

    Args:
        path: Relative directory path from project root.

    Returns:
        Newline-separated list of entries, or error message.
    """
    # Security: validate path
    if ".." in path:
        return "Error: Path traversal not allowed"

    if path.startswith("/"):
        return "Error: Absolute paths not allowed"

    # Resolve to absolute path
    try:
        full_path = (PROJECT_ROOT / path).resolve()
    except Exception as e:
        return f"Error: Invalid path: {e}"

    # Security: ensure path is within project root
    try:
        full_path.relative_to(PROJECT_ROOT)
    except ValueError:
        return "Error: Path outside project directory"

    # Check if directory exists
    if not full_path.exists():
        return f"Error: Directory not found: {path}"

    if not full_path.is_dir():
        return f"Error: Not a directory: {path}"

    # List entries
    try:
        entries = [e.name for e in full_path.iterdir()]
        return "\n".join(sorted(entries))
    except Exception as e:
        return f"Error: {e}"


# Tool functions mapping
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "list_files": list_files,
}

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a documentation assistant for a software engineering toolkit project.

You have access to two tools. To use them, include this format in your response:

TOOL_CALL: tool_name({"arg": "value"})

Available tools:
1. list_files({"path": "directory"}) - List files in a directory
2. read_file({"path": "file"}) - Read contents of a file

To answer questions about the project:
1. First use list_files to discover relevant files (e.g., in the 'wiki' directory)
2. Then use read_file to read content from relevant files
3. Find the answer in the file contents
4. Include the source reference (file path and section anchor if applicable)

When providing answers:
- Be concise and accurate
- Always include the source field with the file path
- If the answer is in a specific section, include the section anchor (e.g., wiki/git-workflow.md#resolving-merge-conflicts)
- If you cannot find the answer, say so honestly

Important: Only access files within the project directory. Do not attempt to read files outside the project.

After receiving tool results, continue reasoning and either call more tools or provide the final answer."""


# ---------------------------------------------------------------------------
# Agentic loop
# ---------------------------------------------------------------------------


def execute_tool(tool_name: str, args: dict) -> str:
    """Execute a tool and return the result."""
    print(f"Executing tool: {tool_name}({args})", file=sys.stderr)

    if tool_name not in TOOL_FUNCTIONS:
        return f"Error: Unknown tool: {tool_name}"

    try:
        func = TOOL_FUNCTIONS[tool_name]
        result = func(**args)
        if len(result) > 500:
            print(f"Tool result: {result[:500]}... (truncated)", file=sys.stderr)
        else:
            print(f"Tool result: {result}", file=sys.stderr)
        return result
    except Exception as e:
        return f"Error executing {tool_name}: {e}"


def parse_tool_calls(text: str) -> list:
    """Parse tool calls from LLM response text."""
    tool_calls = []
    # Match TOOL_CALL: tool_name({...})
    pattern = r'TOOL_CALL:\s*(\w+)\((\{[^}]+\})\)'
    matches = re.findall(pattern, text)
    for tool_name, args_str in matches:
        try:
            args = json.loads(args_str)
            tool_calls.append({"tool": tool_name, "args": args})
        except json.JSONDecodeError:
            print(f"Failed to parse args: {args_str}", file=sys.stderr)
    return tool_calls


def run_agent(question: str) -> dict:
    """Run the agentic loop and return the result."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    tool_calls_log = []
    url = f"{LLM_API_BASE}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}",
    }

    for iteration in range(MAX_TOOL_CALLS):
        print(f"\n--- Iteration {iteration + 1} ---", file=sys.stderr)

        # Build request
        payload = {
            "model": LLM_MODEL,
            "messages": messages,
        }

        # Send request
        print(f"POST {url}", file=sys.stderr)
        response = httpx.post(url, headers=headers, json=payload, timeout=60.0)
        response.raise_for_status()

        # Parse response
        data = response.json()
        choice = data["choices"][0]
        message = choice["message"]
        content = message.get("content", "")

        print(f"LLM response: {content[:300]}...", file=sys.stderr)

        # Parse tool calls from text
        tool_calls = parse_tool_calls(content)

        if tool_calls:
            # Execute tools
            for tc in tool_calls:
                tool_name = tc["tool"]
                args = tc["args"]

                result = execute_tool(tool_name, args)

                # Log tool call
                tool_calls_log.append({
                    "tool": tool_name,
                    "args": args,
                    "result": result,
                })

                # Append tool result to messages
                messages.append({
                    "role": "user",
                    "content": f"TOOL_RESULT: {tool_name}({args}) = {result}",
                })

            # Continue loop
            continue
        else:
            # No tool calls - final answer
            answer = content
            print(f"Final answer: {answer[:300]}...", file=sys.stderr)

            # Extract source from answer
            source = ""
            wiki_refs = re.findall(r'wiki/[\w\-/]+\.md(?:#[\w\-]+)?', answer)
            if wiki_refs:
                source = wiki_refs[0]
            else:
                file_refs = re.findall(r'[\w\-/]+\.md(?:#[\w\-]+)?', answer)
                if file_refs:
                    source = file_refs[0]

            return {
                "answer": answer,
                "source": source,
                "tool_calls": tool_calls_log,
            }

    # Max iterations reached
    print("Max tool calls reached, returning partial answer", file=sys.stderr)
    return {
        "answer": "Reached maximum tool calls limit.",
        "source": "",
        "tool_calls": tool_calls_log,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    # Validate arguments
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py <question>", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    # Validate environment
    if not LLM_API_KEY:
        print("Error: LLM_API_KEY not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    if not LLM_API_BASE:
        print("Error: LLM_API_BASE not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    if not LLM_MODEL:
        print("Error: LLM_MODEL not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)

    print(f"Question: {question}", file=sys.stderr)

    try:
        # Run agent
        result = run_agent(question)

        # Output JSON
        print(json.dumps(result))

        print("Done", file=sys.stderr)
        sys.exit(0)

    except httpx.TimeoutException as e:
        print(f"Error: Request timed out: {e}", file=sys.stderr)
        result = {"answer": "Request timed out.", "source": "", "tool_calls": []}
        print(json.dumps(result))
        sys.exit(1)
    except httpx.HTTPError as e:
        print(f"Error: HTTP request failed: {e}", file=sys.stderr)
        result = {"answer": f"API error: {e}", "source": "", "tool_calls": []}
        print(json.dumps(result))
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        result = {"answer": f"Error: {e}", "source": "", "tool_calls": []}
        print(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
