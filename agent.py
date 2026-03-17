#!/usr/bin/env python3
"""
Agent module for interacting with LLM.

Usage:
    uv run agent.py "Your question here"

Output:
    JSON to stdout: {"answer": "...", "source": "...", "tool_calls": [...]}
    Debug logs go to stderr.
"""

import os
import sys
import json
import httpx
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI


# Maximum number of tool calls per question
MAX_TOOL_CALLS = 15

# System prompt for the documentation agent
SYSTEM_PROMPT = """You are a documentation assistant for a software engineering lab.
You have access to tools to read files, list directories, and query the backend API.

When answering questions:
1. Use list_files to discover what files exist in a directory
2. Use read_file to read source code or documentation files
3. Use query_api to query the running backend API for:
   - Data counts (e.g., "how many items")
   - Live analytics (e.g., completion rates, top learners)
   - Testing endpoint behavior (e.g., status codes, error responses)
   - Debugging API errors

Tool selection guide:
- For static questions about the codebase (framework, ports, structure), use read_file on source code
- For data-dependent questions (counts, scores, live data), use query_api with auth=true (default)
- For wiki/documentation questions, use list_files and read_file on wiki/
- To test unauthenticated access (e.g., "what status code without auth?"), use query_api with auth=false

DEBUGGING TIP: When an API endpoint returns an error:
- If you get 422 (missing parameter), try again with the required parameter (e.g., ?lab=lab-01)
- If you get 500 (server error), read the error message and traceback, then read the source code to find the bug
- For analytics endpoints, always try with a lab parameter like ?lab=lab-01 or ?lab=lab-99

IMPORTANT: All paths must be relative to the project root. For example:
- To list backend app files: use list_files("backend/app")
- To read a router: use read_file("backend/app/routers/items.py")
- To list wiki files: use list_files("wiki")

Always use tools to find accurate information. Do not make assumptions about file contents.

SOURCE REFERENCE: At the end of your answer, always include a "Source:" line with the file path(s) you used:
- For wiki files: Source: wiki/filename.md#section
- For source files: Source: backend/app/routers/items.py
- For API queries: Source: query_api GET /path

This is REQUIRED - always include at least one source reference.

RESPONSE FORMAT: Your final answer must be complete and self-contained. When asked to list multiple items (like router modules), read all relevant files and provide a comprehensive summary. Never say "let me check" or "I'll continue" - gather all information first, then provide the complete answer.

For bug diagnosis questions: Always identify the specific error type (e.g., TypeError, ZeroDivisionError), the line or operation causing it, and explain why it happens in the code.
"""


