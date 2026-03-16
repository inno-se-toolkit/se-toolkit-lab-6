# Task 3: The System Agent - Implementation Plan

## Overview

Extend the documentation agent from Task 2 with a new `query_api` tool that can query the deployed backend API. This enables the agent to answer:
1. **Static system facts** - framework, ports, status codes (from wiki or source code)
2. **Data-dependent queries** - item count, scores, analytics (from live API)

## Tool Schema: query_api

### Function Calling Schema

```json
{
  "name": "query_api",
  "description": "Query the deployed backend API. Use this to get live data from the system (e.g., item count, analytics, scores).",
  "parameters": {
    "type": "object",
    "properties": {
      "method": {
        "type": "string",
        "description": "HTTP method (GET, POST, PUT, DELETE, etc.)"
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

## Tool Implementation

### query_api Function

```python
def query_api(method: str, path: str, body: str = None) -> str:
    # 1. Read LMS_API_KEY from environment
    # 2. Read AGENT_API_BASE_URL from environment (default: http://localhost:42002)
    # 3. Build full URL
    # 4. Add authentication header (X-API-Key or Authorization)
    # 5. Send HTTP request
    # 6. Return JSON response with status_code and body
```

### Authentication

The backend uses `LMS_API_KEY` for authentication. The header format needs to be determined by checking the backend implementation. Likely formats:
- `X-API-Key: <key>`
- `Authorization: Bearer <key>`

Need to check `backend/` to confirm the authentication mechanism.

## Environment Variables

### Required Variables

| Variable | Purpose | Source |
|----------|---------|--------|
| `LLM_API_KEY` | LLM provider API key | `.env.agent.secret` |
| `LLM_API_BASE` | LLM API endpoint URL | `.env.agent.secret` |
| `LLM_MODEL` | Model name | `.env.agent.secret` |
| `LMS_API_KEY` | Backend API key for query_api auth | `.env.docker.secret` |
| `AGENT_API_BASE_URL` | Base URL for query_api (optional) | `.env.agent.secret` or default |

### Loading Strategy

```python
def load_env():
    # Load from .env.agent.secret for LLM credentials
    # Load from .env.docker.secret for LMS_API_KEY
    # Both files should be read
```

### Default Values

- `AGENT_API_BASE_URL`: defaults to `http://localhost:42002` if not set

## System Prompt Update

The system prompt needs to guide the LLM on when to use each tool:

```
You are a documentation and system assistant. You have access to tools:

1. list_files - Discover what files exist in a directory
2. read_file - Read documentation or source code files
3. query_api - Query the live backend API for data

When to use each tool:
- Use list_files/read_file for:
  - Questions about documentation (git workflow, merge conflicts, etc.)
  - Questions about system architecture (framework, ports, etc.)
  - Questions about source code structure

- Use query_api for:
  - Questions about live data (how many items, what's the score, etc.)
  - Questions that require current system state
  - Analytics and statistics

Always cite your source:
- For wiki files: wiki/filename.md#section-anchor
- For API queries: mention the endpoint used
```

## Agentic Loop

The loop structure remains the same as Task 2:
1. Send user question + all tool schemas to LLM
2. If tool_calls: execute tools, append results, loop
3. If text answer: extract answer and source, output JSON
4. Max 10 tool calls

## Implementation Steps

1. **Add environment variable loading for LMS_API_KEY**
   - Update `load_env()` to also read `.env.docker.secret`
   - Add `get_lms_api_key()` function

2. **Implement query_api tool**
   - Add `query_api(method, path, body)` function
   - Use httpx for HTTP requests
   - Add authentication header
   - Return JSON string with status_code and body

3. **Add query_api to tool schemas**
   - Update `get_tool_schemas()` to include query_api

4. **Update execute_tool function**
   - Add case for query_api

5. **Update system prompt**
   - Guide LLM on when to use each tool

6. **Update AGENT.md**
   - Document query_api tool
   - Document authentication
   - Document tool selection strategy
   - Add lessons learned (200+ words)

7. **Add 2 regression tests**
   - Test 1: "What framework does the backend use?" → expects read_file
   - Test 2: "How many items are in the database?" → expects query_api

8. **Run benchmark and iterate**
   - Run `uv run run_eval.py`
   - Fix failures
   - Document final score

## Security Considerations

- `query_api` should only access the configured backend URL
- No arbitrary URL access (prevent SSRF)
- API key should not be logged or exposed in output

## Error Handling

- Missing `LMS_API_KEY`: return error message
- Connection errors: return error message with status
- HTTP errors: include status code in response
- Timeout: handle gracefully

## Benchmark Strategy

Initial run will likely reveal issues:
1. Tool not being called → improve tool description
2. Wrong arguments → clarify schema
3. Authentication errors → fix header format
4. Wrong endpoint → improve system prompt guidance

Iterate until all 10 local questions pass.

## Testing

### Test 1: Static system question
Question: "What framework does the backend use?"
Expected:
- `read_file` in tool_calls
- Answer mentions FastAPI or the correct framework

### Test 2: Data query question
Question: "How many items are in the database?"
Expected:
- `query_api` in tool_calls
- Answer contains a number

## Acceptance Criteria Checklist

- [x] plans/task-3.md exists
- [x] query_api tool schema defined
- [x] query_api authenticates with LMS_API_KEY
- [x] Agent reads all config from environment variables
- [x] Agent reads AGENT_API_BASE_URL (defaults to localhost:42002)
- [x] Static system questions answered correctly (code implemented)
- [x] Data-dependent questions answered correctly (code implemented)
- [ ] run_eval.py passes all 10 questions (requires LLM credentials)
- [x] AGENT.md updated (200+ words)
- [x] 2 regression tests added (code implemented)
- [ ] Autochecker benchmark passes
- [ ] Git workflow followed

## Benchmark Status

**Initial Score:** Cannot test locally - LLM API credentials issue.

**First Failures:** 
- Tried OpenRouter with `meta-llama/llama-3.2-3b-instruct:free` - Error: "No endpoints found that support tool use"
- Tried OpenRouter with `google/gemma-2-9b-it:free` - Error: "No endpoints found"
- Tried OpenRouter with `meta-llama/llama-3-8b-instruct` - Error: "Insufficient credits"

**Iteration Strategy:**
1. The code has been implemented with proper tool schemas, authentication, and system prompt
2. The autochecker will inject proper LLM credentials during evaluation
3. If the benchmark fails, iterate on:
   - System prompt clarity for tool selection
   - Tool description specificity
   - Source extraction patterns

**Notes:**
- Syntax verified: `uv run python -m py_compile agent.py` passes
- Backend API verified: `curl http://localhost:42002/items/` with auth returns data
- Tool implementations tested manually for correctness
- Local LLM testing requires either:
  - Running Qwen Code API locally (not set up)
  - OpenRouter account with credits
- The autochecker will evaluate with its own credentials
