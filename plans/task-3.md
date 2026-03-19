# Task 3: System Agent — Implementation Plan

## Overview
Add a `query_api` tool to the Task 2 agent so it can query the deployed backend API for system facts (framework, ports) and data-dependent queries (item count, scores).

## Design

### 1. query_api Tool Schema
- **name**: `query_api`
- **parameters**:
  - `method` (string): HTTP method (GET, POST, PUT, DELETE, etc.)
  - `path` (string): API path (e.g., `/items/`, `/analytics/completion-rate?lab=lab-99`)
  - `body` (string, optional): JSON request body for POST/PUT requests
- **returns**: JSON string with `status_code` and `body` fields

### 2. Authentication Flow
- Read `LMS_API_KEY` from `.env.docker.secret` (the backend auth key)
- Include as `Authorization: Bearer <LMS_API_KEY>` header in all API calls
- **Key distinction**: `LMS_API_KEY` (backend) ≠ `LLM_API_KEY` (LLM provider)

### 3. Environment Variables (all from .env files, not hardcoded)
- `LLM_API_KEY`: LLM provider API key (.env.agent.secret)
- `LLM_API_BASE`: LLM API endpoint (.env.agent.secret)
- `LLM_MODEL`: Model name (.env.agent.secret)
- `LMS_API_KEY`: Backend authentication key (.env.docker.secret)
- `AGENT_API_BASE_URL`: Backend base URL (default: `http://localhost:42002`)

### 4. System Prompt Updates
Tell the LLM how to choose the right tool:
- Use `read_file` for documentation lookups (static, in wiki/)
- Use `query_api` for live system data:
  - Framework/tech stack questions (`GET /` or check docs)
  - Item/data counts (`GET /items/`)
  - Analytics queries (`GET /analytics/completion-rate?lab=...`)
- Use `list_files` to explore structure

### 5. Tool Call Flow (unchanged from Task 2)
1. Send question + tools to LLM
2. LLM decides which tool to call
3. Execute tool, collect result
4. Return result to LLM as context
5. Repeat until LLM says "done" (no more tool calls)
6. Extract final answer

## Implementation Steps

### Step 1: Add query_api Function
- Implement `_tool_query_api(method, path, body=None)` 
- Handle authentication header
- Make requests using `httpx.Client`
- Return JSON with status_code and body

### Step 2: Register Tool Schema
- Add query_api to `_get_tool_schemas()`
- Include clear parameter descriptions for the LLM

### Step 3: Update Tool Dispatcher
- Add query_api case to `_call_tool()`

### Step 4: Enhance System Prompt
- Document when to use each tool
- Provide examples of query_api calls
- Emphasize choosing the right tool for the question type

### Step 5: Test Iteration Strategy
1. Run `uv run run_eval.py` locally first
2. Expected failures in early iterations:
   - Schema issues (LLM misunderstands parameters)
   - Wrong tool selection (LLM uses read_file instead of query_api)
   - Argument errors (e.g., missing `?lab=` in query)
3. Fix by:
   - Improving schema descriptions
   - Adding examples to system prompt
   - Clarifying parameter meanings

## Data Sources

### Backend API Endpoints
- `GET /items/` — return itemlist → count items in database
- `GET /analytics/completion-rate?lab={lab}` → completion metrics
- `GET /analytics/scores?lab={lab}` → score distribution
- All require Bearer token in Authorization header

### Environment Reading
- `.env.agent.secret`: LLM credentials (reads at startup via `_load_env_file`)
- `.env.docker.secret`: Backend credentials (same loader)
- Autochecker injects its own values, so these are only local conveniences

## Error Handling
- Invalid path format → return error message
- API returns error (4xx/5xx) → return full response with status_code
- Network timeout → httpx raises; caught in main try-except
- Missing auth key → `_require_env` raises RuntimeError with clear message

## Success Criteria
- [ ] All 10 local eval questions pass
- [ ] query_api calls authenticate correctly
- [ ] LLM chooses right tool (read_file vs query_api) for each question
- [ ] No hardcoded credentials
- [ ] 2 regression tests pass (one for read_file, one for query_api)
- [ ] Agent passes autochecker hidden questions

## Benchmark Diagnostic (post-first-run)
Will update after first `uv run run_eval.py` with:
- Which questions passed/failed
- LLM tool selection issues
- API authentication problems
- Answer formatting issues
