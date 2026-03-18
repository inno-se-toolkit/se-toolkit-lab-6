# Plan for Task 3: The System Agent

## Overview

Task 3 extends the documentation agent from Task 2 with a new `query_api` tool that allows the agent to query the deployed backend API. This enables answering two new kinds of questions:

1. **Static system facts** - framework, ports, status codes (can also use wiki)
2. **Data-dependent queries** - item count, scores, analytics (must query API)

## Implementation Plan

### 1. Add `query_api` Tool Schema

I will add a new tool schema to `get_tool_schemas()` in `agent.py`:

```python
{
    "type": "function",
    "function": {
        "name": "query_api",
        "description": "Query the backend API for data or system information",
        "parameters": {
            "type": "object",
            "properties": {
                "method": {"type": "string", "description": "HTTP method (GET, POST, etc.)"},
                "path": {"type": "string", "description": "API path (e.g., '/items/', '/analytics/completion-rate')"},
                "body": {"type": "string", "description": "Optional JSON request body"}
            },
            "required": ["method", "path"]
        }
    }
}
```

### 2. Implement `tool_query_api()` Function

The function will:

- Read `AGENT_API_BASE_URL` from environment (default: `http://localhost:42002`)
- Read `LMS_API_KEY` from `.env.docker.secret` for authentication
- Make HTTP request using `httpx`
- Return JSON string with `status_code` and `body`

```python
def tool_query_api(method: str, path: str, body: str = None) -> str:
    # Load LMS_API_KEY from .env.docker.secret
    # Build URL from AGENT_API_BASE_URL + path
    # Add Authorization header with LMS_API_KEY
    # Return JSON: {"status_code": 200, "body": {...}}
```

### 3. Update Configuration Loading

Extend `load_config()` to also load backend credentials:

- `LMS_API_KEY` from `.env.docker.secret`
- `AGENT_API_BASE_URL` from environment (with default)

### 4. Update System Prompt

Modify the system prompt to tell the LLM when to use each tool:

- `list_files` / `read_file` - for wiki documentation
- `query_api` - for live data from the backend (item counts, analytics, etc.)

Example guidance:
> "Use `query_api` when asked about current data in the system (e.g., 'How many items...', 'What is the completion rate'). Use `read_file` for documentation questions."

### 5. Update `execute_tool()` Dispatcher

Add a new branch to handle `query_api`:

```python
elif tool_name == "query_api":
    method = args.get("method", "GET")
    path = args.get("path", "")
    body = args.get("body")
    return tool_query_api(method, path, body)
```

### 6. Update AGENT.md Documentation

Document:

- The new `query_api` tool and its parameters
- Authentication with `LMS_API_KEY`
- How the LLM decides between wiki tools and `query_api`
- Environment variables used
- Lessons learned from benchmark testing

### 7. Add Regression Tests

Add 2 new tests to `tests/test_agent.py`:

1. Test that "What framework does the backend use?" triggers `read_file`
2. Test that "How many items are in the database?" triggers `query_api`

## Environment Variables

| Variable | Source | Default |
|----------|--------|---------|
| `LLM_API_KEY` | `.env.agent.secret` | - |
| `LLM_API_BASE` | `.env.agent.secret` | - |
| `LLM_MODEL` | `.env.agent.secret` | - |
| `LMS_API_KEY` | `.env.docker.secret` | - |
| `AGENT_API_BASE_URL` | Environment / `.env` | `http://localhost:42002` |

## Benchmark Strategy

1. First run `uv run run_eval.py` to see initial score
2. For each failing question:
   - Analyze what tool the agent should have used
   - Check if the tool description is clear enough
   - Verify the API endpoint is correct
   - Adjust system prompt if needed
3. Iterate until all 10 local questions pass

## Benchmark Results and Iterations

### Initial Run: 3/10 passed

**First failures:**

1. Question 4 (API routers): Agent didn't use `list_files` for backend directories. **Fix:** Updated system prompt to mention exploring any directory, not just wiki.

2. Question 6 (status code): Agent used `read_file` instead of `query_api`. **Fix:** Updated system prompt to explicitly mention using `query_api` for API behavior questions.

3. Question 7 (completion-rate bug): Agent used wrong query parameter (`lab_id` instead of `lab`). **Fix:** Updated `query_api` tool description to include query parameters in path string.

### Second Run: 5/10 passed

**Remaining issues:**

- Question 7: Agent didn't read source code after getting error. **Fix:** Added "When asked to diagnose a bug" section to system prompt.

### Third Run: 6/10 passed

**Remaining issues:**

- Question 7: Source field was "unknown". **Fix:** Updated `extract_source_from_answer()` to match any file path, not just `wiki/`.

### Final Run: 10/10 passed ✓

All local questions now pass. The agent successfully:

- Uses `list_files` and `read_file` for documentation and code structure questions
- Uses `query_api` for data and API behavior questions
- Diagnoses bugs by combining API errors with source code analysis
- Provides proper source references

## Potential Issues

- **Path validation**: `query_api` paths don't need file system validation, but should be sanitized
- **Authentication**: Must use `LMS_API_KEY` not `LLM_API_KEY`
- **Error handling**: API errors should be returned to LLM so it can retry or report
- **Timeout**: API calls may be slow; need appropriate timeout handling

## Acceptance Criteria Checklist

- [x] `plans/task-3.md` exists with implementation plan and benchmark diagnosis
- [x] `query_api` tool schema defined in `get_tool_schemas()`
- [x] `tool_query_api()` implemented with authentication
- [x] `AGENT_API_BASE_URL` read from environment
- [x] `LMS_API_KEY` loaded from `.env.docker.secret`
- [x] System prompt updated to guide tool selection
- [x] `run_eval.py` passes all 10 questions (10/10)
- [x] `AGENT.md` updated (200+ words)
- [x] 2 new regression tests added (5 total tests passing)
