# Task 3 Plan: The System Agent

## Overview

Task 3 extends the Task 2 agent with a new tool `query_api` that can query the deployed backend API. The agent can now answer:
1. **Static system facts** — framework, ports, status codes (from source code)
2. **Data-dependent queries** — item count, scores, analytics (from live API)

## LLM Provider and Model

Same as Task 2:
- **Provider:** Qwen Code API
- **Model:** `qwen3-coder-plus`

Configuration from `.env.agent.secret`:
- `LLM_API_KEY`
- `LLM_API_BASE`
- `LLM_MODEL`

## New Environment Variables

Task 3 requires additional configuration:

| Variable | Purpose | Source |
|----------|---------|--------|
| `LMS_API_KEY` | Backend API authentication | `.env.docker.secret` |
| `AGENT_API_BASE_URL` | Backend API base URL (default: `http://localhost:42002`) | Optional, defaults to localhost |

**Important:** Two distinct keys:
- `LLM_API_KEY` — authenticates with LLM provider (Qwen)
- `LMS_API_KEY` — protects backend LMS endpoints

The agent must read ALL configuration from environment variables, not hardcoded values.

## New Tool Schema: `query_api`

```json
{
  "name": "query_api",
  "description": "Query the deployed backend API to get data or check system status",
  "parameters": {
    "type": "object",
    "properties": {
      "method": {
        "type": "string",
        "description": "HTTP method (GET, POST, etc.)",
        "enum": ["GET", "POST", "PUT", "DELETE"]
      },
      "path": {
        "type": "string",
        "description": "API endpoint path (e.g., '/items/', '/analytics/completion-rate')"
      },
      "body": {
        "type": "string",
        "description": "Optional JSON request body for POST/PUT requests"
      }
    },
    "required": ["method", "path"]
  }
}
```

**Implementation:**
- Use `httpx` to make HTTP requests
- Add `Authorization: Bearer <LMS_API_KEY>` header
- Return JSON string with `status_code` and `body`
- Handle errors gracefully (return error message, don't crash)

## Updated System Prompt

The system prompt must guide the LLM to choose the right tool:

```
You are a documentation and system assistant for a software engineering project.

Available tools:
- list_files(path): List files in a directory
- read_file(path): Read contents of a file
- query_api(method, path, body?): Query the live backend API

When answering questions:
1. For wiki/documentation questions → use list_files and read_file
2. For source code questions → use read_file on backend/ files
3. For live data questions (counts, status codes, analytics) → use query_api
4. For bug diagnosis → use query_api to see the error, then read_file to find the bug

Always include source references when applicable.
Maximum 10 tool calls per question.
```

## Agentic Loop

Same as Task 2, no changes needed:
1. Send question + tool definitions to LLM
2. Execute tool calls, append results
3. Repeat until answer or max 10 iterations
4. Output JSON with `answer`, `source` (optional), `tool_calls`

## Output Format

Same as Task 2, but `source` is now optional:

```json
{
  "answer": "There are 120 items in the database.",
  "source": "",  // Optional for API queries
  "tool_calls": [
    {
      "tool": "query_api",
      "args": {"method": "GET", "path": "/items/"},
      "result": "{\"status_code\": 200, \"body\": [...]}"
    }
  ]
}
```

## Benchmark Questions

The `run_eval.py` script tests 10 questions:

| # | Question | Expected Tool | Expected Answer |
|---|----------|---------------|-----------------|
| 0 | Protect branch steps (wiki) | `read_file` | branch, protect |
| 1 | SSH connection (wiki) | `read_file` | ssh/key/connect |
| 2 | Python web framework | `read_file` | FastAPI |
| 3 | API router modules | `list_files` | items, interactions, analytics, pipeline |
| 4 | Items in database | `query_api` | number > 0 |
| 5 | Status code without auth | `query_api` | 401/403 |
| 6 | Completion-rate error | `query_api`, `read_file` | ZeroDivisionError |
| 7 | Top-learners crash | `query_api`, `read_file` | TypeError/None |
| 8 | Request lifecycle | `read_file` | 4+ hops (LLM judge) |
| 9 | ETL idempotency | `read_file` | external_id check (LLM judge) |

## Implementation Steps

1. Create `plans/task-3.md` (this file) — commit first
2. Add `LMS_API_KEY` and `AGENT_API_BASE_URL` to environment loading
3. Implement `query_api` tool:
   - Read `LMS_API_KEY` from `.env.docker.secret`
   - Make HTTP requests with authentication
   - Return status_code + body
4. Add `query_api` to TOOLS list
5. Update system prompt with tool selection guidance
6. Run `uv run run_eval.py` to test
7. Debug failures:
   - Check tool descriptions
   - Fix tool implementation bugs
   - Adjust system prompt
8. Iterate until all 10 questions pass
9. Update `AGENT.md` with:
   - `query_api` documentation
   - Authentication details
   - Lessons learned from benchmark
   - Final eval score (at least 200 words)
10. Add 2 regression tests for Task 3
11. Commit, push, create PR

## Security Considerations

1. **API Key Protection:**
   - `LMS_API_KEY` must NOT be hardcoded
   - Read from environment variable only
   - Never commit `.env.docker.secret`

2. **Path Validation:**
   - `query_api` should validate paths (no `..` traversal)
   - Only allow relative paths from API base

3. **Request Limits:**
   - Timeout for API calls (30 seconds)
   - Max 10 tool calls per question

## Debugging Strategy

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Agent doesn't call `query_api` | Tool description unclear | Improve description |
| API returns 401 | Missing/wrong LMS_API_KEY | Check env loading |
| Agent crashes on null content | `msg.get("content", "")` with null | Use `(msg.get("content") or "")` |
| Timeout | Too many tool calls | Reduce max iterations |
| Wrong tool used | LLM confused about tools | Clarify system prompt |

## Success Criteria

- ✅ `plans/task-3.md` committed before code
- ✅ `query_api` tool defined and authenticated
- ✅ Agent reads all config from environment variables
- ✅ `run_eval.py` passes all 10 questions
- ✅ `AGENT.md` updated (200+ words)
- ✅ 2 regression tests pass
- ✅ Git workflow: issue, branch, PR, review, merge
- ✅ Autochecker bot benchmark passes

## Initial Benchmark Run

(To be filled after first `run_eval.py` run)

```
Score: X/10 passed
Failures:
- Question N: ...
```

## Iteration Strategy

(To be filled based on failures)
