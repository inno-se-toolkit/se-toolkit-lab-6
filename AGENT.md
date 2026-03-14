# Agent

## Overview

`agent.py` is a CLI agent for a Learning Management Service project. It takes a natural-language question, uses tools to explore project documentation, read source code, and query the deployed backend API, then returns a structured JSON answer grounded in real data.

The agent uses an agentic loop: it sends the question to an LLM along with tool definitions, the LLM decides which tools to call, the agent executes them and feeds results back, and the loop continues until the LLM produces a final text answer or the tool call limit is reached.

## LLM provider

Qwen Code API (`qwen3-coder-plus`) accessed through an OpenAI-compatible chat completions endpoint, or any OpenAI-compatible provider (OpenAI, OpenRouter, etc.).

## Configuration

All configuration is read from environment variables. Two env files are used as local conveniences:

```bash
cp .env.agent.example .env.agent.secret
# Edit .env.agent.secret with LLM credentials

cp .env.docker.example .env.docker.secret
# Edit .env.docker.secret with backend API key
```

| Variable             | Purpose                                  | Source              |
| -------------------- | ---------------------------------------- | ------------------- |
| `LLM_API_KEY`        | LLM provider API key                     | `.env.agent.secret` |
| `LLM_API_BASE`       | LLM API endpoint URL                     | `.env.agent.secret` |
| `LLM_MODEL`          | Model name (default: `qwen3-coder-plus`) | `.env.agent.secret` |
| `LMS_API_KEY`        | Backend API key for `query_api` auth     | `.env.docker.secret` |
| `AGENT_API_BASE_URL` | Backend base URL (default: `http://localhost:42002`) | Environment |

## Usage

```bash
uv run agent.py "How many items are in the database?"
```

**Output** — a single JSON line to stdout:

```json
{
  "answer": "There are 120 items in the database.",
  "source": "",
  "tool_calls": [
    {"tool": "query_api", "args": {"method": "GET", "path": "/items/"}, "result": "..."}
  ]
}
```

## Tools

### `read_file`

Reads a file from the project repository. Takes a relative `path` from the project root. Returns file contents or an error message. Rejects paths that traverse outside the project directory using `os.path.realpath` validation.

### `list_files`

Lists files and directories at a given path. Takes a relative directory `path`. Returns a newline-separated listing. Rejects paths outside the project directory.

### `query_api`

Sends an HTTP request to the deployed backend API. Takes `method` (GET, POST, etc.), `path` (e.g., `/items/`), and an optional `body` (JSON string). Returns a JSON string with `status_code` and `body`. Authenticates using the `LMS_API_KEY` environment variable sent as an `X-API-Key` header. The base URL is read from `AGENT_API_BASE_URL` (defaults to `http://localhost:42002`).

## Agentic loop

1. Send the user's question and all tool definitions to the LLM.
2. If the LLM responds with `tool_calls` → execute each tool, append results as `tool` messages, loop back to step 1.
3. If the LLM responds with plain text (no tool calls) → that is the final answer. Output JSON and exit.
4. Maximum of 10 tool calls per question to prevent infinite loops.
5. The `content` field from the LLM is handled with `(msg.get("content") or "")` to gracefully handle `null` values that some providers return alongside tool calls.

## System prompt strategy

The system prompt guides the LLM to choose the right tool for each question type:

- **Wiki questions** → `list_files("wiki")` then `read_file` on the relevant wiki page
- **Source code questions** → `list_files` on backend directories, then `read_file` on source files
- **Data questions** → `query_api` with the appropriate endpoint
- **Bug diagnosis** → `query_api` to trigger the error, then `read_file` to find the buggy code
- **Architecture questions** → `read_file` on docker-compose.yml, Dockerfile, and backend source

The prompt also includes common API endpoints to help the LLM make correct tool calls on the first try.

## Lessons learned

- The LLM sometimes returns `content: null` (not missing, but explicitly null) when making tool calls. Using `msg.get("content", "")` still returns `None` in this case — must use `(msg.get("content") or "")` instead.
- Tool descriptions matter significantly for routing accuracy. Vague descriptions cause the LLM to pick the wrong tool. Including example paths in descriptions helps.
- The system prompt needs to be specific about when to use `query_api` vs `read_file` — without clear guidance, the LLM defaults to reading files even for data questions.
- For bug diagnosis questions, the system prompt must explicitly instruct the LLM to first query the API to see the error, then read the source code. Without this two-step guidance, the LLM tries to guess the bug from code alone.
- Truncating tool results in the output log (to 500 chars) keeps the JSON output manageable without affecting the LLM's reasoning, since the full result is still in the conversation messages.
