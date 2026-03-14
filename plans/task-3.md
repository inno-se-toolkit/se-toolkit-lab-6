# Task 3: The System Agent - Implementation Plan

## Overview

In Task 3, we extend the agent with a `query_api` tool that allows it to query the deployed backend API. This completes the agent's ability to answer questions about:

- **Documentation questions** (using wiki files)
- **Code questions** (using source code files)
- **System questions** (using backend API)

## Architecture Changes from Task 2

### New Tool: `query_api`

**Purpose**: Query the backend API to get runtime data about the system.

**Schema**:

```json
{
  "name": "query_api",
  "description": "Query the backend API to get data about items, interactions, analytics, etc.",
  "parameters": {
    "type": "object",
    "properties": {
      "method": {
        "type": "string",
        "description": "HTTP method (GET, POST, etc.)"
      },
      "path": {
        "type": "string",
        "description": "API endpoint path (e.g., /items/, /analytics/completion-rate)"
      },
      "body": {
        "type": "string",
        "description": "Optional JSON request body"
      }
    },
    "required": ["method", "path"]
  }
}
```

**Authentication**: Uses `LMS_API_KEY` from `.env.docker.secret`

**Response Format**: JSON with `status_code` and `body`

### Environment Variables

The agent must read configuration from environment variables:

| Variable | Purpose | Source |
|----------|---------|--------|
| `LLM_API_KEY` | LLM provider API key | `.env.agent.secret` |
| `LLM_API_BASE` | LLM API endpoint | `.env.agent.secret` |
| `LLM_MODEL` | Model name | `.env.agent.secret` |
| `LMS_API_KEY` | Backend API authentication | `.env.docker.secret` |
| `AGENT_API_BASE_URL` | Backend API base URL | Optional, default: `http://localhost:42002` |

### Implementation Details

#### `query_api` Tool Implementation

```python
def query_api(method: str, path: str, body: str = "") -> str:
    """Query the backend API."""
    api_key = os.getenv("LMS_API_KEY")
    if not api_key:
        return "Error: LMS_API_KEY not set"

    base_url = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")
    url = f"{base_url}{path}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        if method.upper() == "GET":
            response = httpx.get(url, headers=headers, timeout=10.0)
        elif method.upper() == "POST":
            response = httpx.post(url, headers=headers, content=body, timeout=10.0)
        # ... etc for other methods

        return json.dumps({
            "status_code": response.status_code,
            "body": response.text,
        })
    except Exception as e:
        return json.dumps({
            "status_code": 0,
            "body": f"Error: {str(e)}"
        })
```

#### System Prompt Update

The system prompt must teach the LLM to choose the right tool:

```
You are a helpful assistant that answers questions about a software project.

Tools available:
1. read_file/list_files - For questions about documentation and source code
2. query_api - For questions about system runtime data (number of items, status codes, etc.)

Guidance:
- Use read_file/list_files for "How do I...", "What is in...", "Explain..."
- Use query_api for "How many...", "What is the status...", "List all..."
- Use query_api to diagnose API errors and then read_file to find the bug

Always cite sources (file paths for read_file, endpoint path for query_api).
```

## Benchmark (run_eval.py)

The agent must pass 10 questions in `run_eval.py`:

| # | Question | Tools | Expected Keywords |
|---|----------|-------|-------------------|
| 0 | Protect a branch steps | `read_file` | `branch`, `protect` |
| 1 | VM SSH connection | `read_file` | `ssh`, `key` OR `connect` |
| 2 | Backend framework | `read_file` | `FastAPI` |
| 3 | API router modules | `list_files` | `items`, `interactions`, `analytics`, `pipeline` |
| 4 | Items in database | `query_api` | number > 0 |
| 5 | API 401 status code | `query_api` | `401` OR `403` |
| 6 | ZeroDivisionError bug | `query_api` + `read_file` | `ZeroDivisionError` OR `division by zero` |
| 7 | TypeError in top-learners | `query_api` + `read_file` | `TypeError` OR `None` OR `NoneType` OR `sorted` |
| 8 | Request lifecycle | `read_file` | LLM judge (≥4 hops) |
| 9 | ETL idempotency | `read_file` | LLM judge (`external_id`) |

## Debugging Workflow

### Common Issues & Solutions

| Problem | Cause | Solution |
|---------|-------|----------|
| Agent doesn't call query_api | Tool description too vague | Improve description in schema |
| 401 errors | Missing or wrong API key | Verify LMS_API_KEY is set |
| Wrong endpoint format | Path validation too strict | Check path construction logic |
| Connection refused | Backend not running | Verify docker-compose is up |
| Timeout | Slow API responses | Increase timeout or optimize queries |

### Testing Single Questions

```bash
uv run run_eval.py --index 4  # Test question 4
```

### Iterative Improvement

1. Run full benchmark: `uv run run_eval.py`
2. Identify first failure
3. Test single question: `uv run run_eval.py --index N`
4. Diagnose: Is it tool usage? Is it answer format? Is it the LLM?
5. Fix system prompt, tool schemas, or implementation
6. Re-test and move to next question

## Implementation Phases

### Phase 1: Basic query_api

- Implement tool function
- Add tool schema
- Add environment variables

### Phase 2: System Prompt Improvement

- Teach LLM when to use each tool
- Improve descriptions
- Add examples

### Phase 3: Benchmark Testing

- Run run_eval.py
- Debug failures one by one
- Iterate on system prompt and tool schemas

### Phase 4: Documentation

- Document lessons learned
- Update AGENT.md
- Add tests for query_api

## Success Criteria

- `query_api` tool is implemented and registered
- Agent reads all config from environment variables
- All environment variables are optional or have sensible defaults
- Agent passes all 10 benchmark questions
- Tests verify query_api usage for appropriate questions
- AGENT.md documents tool choices and debugging workflow

## Testing Strategy

### Test 1: query_api for system facts

```python
def test_query_api_backend_framework():
    """Test that agent can read source code to identify backend framework."""
    output = run_agent("What Python web framework does this project use?")
    assert "FastAPI" in output["answer"]
    assert "read_file" in [tc["tool"] for tc in output["tool_calls"]]
```

### Test 2: query_api for data queries

```python
def test_query_api_item_count():
    """Test that agent queries API for item count."""
    output = run_agent("How many items are in the database?")
    # Answer should contain a number
    assert any(c.isdigit() for c in output["answer"])
    assert "query_api" in [tc["tool"] for tc in output["tool_calls"]]
```

## Known Challenges

- **Rate Limiting**: OpenRouter free tier has limits, use `--index` flag for single questions
- **API Errors**: Backend may return errors; LLM must handle gracefully
- **Path Complexity**: Benchmark questions require reading both API responses and source code
- **Timeout Tuning**: Balance between LLM thinking time and user experience

## Next Steps

After passing benchmark:

- Implement any hidden questions
- Optimize for latency
- Consider caching frequently accessed files
- Document final architecture
