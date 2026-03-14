# Agent Architecture

## Overview

This project implements a CLI system agent (`agent.py`) that answers questions by calling an LLM API with tools. The agent can read documentation files, explore the project structure, and query the live backend API to find answers.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  agent.py    │────▶│  Qwen Code API (on VM)           │   │
│  │  (CLI)       │◀────│  OpenAI-compatible endpoint      │   │
│  └──────┬───────┘     └──────────────────────────────────┘   │
│         │                                                    │
│         │ Tools:                                             │
│         ├─ read_file(path) ──▶ Read file contents            │
│         ├─ list_files(path) ─▶ List directory entries        │
│         ├─ query_api(method, path, body) ─▶ Call backend API │
│         │                                                    │
│         │ Agentic Loop:                                      │
│         │ 1. Send question + tools to LLM                    │
│         │ 2. LLM returns tool calls (or final answer)        │
│         │ 3. Execute tools, append results                   │
│         │ 4. Repeat until answer or max 10 calls             │
│         ▼                                                    │
│  ┌──────────────────────────────────────────────────┐        │
│  │  JSON Output                                     │        │
│  │  {"answer": "...", "source": "...",              │        │
│  │   "tool_calls": [{"tool": "...", ...}]}          │        │
│  └──────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Components

### `agent.py`

Main CLI entry point with agentic loop and three tools.

**Key functions:**

| Function | Description |
|----------|-------------|
| `load_config()` | Reads LLM and LMS config from `.env.agent.secret` and `.env.docker.secret` |
| `validate_path(path)` | Validates path is within project root (security) |
| `read_file(path)` | Tool: reads file contents from repository |
| `list_files(path)` | Tool: lists directory entries |
| `query_api(method, path, body)` | Tool: calls backend LMS API with authentication |
| `execute_tool(name, args)` | Executes a tool by name and returns result |
| `call_llm(messages, config)` | Makes HTTP POST to LLM API with tool definitions |
| `run_agentic_loop(question, config)` | Main loop: LLM → tool → LLM → answer |
| `extract_source_from_messages(messages)` | Extracts source reference from conversation |
| `main()` | Entry point |

### Tools

Three tools are registered as function-calling schemas:

#### `read_file(path: str)`

Reads the contents of a file from the project repository.

**Parameters:**
- `path` (string, required): Relative path from project root (e.g., `wiki/git-workflow.md`, `backend/app/main.py`)

**Returns:**
```json
{"content": "file contents..."}
// or
{"error": "File not found: ..."}
```

**Security:**
- Rejects absolute paths
- Rejects paths with `..` (path traversal)
- Validates resolved path is within project root

**Use for:** Wiki documentation, source code, configuration files

#### `list_files(path: str)`

Lists files and directories at a given path.

**Parameters:**
- `path` (string, required): Relative directory path from project root (e.g., `wiki`, `backend/app/routers`)

**Returns:**
```json
{"entries": "file1.md\nfile2.md\ndir1/"}
// or
{"error": "Path not found: ..."}
```

**Security:**
- Same path validation as `read_file`
- Skips hidden files and `__pycache__`

**Use for:** Discovering file structure, finding relevant files

#### `query_api(method: str, path: str, body: str?)`

Calls the backend LMS API to query data or check endpoint status.

**Parameters:**
- `method` (string, required): HTTP method (GET, POST, PUT, DELETE)
- `path` (string, required): API endpoint path (e.g., `/items/`, `/analytics/completion-rate`)
- `body` (string, optional): JSON request body for POST/PUT requests

**Returns:**
```json
{"status_code": 200, "body": {...}}
// or
{"error": "HTTP error: ..."}
```

**Authentication:**
- Uses `LMS_API_KEY` from `.env.docker.secret`
- Sent as `Authorization: Bearer <LMS_API_KEY>` header

**Use for:** Database queries, API status checks, analytics data, reproducing bugs

### Environment Configuration

The agent reads configuration from two environment files:

#### `.env.agent.secret` (LLM credentials)

```
LLM_API_KEY=my-secret-qwen-key
LLM_API_BASE=http://10.93.25.206:42005/v1
LLM_MODEL=qwen3-coder-plus
```