class Agent:
    """A simple agent that calls an LLM and returns structured JSON responses."""

    def __init__(self):
        """
        Initialize the agent with configuration from environment variables.

        Reads from .env.agent.secret:
            - LLM_API_KEY: API key for authentication
            - LLM_API_BASE: Base URL for the LLM API (OpenAI-compatible)
            - LLM_MODEL: Model name to use

        Reads from .env.docker.secret:
            - LMS_API_KEY: Backend API key for query_api authentication

        Optional:
            - AGENT_API_BASE_URL: Base URL for backend API (default: http://localhost:42002)
        """
        # Load environment variables from both files
        load_dotenv(".env.agent.secret")
        load_dotenv(".env.docker.secret")

        # Get LLM configuration from environment
        api_key = os.getenv("LLM_API_KEY")
        api_base = os.getenv("LLM_API_BASE")
        model = os.getenv("LLM_MODEL")

        # Get backend API configuration
        self.lms_api_key = os.getenv("LMS_API_KEY")
        self.agent_api_base_url = os.getenv(
            "AGENT_API_BASE_URL", "http://localhost:42002"
        )

        # Validate required configuration
        if not api_key:
            raise ValueError(
                "LLM_API_KEY not found. Please set it in .env.agent.secret file."
            )
        if not api_base:
            raise ValueError(
                "LLM_API_BASE not found. Please set it in .env.agent.secret file."
            )
        if not model:
            raise ValueError(
                "LLM_MODEL not found. Please set it in .env.agent.secret file."
            )

        # Store configuration
        self.api_key = api_key
        self.api_base = api_base
        self.model = model

        # Project root for path security
        self.project_root = Path(__file__).parent.resolve()

        # Initialize OpenAI client with custom base URL
        # This allows using any OpenAI-compatible API (Qwen Code API, OpenRouter, etc.)
        self.client = OpenAI(api_key=self.api_key, base_url=self.api_base)

        # Track tool calls for output
        self.tool_calls_log: list[dict] = []

        print(f"Agent initialized with model: {self.model}", file=sys.stderr)

    def _get_tool_schemas(self) -> list[dict]:
        """
        Return the tool schemas for function calling.

        Returns:
            List of tool schema dictionaries
        """
        return [
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
                    "description": "List files and directories at a given path in the project",
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
            },
            {
                "type": "function",
                "function": {
                    "name": "query_api",
                    "description": "Query the backend API. Use for data-dependent questions like item counts, analytics, or testing endpoints. Set auth=false to test unauthenticated access.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "method": {
                                "type": "string",
                                "description": "HTTP method (GET, POST, PUT, DELETE, etc.)"
                            },
                            "path": {
                                "type": "string",
                                "description": "API path (e.g., '/items/', '/analytics/completion-rate')"
                            },
                            "body": {
                                "type": "string",
                                "description": "Optional JSON request body for POST/PUT requests"
                            },
                            "auth": {
                                "type": "boolean",
                                "description": "Whether to include authentication header (default: true). Set to false to test unauthenticated access."
                            }
                        },
                        "required": ["method", "path"]
                    }
                }
            }
        ]

    def _validate_path(self, requested_path: str) -> tuple[bool, str]:
        """
        Validate that a path is safe and within the project directory.

        Args:
            requested_path: The path to validate

        Returns:
            Tuple of (is_valid, error_message_or_resolved_path)
        """
        # Reject paths with directory traversal
        if ".." in requested_path:
            return False, "Path traversal not allowed"

        # Reject absolute paths
        if requested_path.startswith("/"):
            return False, "Absolute paths not allowed"

        # Resolve the full path
        resolved = (self.project_root / requested_path).resolve()

        # Check if resolved path is within project root
        try:
            resolved.relative_to(self.project_root)
        except ValueError:
            return False, "Path escapes project directory"

        return True, str(resolved)

    def read_file(self, path: str) -> str:
        """
        Read a file from the project repository.

        Args:
            path: Relative path from project root

        Returns:
            File contents as string, or error message
        """
        print(f"Tool call: read_file({path})", file=sys.stderr)

        # Validate path
        is_valid, result = self._validate_path(path)
        if not is_valid:
            return f"Error: {result}"

        file_path = Path(result)

        # Check if file exists
        if not file_path.exists():
            return f"Error: File not found: {path}"

        # Check if it's a file (not a directory)
        if not file_path.is_file():
            return f"Error: Not a file: {path}"

        # Read and return contents
        try:
            content = file_path.read_text(encoding="utf-8")
            print(f"Read {len(content)} bytes from {path}", file=sys.stderr)
            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def list_files(self, path: str) -> str:
        """
        List files and directories at a given path.

        Args:
            path: Relative directory path from project root

        Returns:
            Newline-separated list of entries, or error message
        """
        print(f"Tool call: list_files({path})", file=sys.stderr)

        # Validate path
        is_valid, result = self._validate_path(path)
        if not is_valid:
            return f"Error: {result}"

        dir_path = Path(result)

        # Check if directory exists
        if not dir_path.exists():
            return f"Error: Directory not found: {path}"

        # Check if it's a directory
        if not dir_path.is_dir():
            return f"Error: Not a directory: {path}"

        # List entries
        try:
            entries = []
            for entry in sorted(dir_path.iterdir()):
                # Skip hidden files and __pycache__
                if entry.name.startswith(".") and entry.name != ".qwen":
                    continue
                if entry.name == "__pycache__":
                    continue
                # Add indicator for directories
                if entry.is_dir():
                    entries.append(f"{entry.name}/")
                else:
                    entries.append(entry.name)
            result_str = "\n".join(entries)
            print(f"Listed {len(entries)} entries in {path}", file=sys.stderr)
            return result_str
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    def query_api(self, method: str, path: str, body: str | None = None, auth: bool = True) -> str:
        """
        Query the backend API with optional LMS_API_KEY authentication.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: API path (e.g., '/items/', '/analytics/completion-rate')
            body: Optional JSON request body for POST/PUT requests
            auth: Whether to include authentication header (default: True)

        Returns:
            JSON string with status_code and body, or error message
        """
        print(f"Tool call: query_api({method} {path}, auth={auth})", file=sys.stderr)

        # Build the URL
        url = f"{self.agent_api_base_url}{path}"

        # Prepare headers
        headers = {
            "Content-Type": "application/json",
        }
        
        # Add authentication if requested
        if auth and self.lms_api_key:
            headers["Authorization"] = f"Bearer {self.lms_api_key}"
        elif auth and not self.lms_api_key:
            return "Error: LMS_API_KEY not configured"

        try:
            # Make the request
            with httpx.Client() as client:
                if method.upper() == "GET":
                    response = client.get(url, headers=headers, timeout=30.0)
                elif method.upper() == "POST":
                    response = client.post(
                        url, headers=headers, json=json.loads(body) if body else None, timeout=30.0
                    )
                elif method.upper() == "PUT":
                    response = client.put(
                        url, headers=headers, json=json.loads(body) if body else None, timeout=30.0
                    )
                elif method.upper() == "DELETE":
                    response = client.delete(url, headers=headers, timeout=30.0)
                else:
                    return f"Error: Unsupported method: {method}"

            # Build result
            result = {
                "status_code": response.status_code,
                "body": response.text,
            }
            result_str = json.dumps(result)
            print(f"API returned status {response.status_code}", file=sys.stderr)
            return result_str

        except httpx.RequestError as e:
            return f"Error: Request failed - {str(e)}"
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON body - {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"

    def execute_tool(self, tool_name: str, args: dict) -> str:
        """
        Execute a tool with the given arguments.

        Args:
            tool_name: Name of the tool to execute
            args: Arguments for the tool

        Returns:
            Tool result as string
        """
        if tool_name == "read_file":
            return self.read_file(args.get("path", ""))
        elif tool_name == "list_files":
            return self.list_files(args.get("path", ""))
        elif tool_name == "query_api":
            return self.query_api(
                args.get("method", "GET"),
                args.get("path", ""),
                args.get("body"),
                args.get("auth", True)  # Default to authenticated
            )
        else:
            return f"Error: Unknown tool: {tool_name}"

    def call_llm(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """
        Call the LLM with messages and optional tools.

        Args:
            messages: List of message dictionaries
            tools: Optional list of tool schemas

        Returns:
            Response dictionary with choices
        """
        print(f"Calling LLM with {len(messages)} messages", file=sys.stderr)

        request_kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        if tools:
            request_kwargs["tools"] = tools

        response = self.client.chat.completions.create(**request_kwargs)  # type: ignore[arg-type]

        return response  # type: ignore[return-value]

    def run(self, question: str) -> dict:
        """
        Run the agentic loop to answer a question.

        Args:
            question: The user's question

        Returns:
            Dictionary with answer, source, and tool_calls
        """
        # Initialize messages with system prompt and user question
        messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]

        # Get tool schemas
        tool_schemas = self._get_tool_schemas()

        # Track tool calls for output
        self.tool_calls_log = []

        # Agentic loop
        iteration = 0
        while iteration < MAX_TOOL_CALLS:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---", file=sys.stderr)

            # Call LLM with tools
            response = self.call_llm(messages, tools=tool_schemas)

            # Get the first choice
            choice = response.choices[0]
            message = choice.message

            # Check for tool calls
            if hasattr(message, "tool_calls") and message.tool_calls:
                print(f"LLM returned {len(message.tool_calls)} tool call(s)", file=sys.stderr)

                # Add assistant message with tool calls to conversation
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": message.tool_calls
                })

                # Execute each tool call
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    # Parse arguments as JSON
                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        tool_args = {}

                    # Execute the tool
                    result = self.execute_tool(tool_name, tool_args)

                    # Log the tool call for output
                    self.tool_calls_log.append({
                        "tool": tool_name,
                        "args": tool_args,
                        "result": result
                    })

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })

                    print(f"Tool {tool_name} completed", file=sys.stderr)

                # Continue loop to get next LLM response
                continue

            # No tool calls - we have the final answer
            answer = message.content or ""
            print(f"LLM returned final answer", file=sys.stderr)

            # Extract source from answer (look for markdown links or references)
            source = self._extract_source(answer)

            return {
                "answer": answer,
                "source": source,
                "tool_calls": self.tool_calls_log
            }

        # Max iterations reached
        print(f"Max tool calls ({MAX_TOOL_CALLS}) reached", file=sys.stderr)

        # Try to get whatever answer we have
        # Call LLM one more time without tools to get a summary
        messages.append({
            "role": "user",
            "content": "Please provide your best answer based on the information gathered so far."
        })

        response = self.call_llm(messages, tools=None)
        answer = response.choices[0].message.content or ""
        source = self._extract_source(answer)

        return {
            "answer": answer,
            "source": source,
            "tool_calls": self.tool_calls_log
        }

    def _extract_source(self, answer: str) -> str:
        """
        Extract source reference from the answer.

        Looks for patterns like:
        - wiki/filename.md#section
        - (wiki/filename.md#section)
        - Source: wiki/filename.md#section
        - Source: backend/app/routers/items.py
        - Source: query_api GET /path

        Args:
            answer: The LLM's answer text

        Returns:
            Source string or empty string if not found
        """
        import re

        # Pattern to match wiki file references with anchors
        patterns = [
            r"wiki/[\w-]+\.md#[\w-]+",
            r"\(wiki/[\w-]+\.md#[\w-]+\)",
            r"Source:\s*(wiki/[\w-]+\.md#[\w-]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, answer)
            if match:
                source = match.group(0)
                # Remove parentheses if present
                source = source.strip("()")
                return source

        # If no source found, try to find any wiki file reference
        wiki_file_pattern = r"wiki/[\w-]+\.md"
        match = re.search(wiki_file_pattern, answer)
        if match:
            return match.group(0)

        # Try to find backend source file references
        backend_pattern = r"backend/[\w/.-]+"
        match = re.search(backend_pattern, answer)
        if match:
            source = match.group(0)
            # Clean up trailing punctuation
            source = source.rstrip(".,;:")
            return source

        # Try to find query_api source references
        api_pattern = r"Source:\s*query_api\s+(GET|POST|PUT|DELETE)\s+[\w/.-]+"
        match = re.search(api_pattern, answer)
        if match:
            return match.group(0).replace("Source: ", "")

        return ""

    def format_response(self, answer: str, source: str, tool_calls: list[dict]) -> str:
        """
        Format the response as JSON.

        Args:
            answer: The LLM's text answer
            source: The source reference
            tool_calls: List of tool call records

        Returns:
            JSON string
        """
        response = {
            "answer": answer,
            "source": source,
            "tool_calls": tool_calls
        }
        return json.dumps(response, ensure_ascii=False, indent=2)


def main():
    """Main entry point for the agent CLI."""
    # Get prompt from command line arguments
    if len(sys.argv) < 2:
        print("Error: Please provide a prompt", file=sys.stderr)
        print('Usage: uv run agent.py "your prompt here"', file=sys.stderr)
        sys.exit(1)

    prompt = sys.argv[1]

    try:
        # Create agent and run
        agent = Agent()
        result = agent.run(prompt)
        formatted_response = agent.format_response(
            result["answer"],
            result["source"],
            result["tool_calls"]
        )

        # Output JSON to stdout (only valid JSON, no debug info)
        print(formatted_response)

        sys.exit(0)

    except Exception as e:
        # Log error to stderr
        print(f"Error: {str(e)}", file=sys.stderr)

        # Still output valid JSON structure for consistency
        error_response = {
            "answer": f"Error: {str(e)}",
            "source": "",
            "tool_calls": []
        }
        print(json.dumps(error_response))
        sys.exit(1)


if __name__ == "__main__":
    main()
