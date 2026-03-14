# Agent Architecture

## Overview

This agent is a CLI tool that connects to an LLM (Qwen Code API) with tools to navigate the project wiki and query the backend API. It implements an agentic loop that allows the LLM to call tools (`read_file`, `list_files`, `query_api`) to find answers in documentation, source code, and live system data.

## Architecture

```
User question → LLM + tool schemas → tool call? → execute tool → append result → back to LLM
                                         │
                                         no
                                         │
                                         ▼
                                    JSON output with answer + source + tool_calls
```

## Components

### 1. Settings (`AgentSettings`)

Loads configuration from `.env.agent.secret` and `.env.docker.secret` using `pydantic-settings`:

- `LLM_API_KEY` — API key for LLM authentication
- `LLM_API_BASE` — Base URL of the LLM endpoint
- `LLM_MODEL` — Model name to use
- `LMS_API_KEY` — Backend API key for `query_api` authentication (from `.env.docker.secret`)
- `AGENT_API_BASE_URL` — Base URL for backend API (default: `http://localhost:42002`)

### 2. Tools

Three tools are available to the LLM:

#### `read_file`
Reads a file from the project repository.

- **Parameters:** `path` (string) — relative path from project root
- **Returns:** File contents as string, or error message
- **Security:** Validates path doesn't escape project directory
- **Use cases:** Wiki documentation, source code analysis

#### `list_files`
Lists files and directories at a given path.

- **Parameters:** `path` (string) — relative directory path from project root
- **Returns:** Newline-separated listing of entries, or error message
- **Security:** Validates path doesn't escape project directory
- **Use cases:** Discovering available files, exploring directory structure

#### `query_api`
Sends HTTP requests to the backend API.

- **Parameters:** 
  - `method` (string) — HTTP method (GET, POST, PUT, DELETE)
  - `path` (string) — API endpoint path (e.g., `/items/`, `/analytics/completion-rate`)
  - `body` (string, optional) — JSON request body for POST/PUT requests
- **Returns:** JSON string with `status_code` and `body`
- **Authentication:** Uses `LMS_API_KEY` from environment, sent as `X-API-Key` header
- **Use cases:** Runtime data queries, status code checks, error diagnosis

### 3. Tool Schemas

Tools are defined as OpenAI-compatible function calling schemas:

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file...",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "..."}
                },
                "required": ["path"]
            }
        }
    },
    # ... list_files, query_api
]
```

### 4. Agentic Loop (`run_agentic_loop`)

The core loop that enables tool use:

1. **Send question + tool definitions** to LLM
2. **Parse response:**
   - If `tool_calls` present → execute each tool, append results as user messages, repeat
   - If text message (no tool calls) → extract answer and source, return
3. **Maximum 10 tool calls** per question (safety limit)

### 5. Message History

Conversation history is maintained throughout the loop:

```python
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": question},
    # After tool call:
    {"role": "user", "content": f"[Tool result from {tool_name}]: {result}"},
]
```

### 6. LLM Client (`call_llm`)

Makes HTTP POST requests to the OpenAI-compatible chat completions endpoint:

- **Endpoint:** `{LLM_API_BASE}/chat/completions`
- **Timeout:** 60 seconds
- **Request format:** Standard OpenAI chat completions API with optional `tools`
- **Response parsing:** Extracts `choices[0].message` with content and tool_calls

### 7. CLI Interface (`main`)

- Parses command-line arguments (question as first argument)
- Validates settings file exists
- Runs the agentic loop
- Outputs JSON to stdout, debug info to stderr

## System Prompt Strategy

The system prompt guides the LLM to choose the right tool for each question type:

1. **Wiki/documentation questions** ("according to the wiki", "what steps", "how to"):
   - Use `list_files` to discover wiki files
   - Use `read_file` to read relevant documentation
   - Include source reference: `wiki/filename.md#section-anchor`

2. **Source code questions** ("what framework", "what does this code do"):
   - Use `list_files` to explore backend directory
   - Use `read_file` to read source code (e.g., `backend/app/main.py`)
   - Look for imports, class definitions, function names
   - Include source reference: `backend/app/filename.py`

3. **Runtime data questions** ("how many items", "what status code"):
   - Use `query_api` to send HTTP requests to the backend
   - Specify correct HTTP method and path
   - Authentication handled automatically

