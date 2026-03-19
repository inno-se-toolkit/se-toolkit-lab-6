# Agent Architecture (Task 3 — System Agent)

This repository contains an `agent.py` CLI that answers questions by **calling an LLM with agentic tools**. Task 3 extends the Task 2 architecture with a second tool source: the **query_api** tool allows the agent to query the deployed backend API for live system data and framework facts.

Unlike Task 2 (documentation-only), the Task 3 agent can now:
- Answer documentation questions by reading wiki files → uses `read_file`
- Answer data queries by querying the backend API → uses `query_api`
- Answer framework/tech stack questions by checking both sources

## Provider (LLM)
- Provider: **Qwen Code API** via `qwen-code-oai-proxy`
- Endpoint: `LLM_API_BASE` + `/chat/completions`
- Authentication: `LLM_API_KEY`
- Model: `LLM_MODEL`

## Environment Configuration
The agent reads configuration from environment variables:
- `LLM_API_KEY` (LLM provider API key, from `.env.agent.secret`)
- `LLM_API_BASE` (LLM provider endpoint, from `.env.agent.secret`)
- `LLM_MODEL` (Model name, from `.env.agent.secret`)
- `LMS_API_KEY` (Backend API authentication key, from `.env.docker.secret`)
- `AGENT_API_BASE_URL` (Backend API base URL, defaults to `http://localhost:42002`)

**Important**: These are **two distinct API keys**:
- `LLM_API_KEY` authenticates with the LLM provider (Qwen Code API)
- `LMS_API_KEY` authenticates with the backend API (Learning Management Service)

For local development, `agent.py` loads `.env.agent.secret` and `.env.docker.secret` (if present) but only fills missing values; environment variables injected by the autochecker always take priority.

## Tools

The agent has three tools available via OpenAI-compatible function calling:

### read_file
- **Description**: Read a file from the project repository
- **Parameters**: 
  - `path` (string): Relative path from project root (e.g., "wiki/git.md")
- **Returns**: File contents as string, or error message if file doesn't exist
- **Security**: Rejects paths with `..` or absolute paths to prevent directory traversal
- **Use Case**: Documentation and source code lookup

### list_files
- **Description**: List files and directories at a given path
- **Parameters**:
  - `path` (string): Relative directory path from project root (e.g., "wiki")
- **Returns**: Newline-separated listing of entries (directories end with `/`)
- **Security**: Rejects paths with `..` or absolute paths
- **Use Case**: Exploring project structure and wiki organization

### query_api
- **Description**: Query the deployed backend API for live system data
- **Parameters**:
  - `method` (string): HTTP method (GET, POST, PUT, DELETE, PATCH)
  - `path` (string): API endpoint path (e.g., "/items/", "/analytics/completion-rate?lab=lab-01")
  - `body` (string, optional): JSON request body for POST/PUT/PATCH requests
- **Returns**: JSON string with `{"status_code": int, "body": ...}`
- **Authentication**: Uses `LMS_API_KEY` as Bearer token in Authorization header
- **Use Case**: Live data queries and system facts (framework detection, data availability, metrics)

## Agentic Loop

The agent implements a reasoning loop (same as Task 2, extended with query_api):

1. **Send question to LLM** with all three tool schemas
2. **Parse LLM response**:
   - If the response includes `tool_calls` → execute each tool, record results, append as "tool" role messages, loop back to step 1
   - If the response is text only (no `tool_calls`) → extract answer, move to step 4
   - If max iterations (10) reached → stop looping, use accumulated answer
3. **Execute tools** with validation; if tool fails, return error message to LLM for re-planning
4. **Extract source reference** from answer (wiki paths, or "API" for query_api calls)
5. **Return JSON** with answer, source, and tool_calls log

### System Prompt Strategy (Task 3 Extension)
The system prompt directs the LLM to:

**Tool Selection**:
- Use `read_file` / `list_files` for **documentation and source code** (static, in wiki/ or backend/)
- Use `query_api` for **live system data and framework facts** (dynamic, from running backend)

**Example Guidance**:
- "What framework does this project use?" → Try reading `backend/app/main.py` (read_file) OR check framework headers (query_api)
- "How many items are in the database?" → GET /items/ (query_api)
- "What are the HTTP status codes?" → Query API responses or read API documentation
- "How do you resolve a merge conflict?" → Read wiki/git-workflow.md (read_file)

The LLM must learn to differentiate: documentation questions stay in wiki/, data questions go to query_api, and some questions may require both tools.

## Request/Response Shape

### Output Format
Single JSON line on stdout (Task 3):
```json
{
  "answer": "The backend uses FastAPI. There are 42 items in the database.",
  "source": "backend/app/main.py and API: /items/",
  "tool_calls": [
    {"tool": "read_file", "args": {"path": "backend/app/main.py"}, "result": "from fastapi import FastAPI\n..."},
    {"tool": "query_api", "args": {"method": "GET", "path": "/items/"}, "result": "{\"status_code\": 200, \"body\": [...]}"}
  ]
}
```

- **answer**: Final text answer from the LLM
- **source**: Reference to source(s) used (wiki file, backend code path, or "API: /endpoint")
- **tool_calls**: Array of all tool calls executed (up to 10 per question)

## Authentication & Security

**query_api Authentication**:
- Reads `LMS_API_KEY` from environment (must be set)
- Adds `Authorization: Bearer {LMS_API_KEY}` header to all requests
- backend/app/auth.py middleware verifies this header
- If key is missing: agent raises `RuntimeError` with clear message, exits with code 1

**Environment Variable Priority**:
1. Already set in `os.environ` (e.g., autochecker injection)
2. Loaded from `.env.agent.secret` (local dev only)
3. Loaded from `.env.docker.secret` (local dev only)
4. Fall back to `_require_env()` which raises error if missing

This ensures autochecker can inject different credentials without agent hardcoding.

## Lessons Learned (Task 3 Build)

1. **LLM Tool Selection Requires Clear Prompting**: The LLM needs explicit guidance on when to use query_api vs read_file. Vague prompts lead to wrong tool choice. Prompts for specific endpoint patterns (/items/, /analytics/*) help.

2. **API Response Format Matters**: The agent formats API responses as `{status_code, body}` so the LLM can see both success and error details. Returning just the body can confuse the LLM if status != 200.

3. **Environment Variables Must Be Optional**: The `_require_env()` function checks if a var exists, but the agent must gracefully handle missing `AGENT_API_BASE_URL` (defaults to localhost). Autochecker injects its own URL, so defaults are only for local dev.

4. **Tool Descriptions Are Critical**: The query_api description explicitly says "Do NOT use for documentation lookups" — this single phrase reduced mis-selection significantly. Negative guidance is as important as positive.

5. **Authentication Separation**: Keep `LMS_API_KEY` and `LLM_API_KEY` separate in code and docs. Both are "API keys" but they authenticate different services. Confusing them is a common error during integration.

## Run
Example Task 3 queries:
```bash
# Documentation lookup (uses read_file)
uv run agent.py "What is HTTP status 422?"

# Data query (uses query_api)
uv run agent.py "How many items are in the database?"

# Framework question (uses read_file + query_api)
uv run agent.py "What web framework does this project use?"
```


