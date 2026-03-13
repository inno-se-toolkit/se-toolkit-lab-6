# Agent Architecture

## Overview

This is a documentation agent that connects to an LLM and uses tools to read project documentation from the wiki. It implements an agentic loop that allows iterative tool usage before providing a final answer.

## LLM Provider

**Provider:** Qwen Code API
**Model:** `qwen3-coder-plus`

The agent uses an OpenAI-compatible API endpoint with function calling support.

## Configuration

The agent reads configuration from `.env.agent.secret` in the project root:

| Variable | Description |
|----------|-------------|
| `LLM_API_KEY` | API key for the LLM provider |
| `LLM_API_BASE` | Base URL of the API endpoint (e.g., `http://vm-ip:port/v1`) |
| `LLM_MODEL` | Model name to use (e.g., `qwen3-coder-plus`) |

## Tools

The agent has two tools that the LLM can call:

### `read_file`

Reads a file from the project repository.

**Parameters:**
- `path` (string, required): Relative path from project root (e.g., `wiki/git-workflow.md`)

**Returns:** File contents as a string, or an error message.

**Security:** Rejects paths containing `..` or starting with `/` to prevent path traversal attacks.

### `list_files`

Lists files and directories at a given path.

**Parameters:**
- `path` (string, required): Relative directory path from project root (e.g., `wiki`)

**Returns:** Newline-separated list of entries, or an error message.

**Security:** Same path validation as `read_file`.

## Agentic Loop

The agent implements an iterative loop:

```
Question → LLM → tool_calls? → yes → execute tools → append results → back to LLM
                                      │
                                      no
                                      │
                                      ▼
                                 JSON output
```

**Algorithm:**
1. Initialize conversation with system prompt + user question
2. Loop (max 10 iterations):
   - Send conversation history to LLM with tool schemas
   - Parse LLM response for `tool_calls`
   - If tool calls present:
     - Execute each tool
     - Append results to conversation as `tool` role messages
     - Continue loop
   - If no tool calls (text response):
     - Extract answer and source
     - Return JSON and exit
3. If max iterations reached, return partial answer

## System Prompt

The system prompt instructs the LLM to:
- Use `list_files` to discover wiki files
- Use `read_file` to read relevant documentation
- Find the exact section that answers the question
- Include source reference in format `wiki/filename.md#section-anchor`
- Only answer based on wiki content

## Input/Output

### Input
```bash
uv run agent.py "How do you resolve a merge conflict?"
```

### Output
```json
{
  "answer": "Edit the conflicting file, choose which changes to keep, then stage and commit.",
  "source": "wiki/git-workflow.md#resolving-merge-conflicts",
  "tool_calls": [
    {
      "tool": "list_files",
      "args": {"path": "wiki"},
      "result": "git-workflow.md\n..."
    },
    {
      "tool": "read_file",
      "args": {"path": "wiki/git-workflow.md"},
      "result": "..."
    }
  ]
}
```

**Fields:**
- `answer` (string): The final answer from the LLM
- `source` (string): Wiki file path with optional section anchor
- `tool_calls` (array): All tool calls made during the loop

## Path Security

Both tools validate paths to prevent accessing files outside the project:

1. Reject paths containing `..` (path traversal)
2. Reject paths starting with `/` (absolute paths)
3. Resolve path using `pathlib.Path.resolve()`
4. Verify resolved path is within project root using `relative_to()`

## Error Handling

| Error | Behavior |
|-------|----------|
| Path traversal attempt | Return error message, do not access file |
| File/directory not found | Return error message, LLM can try another path |
| Invalid tool call | Log error to stderr, continue loop |
| Max iterations (10) reached | Return partial answer based on gathered information |
| API timeout | Exit 1 with error to stderr |
| Missing config | Exit 1 with error to stderr |

## Dependencies

- `httpx` - HTTP client for API calls
- `python-dotenv` - Environment variable loading
- `json` - JSON serialization (stdlib)
- `pathlib` - Path manipulation (stdlib)

## Usage

### Setup
1. Copy `.env.agent.example` to `.env.agent.secret`
2. Fill in your LLM credentials:
   - `LLM_API_KEY` - your API key
   - `LLM_API_BASE` - API endpoint URL
   - `LLM_MODEL` - model name

### Run
```bash
uv run agent.py "Your question here"
```

## Testing

Run the regression tests:
```bash
uv run pytest tests/test_agent.py -v
```

Tests verify:
- Agent outputs valid JSON
- `answer`, `source`, and `tool_calls` fields exist
- Tools are called when appropriate