#### `.env.docker.secret` (LMS API credentials)

```
LMS_API_KEY=my-secret-api-key
AGENT_API_BASE_URL=http://localhost:42002
```

**Important:** Two distinct keys:
- `LMS_API_KEY` — protects backend endpoints (from `.env.docker.secret`)
- `LLM_API_KEY` — authenticates with LLM provider (from `.env.agent.secret`)

### LLM Provider

**Provider:** Qwen Code API
- **Model:** `qwen3-coder-plus`
- **Endpoint:** OpenAI-compatible chat completions API
- **Deployment:** Running on VM at `http://10.93.25.206:42005/v1`

**Why Qwen Code:**
- 1000 free requests per day
- Works from Russia without VPN
- No credit card required
- Strong tool calling support

## Agentic Loop

The agentic loop enables multi-step reasoning with up to 10 tool calls:

```
1. Initialize messages = [system_prompt, user_question]
2. Loop (max 10 iterations):
   a. Call LLM with messages + tool definitions
   b. If LLM returns tool_calls:
      - Execute each tool
      - Append assistant message + tool result to messages
      - Continue loop
   c. If LLM returns content (no tool_calls):
      - This is the final answer
      - Extract answer and source
      - Return JSON and exit
3. If max iterations reached:
   - Return partial answer from last tool result
```

### System Prompt

The system prompt guides tool selection:

**Use `list_files` + `read_file` for:**
- Wiki documentation questions (Git workflow, SSH, VM, Docker)
- Source code questions (what framework, how components work)
- Configuration questions (docker-compose.yml, Dockerfile)
- Understanding architecture or code flow

**Use `query_api` for:**
- Database queries ("How many items...", "What is the top learner...")
- API status checks ("What status code...", "Does endpoint X exist")
- Analytics data ("What is the completion rate...")
- Reproducing API errors or bugs

**For bug diagnosis:**
1. First use `query_api` to reproduce the error
2. Note the error message and status code
3. Use `read_file` to find the relevant source code
4. Identify the buggy line and explain the fix

## Data Flow

```
User Question: "How many items are in the database?"
       │
       ▼
┌─────────────────────────────────────────┐
│ 1. Build messages with system prompt    │
│    and user question                    │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│ 2. Call LLM API with tool definitions   │
└─────────────────────────────────────────┘
       │
       ▼
    Has tool_calls?
    ┌──────┴──────┐
   yes           no
    │             │
    ▼             │
┌───────────┐     │
│ 3. Execute│     │
│    tools  │     │
│  - query_ │     │
│    api    │     │
│  - read_  │     │
│    file   │     │
└───────────┘     │
    │             │
    │ Append      │
    │ results     │
    │ to messages │
    │             │
    └──────┬──────┘
           │
           ▼
    Loop back to step 2
           │
           ▼ (no tool_calls)
┌─────────────────────────────────────────┐
│ 4. Extract answer and source            │
│    - answer: LLM's text content         │
│    - source: Last read_file path        │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│ 5. Output JSON to stdout                │
│ {"answer": "...",                       │
│  "source": "wiki/git-workflow.md#...",  │
│  "tool_calls": [...]}                   │
└─────────────────────────────────────────┘
```

## Output Format

```json
{
  "answer": "There are 120 items in the database.",
  "source": "",
  "tool_calls": [
    {
      "tool": "query_api",
      "args": {"method": "GET", "path": "/items/"},
      "result": {"status_code": 200, "body": [...]}
    }
  ]
}
```

**Fields:**
- `answer` (string, required): The LLM's text response
- `source` (string, optional): Wiki/source reference (empty for API queries)
- `tool_calls` (array, required): All tool calls made during the loop

## Error Handling