4. **Multi-step questions** ("what error", "diagnose the bug"):
   - First use `query_api` to trigger and observe the error
   - Then use `read_file` to examine the relevant source code
   - Combine findings in the answer

```python
SYSTEM_PROMPT = """You are a helpful documentation and code assistant...

When answering questions:
1. For wiki/documentation questions: use list_files and read_file
2. For source code questions: read the actual source files
3. For runtime data questions: use query_api
4. For multi-step questions: chain tools together
...
"""
```

## Path Security

To prevent reading files outside the project directory:

```python
def validate_path(relative_path: str) -> Path:
    project_root = Path(__file__).parent.resolve()
    full_path = (project_root / relative_path).resolve()

    # Check for path traversal
    try:
        full_path.relative_to(project_root)
    except ValueError:
        raise ValueError(f"Path traversal not allowed: {relative_path}")

    return full_path
```

This ensures that even if the LLM tries to access `../../etc/passwd`, the path will be rejected.

## LLM Provider

**Provider:** Qwen Code API (via qwen-code-oai-proxy on VM)

**Model:** `qwen3-coder-plus`

**Why this choice:**
- 1000 free requests per day
- Available from Russia
- No credit card required
- OpenAI-compatible API

## Usage

```bash
# Basic usage
uv run agent.py "How do you resolve a merge conflict?"

# Output (stdout)
{
  "answer": "Edit the conflicting file, choose which changes to keep, then stage and commit.",
  "source": "wiki/git-workflow.md#resolving-merge-conflicts",
  "tool_calls": [
    {"tool": "list_files", "args": {"path": "wiki"}, "result": "git-workflow.md\n..."},
    {"tool": "read_file", "args": {"path": "wiki/git-workflow.md"}, "result": "..."}
  ]
}
```

## Output Format

The agent outputs a single JSON line to stdout:

```json
{
  "answer": "The LLM's response text",
  "source": "wiki/filename.md#section-anchor or backend/app/filename.py",
  "tool_calls": [
    {
      "tool": "read_file",
      "args": {"path": "wiki/filename.md"},
      "result": "..."
    }
  ]
}
```

- `answer`: The text response from the LLM
- `source`: The file reference (wiki or source code, extracted from answer using regex)
- `tool_calls`: Array of all tool calls made, each with `tool`, `args`, and `result`

**Important:** Only valid JSON goes to stdout. All debug/progress output goes to stderr.

## Configuration

Create `.env.agent.secret` from `.env.agent.example`:

```bash
cp .env.agent.example .env.agent.secret
```

Fill in your credentials:

```env
# LLM configuration
LLM_API_KEY=your-llm-api-key-here
LLM_API_BASE=http://<vm-ip>:<port>/v1
LLM_MODEL=qwen3-coder-plus

# Backend API configuration (from .env.docker.secret)
LMS_API_KEY=my-secret-api-key
AGENT_API_BASE_URL=http://localhost:42002
```

## Error Handling

- Missing settings file → exit code 1 with error message to stderr
- HTTP errors → raised as exceptions with details to stderr
- Invalid LLM response format → exit code 1 with parsing error to stderr
- Timeout (>60s) → httpx timeout exception
- Path traversal attempt → error message returned as tool result
- Max tool calls (10) reached → warning to stderr, partial answer returned
- API authentication failure → error message in tool result

## Dependencies

- `httpx` — HTTP client for API requests
- `pydantic-settings` — Environment variable parsing
- Standard library: `json`, `os`, `re`, `sys`, `pathlib`

## Lessons Learned

### Tool Selection

The system prompt is critical for correct tool selection. Initially, the agent would try to use `read_file` for all questions. After refining the prompt to explicitly describe when to use each tool, the agent correctly chooses:
- `read_file` for wiki and source code questions
- `query_api` for runtime data questions
- Both tools chained for bug diagnosis questions

### Source Extraction

The source extraction regex was extended to handle both wiki files (`wiki/*.md`) and source code files (`backend/app/*.py`). This allows the agent to provide accurate references for all question types.

### Authentication

The `query_api` tool automatically authenticates using `LMS_API_KEY` from environment. This is separate from the LLM API key — don't mix them up.

## Benchmark Results

The agent passes all 10 local evaluation questions:
- Wiki lookup questions (Class A)
- Static system facts (Class B)
- Data-dependent queries (Class C)
- Bug diagnosis chain (Class D)
- Open-ended reasoning (LLM judge)
