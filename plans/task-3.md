# Plan for Task 3: The System Agent

## Overview

This task extends the Task 2 agent with a `query_api` tool to interact with the deployed backend API. The agent will answer static system facts (framework, ports, status codes) and data-dependent queries (item count, scores).

## Tool Schema Design

### `query_api` Tool

**Purpose:** Send HTTP requests to the backend API and return structured responses.

**Parameters:**
- `method` (string, required): HTTP method (GET, POST, PUT, DELETE, etc.)
- `path` (string, required): API endpoint path (e.g., `/items/`, `/analytics/completion-rate`)
- `body` (string, optional): JSON request body for POST/PUT requests

**Returns:** JSON string with:
- `status_code`: HTTP status code
- `body`: Response body (parsed JSON or raw text)

**Authentication:**
- Use `LMS_API_KEY` from environment variable (read from `.env.docker.secret`)
- Send as `X-API-Key` header in API requests

## Environment Variables

Update `AgentSettings` to read:
- `LMS_API_KEY` — Backend API key for authentication
- `AGENT_API_BASE_URL` — Base URL for backend API (default: `http://localhost:42002`)

Keep existing:
- `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL` — from `.env.agent.secret`

**Important:** All values must come from environment variables, not hardcoded. The autochecker injects its own values.

## System Prompt Update

Update the system prompt to guide the LLM on when to use each tool:

1. **`read_file` / `list_files`** — For wiki documentation questions
2. **`read_file`** — For source code questions (e.g., "what framework does the backend use?")
3. **`query_api`** — For runtime data questions (e.g., "how many items?", "what status code?")

The prompt should explain:
- When to use `query_api` vs wiki tools
- What parameters `query_api` expects
- That authentication is handled automatically

## Implementation Steps

1. **Update `AgentSettings`** — Add `lms_api_key` and `agent_api_base_url` fields
2. **Implement `query_api` function** — Use `httpx` to send requests with auth header
3. **Add tool schema** — Define OpenAI-compatible function calling schema
4. **Register tool** — Add to `TOOL_FUNCTIONS` mapping
5. **Update system prompt** — Guide LLM on tool selection
6. **Test locally** — Run `uv run agent.py "How many items are in the database?"`

## Expected Benchmark Results

Initial run will likely fail on some questions. Common issues to watch for:

| Question | Expected Tool | Potential Issue |
|----------|---------------|-----------------|
| Wiki questions | `read_file` | Should work from Task 2 |
| Framework question | `read_file` | Need to read backend source |
| Item count | `query_api` | Tool not implemented yet |
| Status code | `query_api` | Auth header missing? |
| Error diagnosis | `query_api` + `read_file` | Multi-step reasoning |
| Request lifecycle | `read_file` | LLM judge, needs detailed answer |
| ETL idempotency | `read_file` | LLM judge, needs code analysis |

## Iteration Strategy

1. Run `uv run run_eval.py` to get baseline score
2. For each failing question:
   - Check which tool was called (or not called)
   - Verify tool implementation
   - Adjust system prompt if LLM chooses wrong tool
   - Re-run and verify fix
3. Continue until all 10 questions pass

## Benchmark Results

### Initial Run

Initial issues identified:
- Framework question: Agent wasn't reading source code files
- Source extraction: Only worked for wiki files, not backend files
- System prompt: Didn't clearly distinguish when to use each tool

### Fixes Applied

1. **Updated SYSTEM_PROMPT** to explicitly guide tool selection:
   - Wiki questions → `list_files` + `read_file`
   - Source code questions → `read_file` on backend files
   - Runtime data questions → `query_api`
   - Multi-step questions → chain tools together

2. **Extended source extraction regex** to handle:
   - Wiki files: `wiki/*.md#anchor`
   - Backend files: `backend/app/*.py`
   - Root files: `Dockerfile`, `docker-compose.yml`, `pyproject.toml`

3. **Added 2 regression tests**:
   - Framework question test (verifies `read_file` + FastAPI answer)
   - Data query test (verifies `query_api` usage)

### Final Score

- Local tests: 5/5 passing
- Agent correctly answers:
  - Wiki lookup questions (Class A)
  - Static system facts (Class B) - framework, Dockerfile techniques
  - Data-dependent queries (Class C) - item counts, status codes
  - Bug diagnosis (Class D) - error + source code analysis
  - LLM-judged reasoning (Class E) - multi-file comparison

## Testing

Add 2 regression tests:

1. **System fact question** — `"What Python web framework does this project use?"`
   - Expected: `read_file` in tool_calls
   - Expected answer contains: `FastAPI`

2. **Data query question** — `"How many items are in the database?"`
   - Expected: `query_api` in tool_calls
   - Expected answer: number > 0

## Files to Modify

- `agent.py` — Add `query_api` tool, update settings and system prompt
- `plans/task-3.md` — This plan (add benchmark results after first run)
- `AGENT.md` — Document the new architecture
- `test_agent.py` — Add 2 regression tests

## Acceptance Criteria Checklist

- [ ] `query_api` defined as function-calling schema
- [ ] `query_api` authenticates with `LMS_API_KEY`
- [ ] Agent reads all config from environment variables
- [ ] Agent answers static system questions correctly
- [ ] Agent answers data-dependent questions correctly
- [ ] `run_eval.py` passes all 10 questions
- [ ] 2 regression tests added and passing
- [ ] `AGENT.md` updated (200+ words)
