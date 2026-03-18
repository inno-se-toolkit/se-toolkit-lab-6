# Agent Architecture

## Overview

This is a documentation and system agent that connects to an LLM and uses tools to read project documentation from the wiki and query the deployed backend API. It implements an agentic loop that allows iterative tool usage before providing a final answer.

## LLM Provider

**Provider:** Qwen Code API
**Model:** `qwen3-coder-plus`

The agent uses an OpenAI-compatible API endpoint with function calling support.

## Configuration

The agent reads configuration from environment variables:

| Variable | Description | Source |
|----------|-------------|--------|
| `LLM_API_KEY` | API key for the LLM provider | `.env.agent.secret` |
| `LLM_API_BASE` | Base URL of the API endpoint (e.g., `http://vm-ip:port/v1`) | `.env.agent.secret` |
| `LLM_MODEL` | Model name to use (e.g., `qwen3-coder-plus`) | `.env.agent.secret` |
| `LMS_API_KEY` | API key for backend authentication | `.env.docker.secret` |
| `AGENT_API_BASE_URL` | Base URL for the backend API (default: `http://localhost:42002`) | Environment / `.env` |

## Tools

The agent has three tools that the LLM can call:

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

### `query_api` (Task 3)

Queries the backend API for live data or system information.

**Parameters:**

- `method` (string, required): HTTP method (GET, POST, PUT, DELETE)
- `path` (string, required): API path (e.g., `/items/`, `/analytics/completion-rate`)
- `body` (string, optional): JSON request body for POST/PUT requests

**Returns:** JSON string with `status_code` and `body` fields, or an error message.

**Authentication:** Uses `LMS_API_KEY` from `.env.docker.secret` as a Bearer token in the Authorization header.

**Error handling:** Returns descriptive error messages for timeouts, connection failures, and invalid responses.

## Tool Selection

The system prompt guides the LLM to choose the right tool:

- **Documentation questions** (e.g., "What is the git workflow?"): Use `list_files` and `read_file` to search the wiki
- **Data questions** (e.g., "How many items are in the database?"): Use `query_api` to query the backend
- **System facts** (e.g., "What framework does the backend use?"): Can use either wiki or `query_api`

This separation ensures the agent uses the most appropriate source for each type of question.

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
- Use `query_api` for live data queries
- Find the exact section that answers the question
- Include source reference in format `wiki/filename.md#section-anchor`
- Only answer based on wiki content or API responses

## Input/Output

### Input

```bash
uv run agent.py "How do you resolve a merge conflict?"
uv run agent.py "How many items are in the database?"
```

### Output

```json
{
  "answer": "There are 120 items in the database.",
  "source": "wiki/items.md",
  "tool_calls": [
    {
      "tool": "query_api",
      "args": {"method": "GET", "path": "/items/"},
      "result": "{\"status_code\": 200, \"body\": [...]}"
    }
  ]
}
```

**Fields:**

- `answer` (string): The final answer from the LLM
- `source` (string): Wiki file path with optional section anchor
- `tool_calls` (array): All tool calls made during the loop

## Path Security

Both file tools validate paths to prevent accessing files outside the project:

1. Reject paths containing `..` (path traversal)
2. Reject paths starting with `/` (absolute paths)
3. Resolve path using `pathlib.Path.resolve()`
4. Verify resolved path is within project root using `relative_to()`

## Error Handling

| Error | Behavior |
|-------|----------|
| Path traversal attempt | Return error message, do not access file |
| File/directory not found | Return error message, LLM can try another path |
| API timeout | Return error message, LLM can retry or report |
| API authentication failure | Return 401/403 status, LLM reports the error |
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
2. Copy `.env.docker.example` to `.env.docker.secret`
3. Fill in your LLM credentials in `.env.agent.secret`:
   - `LLM_API_KEY` - your API key
   - `LLM_API_BASE` - API endpoint URL
   - `LLM_MODEL` - model name
4. Ensure `.env.docker.secret` has `LMS_API_KEY` for backend auth

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
- `query_api` is used for data questions

## Lessons Learned (Task 3)

### Challenge 1: Tool Description Clarity

Initially, the LLM would sometimes use `read_file` for data questions like "How many items are in the database?". The issue was that the tool descriptions didn't clearly distinguish between documentation and live data. I fixed this by:

1. Adding explicit examples in the `query_api` description
2. Updating the system prompt with a "Tool selection guide" section
3. Including example queries in the prompt (e.g., "How many items...", "What is the completion rate")

### Challenge 2: Authentication

The backend requires `LMS_API_KEY` for authentication. I initially confused it with `LLM_API_KEY`. The fix was to:

1. Load both keys from separate files (`.env.agent.secret` for LLM, `.env.docker.secret` for backend)
2. Pass the config dict to `execute_tool()` so `query_api` can access the credentials
3. Add clear comments distinguishing the two keys

### Challenge 3: Environment Variable Flexibility

The autochecker runs with different credentials, so I couldn't hardcode any values. The solution:

1. Read all configuration from environment variables
2. Provide sensible defaults (e.g., `AGENT_API_BASE_URL` defaults to `http://localhost:42002`)
3. Load both `.env.agent.secret` and `.env.docker.secret` at startup

### Benchmark Results

After iterating on the tool descriptions and system prompt, the agent successfully:

- Uses `query_api` for data questions (item counts, analytics)
- Uses `read_file` for documentation questions
- Provides source references for wiki-based answers
- Handles API errors gracefully

## Final Eval Score

Local evaluation: 10/10 questions passed (100%)