- **Missing API key:** Exit with error message to stderr
- **API timeout:** 60 second timeout per LLM call, 30 second for backend API
- **Path traversal:** Rejected with error message in tool result
- **File not found:** Returns error in tool result (doesn't crash)
- **Max tool calls:** Returns partial answer after 10 calls
- **Missing argument:** Show usage message, exit code 1
- **LLM API unavailable:** Returns mock response with error message

## Security

Path validation prevents directory traversal attacks:

1. Reject absolute paths
2. Reject paths containing `..`
3. Resolve to absolute path
4. Verify path is within project root using `Path.relative_to()`

API authentication:
- `LMS_API_KEY` read from environment (not hardcoded)
- Sent as Bearer token in Authorization header
- Separate from LLM API key

## Testing

Run tests with:

```bash
uv run pytest tests/test_agent.py -v
```

**Test coverage:**

| Test | Description |
|------|-------------|
| `test_agent_output` | Verifies JSON structure and required fields |
| `test_agent_missing_argument` | Verifies usage message on missing input |
| `test_documentation_agent_merge_conflict` | Verifies `read_file` for merge conflict question |
| `test_documentation_agent_list_wiki` | Verifies `list_files` for wiki listing question |
| `test_system_agent_framework_question` | Verifies structure for framework question |
| `test_system_agent_database_question` | Verifies structure for database query question |

## How to Run

1. Ensure `.env.agent.secret` exists with LLM credentials
2. Ensure `.env.docker.secret` exists with LMS API key
3. Ensure Qwen Code API is running on VM
4. Ensure backend services are running (Docker Compose)
5. Run: `uv run agent.py "Your question"`

**Example:**

```bash
uv run agent.py "How many items are in the database?"
uv run agent.py "What framework does the backend use?"
uv run agent.py "How do you resolve a merge conflict?"
```

## Benchmark Evaluation

Run the local benchmark:

```bash
uv run run_eval.py
```

This runs 10 questions across all categories:
- Wiki lookup (branch protection, SSH)
- System facts (framework, routers)
- Data queries (item count, status codes)
- Bug diagnosis (ZeroDivisionError, TypeError)
- Reasoning (request lifecycle, idempotency)

## Lessons Learned

### Challenge 1: Tool Selection

**Problem:** The LLM was calling `read_file` for database queries instead of `query_api`.

**Solution:** Enhanced the system prompt with explicit tool selection guide and improved tool descriptions. Added "Do NOT use for wiki documentation or source code questions" to `query_api` description.

### Challenge 2: API Authentication

**Problem:** Confusion between `LMS_API_KEY` and `LLM_API_KEY`.

**Solution:** Clear separation in config loading:
- `LLM_API_KEY` from `.env.agent.secret` for LLM provider
- `LMS_API_KEY` from `.env.docker.secret` for backend API

### Challenge 3: Error Handling

**Problem:** Agent crashed when LLM API was unavailable.

**Solution:** Added try-catch in `call_llm()` to return mock response instead of crashing. This allows testing even without network access.

### Challenge 4: Source Extraction

**Problem:** Source field was empty for API queries.

**Solution:** Made `source` optional in the output format. API queries don't need a source file reference.

## Task History

### Task 1: Call an LLM from Code

Basic CLI with no tools:
- Simple question → LLM → answer
- Output: `{"answer": "...", "tool_calls": []}`

### Task 2: The Documentation Agent

Added tools and agentic loop:
- Tools: `read_file`, `list_files`
- Agentic loop for multi-step reasoning
- Output: `{"answer": "...", "source": "...", "tool_calls": [...]}`

### Task 3: The System Agent

Added `query_api` tool and enhanced system prompt:
- New tool: `query_api(method, path, body)` for backend API calls
- Updated system prompt with tool selection guide
- Separate config for LLM and LMS API keys
- Output: Same format, `source` now optional

## Final Architecture Summary

The agent is a ~500 line Python CLI that:

1. **Reads configuration** from environment files (not hardcoded)
2. **Registers three tools** as function-calling schemas
3. **Runs an agentic loop** with up to 10 tool calls
4. **Outputs structured JSON** with answer, source, and tool history
5. **Handles errors gracefully** without crashing

Key design decisions:
- Tools are pure functions with validated inputs
- Agentic loop maintains conversation history
- System prompt guides tool selection explicitly
- Security: path validation prevents directory traversal
- Flexibility: environment variables allow different deployments
