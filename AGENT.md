# Agent Architecture

## Overview

This agent is a CLI tool that connects to an LLM (Qwen Code API) with tools to navigate the project wiki. It implements an agentic loop that allows the LLM to call tools (`read_file`, `list_files`) to find answers in the documentation.

## Architecture

```
User question → LLM + tool schemas → tool call? → execute tool → append result → back to LLM
                                         │
                                         no
                                         │
                                         ▼
                                    JSON output with answer + source
```

## Components

### 1. Settings (`AgentSettings`)

Loads configuration from `.env.agent.secret` using `pydantic-settings`:

- `LLM_API_KEY` — API key for authentication
- `LLM_API_BASE` — Base URL of the LLM endpoint
- `LLM_MODEL` — Model name to use

### 2. Tools

Two tools are available to the LLM:

#### `read_file`
Reads a file from the project repository.

- **Parameters:** `path` (string) — relative path from project root
- **Returns:** File contents as string, or error message
- **Security:** Validates path doesn't escape project directory

#### `list_files`
Lists files and directories at a given path.

- **Parameters:** `path` (string) — relative directory path from project root
- **Returns:** Newline-separated listing of entries, or error message
- **Security:** Validates path doesn't escape project directory

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
    # ... list_files
]
```

### 4. Agentic Loop (`run_agentic_loop`)

The core loop that enables tool use:

1. **Send question + tool definitions** to LLM
2. **Parse response:**
   - If `tool_calls` present → execute each tool, append results as `tool` role messages, repeat
   - If text message (no tool calls) → extract answer and source, return
3. **Maximum 10 tool calls** per question (safety limit)

### 5. Message History

Conversation history is maintained throughout the loop:

```python
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": question},
    # After tool call:
    {"role": "tool", "content": result, "tool_call_id": "..."},
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

The system prompt guides the LLM to:

1. Use `list_files` to discover wiki files
2. Use `read_file` to read relevant file contents
3. Find the specific section that answers the question
4. Include a source reference in the format `wiki/filename.md#section-anchor`
5. Be concise and accurate

```python
SYSTEM_PROMPT = """You are a helpful documentation assistant. You have access to tools...

When answering questions:
1. Use `list_files` to discover what files exist in the wiki
2. Use `read_file` to read the contents of relevant files
3. Find the specific section that answers the question
4. Include a source reference in your answer using the format: `wiki/filename.md#section-anchor`
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
  "source": "wiki/filename.md#section-anchor",
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
- `source`: The wiki section reference (extracted from answer using regex)
- `tool_calls`: Array of all tool calls made, each with `tool`, `args`, and `result`

**Important:** Only valid JSON goes to stdout. All debug/progress output goes to stderr.

## Configuration

Create `.env.agent.secret` from `.env.agent.example`:

```bash
cp .env.agent.example .env.agent.secret
```

Fill in your credentials:

```env
LLM_API_KEY=your-api-key-here
LLM_API_BASE=http://<vm-ip>:<port>/v1
LLM_MODEL=qwen3-coder-plus
```

## Error Handling

- Missing settings file → exit code 1 with error message to stderr
- HTTP errors → raised as exceptions with details to stderr
- Invalid LLM response format → exit code 1 with parsing error to stderr
- Timeout (>60s) → httpx timeout exception
- Path traversal attempt → error message returned as tool result
- Max tool calls (10) reached → warning to stderr, partial answer returned

## Dependencies

- `httpx` — HTTP client for API requests
- `pydantic-settings` — Environment variable parsing
- Standard library: `json`, `os`, `sys`, `pathlib`, `re`
