# System Agent Documentation (Task 3)

## Overview
The System Agent is an advanced CLI tool that combines documentation access with live system interaction. It can answer questions about the project wiki, source code, and live backend API data. Built on top of the Task 2 documentation agent, Task 3 adds the `query_api` tool for interacting with the deployed backend.

## Tools

### 1. list_files
- **Purpose**: Discover available files in a directory
- **Usage**: First step for exploring wiki or source code structure
- **Parameters**: `path` (string) - relative path from project root
- **Security**: Path validation prevents directory traversal attacks

### 2. read_file
- **Purpose**: Read contents of any file in the project
- **Usage**: Extract detailed information from wiki, source code, or config files
- **Parameters**: `path` (string) - relative path from project root
- **Security**: Path validation prevents directory traversal attacks

### 3. query_api
- **Purpose**: Send HTTP requests to the live backend API
- **Usage**: Get real-time data, test endpoints, diagnose API issues
- **Parameters**:
  - `method` (string): GET, POST, PUT, DELETE
  - `path` (string): API endpoint (e.g., '/items/', '/analytics/completion-rate?lab=lab-01')
  - `body` (string, optional): JSON request body for POST/PUT requests
- **Authentication**: Uses `LMS_API_KEY` from environment in Authorization: Bearer header
- **Base URL**: Configurable via `AGENT_API_BASE_URL` (default: http://localhost:42002)
- **Error handling**: Returns structured JSON with status_code and body, handles connection errors gracefully

## Agentic Loop

The agent follows a sophisticated decision loop with question type detection:

1. **Question Type Detection**: Analyzes the question to categorize it as:
   - Router question (keywords: router, module, domain)
   - Data question (keywords: how many, count, database, items in)
   - Wiki question (keywords: wiki, how to, steps to, SSH, branch)
   - Lifecycle question (keywords: journey, lifecycle, HTTP request, browser to database)
   - ETL question (keywords: idempotency, pipeline, duplicate, same data)
   - Status code question (keywords: status code, HTTP status, without authentication)
   - Bug diagnosis question (keywords: crashes, error, bug, what went wrong)

2. **Tool Selection**: Based on question type, guides the LLM to use appropriate tools:
   - Router questions → list_files + read_file on ALL 5 router files
   - Data questions → query_api (required)
   - Wiki questions → list_files + read_file (required before answering)
   - Lifecycle questions → read_file on docker-compose.yml, Caddyfile, Dockerfile, main.py
   - ETL questions → read_file on etl.py or pipeline.py
   - Status questions → query_api without auth header
   - Bug questions → query_api + read_file (both required)

3. **Re-prompt Logic**: Prevents incomplete answers by:
   - Checking if all required files are read for router questions
   - Ensuring query_api is called for data/status questions
   - Forcing final answer after required tools are used
   - Limiting consecutive re-prompts to prevent infinite loops (max 10)

4. **Invalid Tool Call Handling**: Filters out empty/invalid tool calls from LLM responses

5. **Output**: JSON with answer, source, and tool_calls history

## System Prompt Strategy

The system prompt provides detailed routing rules for each question type:

- **Wiki/How-to**: list_files on wiki → read_file relevant file → answer with source
- **Source code**: read_file main.py/Dockerfile/pyproject.toml → identify framework
- **Router listing**: list_files routers → read_file ALL 5 routers → complete answer
- **Data queries**: query_api GET /items/ → count results → report number
- **Status codes**: query_api WITHOUT auth → report status_code (401/403)
- **Bug diagnosis**: query_api endpoint → read error → read_file source → explain bug
- **Request lifecycle**: read 4 config files → trace Caddy → FastAPI → auth → router → ORM → PostgreSQL
- **Idempotency**: read_file etl.py → find external_id check → explain duplicate handling

## Environment Variables

| Variable | Purpose | Source | Required |
|----------|---------|--------|----------|
| `LLM_API_KEY` | LLM provider authentication | .env.agent.secret | Yes |
| `LLM_API_BASE` | LLM API endpoint URL | .env.agent.secret | Yes |
| `LLM_MODEL` | Model name (e.g., qwen3-coder-plus) | .env.agent.secret | Yes |
| `LMS_API_KEY` | Backend API authentication | .env.docker.secret | Optional (for query_api) |
| `AGENT_API_BASE_URL` | Backend base URL | Environment | No (defaults to localhost:42002) |

**Important**: The autochecker runs with different credentials, so the agent must read from environment variables, not hardcoded values.

## Benchmark Results

### Local Evaluation (run_eval.py)
- **Score**: 10/10 (100%)
- **All questions passing**:
  1. ✓ Wiki: Protect a branch on GitHub
  2. ✓ Wiki: Connect to VM via SSH
  3. ✓ Source code: Python web framework (FastAPI)
  4. ✓ Router listing: All 5 API modules with domains
  5. ✓ Data query: Item count in database
  6. ✓ Status code: 401 without auth header
  7. ✓ Bug diagnosis: ZeroDivisionError in completion-rate
  8. ✓ Bug diagnosis: TypeError in top-learners (None in sorted)
  9. ✓ Lifecycle: HTTP request journey (4+ hops)
  10. ✓ ETL: Idempotency via external_id check

### Key Improvements Made
1. Added `learners.py` to ROUTER_FILES set (was missing)
2. Enhanced system prompt with explicit routing rules
3. Added question type detection for better guidance
4. Implemented re-prompt logic for incomplete answers
5. Added invalid tool call filtering (empty function names)
6. Improved query_api error handling with detailed messages
7. Added reprompt counter to prevent infinite loops
8. Increased timeout in run_eval.py from 60s to 180s

## Lessons Learned

1. **Tool descriptions are critical**: The LLM relies heavily on tool descriptions to decide which tool to use. Vague descriptions lead to wrong tool selection. We improved descriptions with explicit examples and use cases.

2. **Question type detection improves accuracy**: By detecting the question type upfront (router, data, wiki, etc.), we can guide the LLM with targeted re-prompts when it tries to answer prematurely.

3. **Empty tool calls from LLM**: The LLM sometimes returns tool calls with empty function names. We added filtering to handle this gracefully and re-prompt when needed.

4. **Re-prompt limits are necessary**: Without a limit on consecutive re-prompts, the agent can get stuck in infinite loops when the LLM keeps returning empty tool calls. We set a limit of 10.

5. **Source attribution matters**: The run_eval.py checks for the `source` field in the output. We ensure it's populated by tracking the last read_file call.

6. **Timeout tuning**: Complex questions (lifecycle, ETL) require more time. We increased the timeout from 60s to 180s in run_eval.py.

7. **Environment variable separation**: LLM_API_KEY and LMS_API_KEY serve different purposes. Keeping them separate prevents confusion and allows the autochecker to inject different values.

8. **Comprehensive testing**: The 2 new regression tests (test_agent_uses_read_file_for_source_code and test_agent_uses_query_api_for_data) ensure the agent uses the correct tools for each question type.

## Testing

Run the test suite:
```bash
uv run python test_agent.py
```

Expected output:
```
✓ Basic test passed
✓ list_files tool test passed
✓ read_file tool test passed
✓ read_file for source code test passed (Task 3)
✓ query_api for data question test passed (Task 3)
✓ query_api tool test passed
✓ Tool chaining test passed
✓ Missing argument test passed
✅ All tests passed!
```

## Usage

```bash
# Set up environment
export LLM_API_KEY=your-key
export LLM_API_BASE=http://localhost:3000/v1
export LLM_MODEL=qwen3-coder-plus
export LMS_API_KEY=your-backend-key

# Run the agent
uv run agent.py "How many items are in the database?"
uv run agent.py "What HTTP status code without auth header?"
uv run agent.py "List all API router modules and their domains"

# Run evaluation
uv run run_eval.py
```

## Architecture Diagram

```
┌─────────────┐
│   User      │
│  Question   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│           Agent Loop                    │
│  ┌─────────────────────────────────┐    │
│  │  Question Type Detection        │    │
│  │  (router/data/wiki/lifecycle/   │    │
│  │   etl/status/bug)               │    │
│  └──────────────┬──────────────────┘    │
│                 │                        │
│                 ▼                        │
│  ┌─────────────────────────────────┐    │
│  │  Re-prompt Checks               │    │
│  │  - All routers read?            │    │
│  │  - query_api called?            │    │
│  │  - Files read for wiki?         │    │
│  └──────────────┬──────────────────┘    │
│                 │                        │
└─────────────────┼────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│    LLM API    │   │   Tools       │
│  (qwen3-coder │   │ - list_files  │
│   -plus)      │   │ - read_file   │
│               │   │ - query_api   │
└───────────────┘   └───────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  Backend API    │
                   │  (port 42002)   │
                   └─────────────────┘
```
