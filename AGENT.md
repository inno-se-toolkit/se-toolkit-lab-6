# Agent Architecture Documentation

## Overview

This document describes the architecture of the agent CLI system built across tasks 1-3. The agent is a Python CLI that starts as a simple LLM caller and evolves into a full agentic system with tools and an iterative loop.

## Task 1: Basic LLM Caller

### Architecture

The initial agent is a simple CLI that:

1. Takes a user question as input
2. Calls an LLM via OpenAI-compatible API
3. Returns structured JSON output

### Components

**Main File: `agent.py`**

- **CLI Interface**: Accepts a question argument and outputs JSON to stdout
- **LLM Configuration**: Reads from environment variables (`LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL`)
- **HTTP Client**: Uses `httpx` for async API calls
- **Error Handling**: Validates configuration and handles network errors gracefully

### Configuration

The agent reads LLM credentials from `.env.agent.secret`:

```bash
LLM_API_KEY=your-api-key
LLM_API_BASE=https://openrouter.ai/api/v1
LLM_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

### LLM Provider: OpenRouter

**Choice**: OpenRouter free tier (meta-llama/llama-3.3-70b-instruct:free)

**Rationale**:

- No credit card required for free tier
- Strong tool-calling support (important for tasks 2-3)
- Globally accessible (works in Russia)
- 50 requests/day free (sufficient for development)
- Straightforward OpenAI-compatible API

**Alternative**: Qwen Code API on personal VM (recommended for production)

### Output Format (Task 1)

```json
{
  "answer": "The answer from the LLM",
  "tool_calls": []
}
```

- `answer`: The text response from the LLM
- `tool_calls`: Empty array (populated in tasks 2-3)

### Usage

```bash
uv run agent.py "What does REST stand for?"
```

### Error Handling

- Missing environment variables → Clear error message
- Network errors → Caught and reported to stderr
- Invalid API responses → Parsed and handled gracefully
- Exit code 0 on success, 1 on failure

## Task 2: Documentation Agent with Agentic Loop

### Architecture Changes

The agent now implements a proper **agentic loop**:

```
Question + Tool Schemas
    ↓
   LLM
    ├─ Returns tool calls → Execute tools → Add results to history → Loop
    └─ Returns text → Extract answer and source → Done
```

### Tools Added

#### `read_file(path: str) -> str`

Reads file contents from the project repository.

- **Input**: Relative path (e.g., `wiki/git-workflow.md`)
- **Output**: File contents or error message
- **Security**: Validates path doesn't escape project root (blocks `../` traversal)
- **Size**: Truncates large files at 50KB to avoid overwhelming the LLM

#### `list_files(path: str) -> str`

Lists files and directories at a path.

- **Input**: Directory path (e.g., `wiki`)
- **Output**: Newline-separated list of entries
- **Security**: Same path validation as `read_file`

### Tool Schemas

Tools are defined as JSON schemas in `get_tool_schemas()` and sent to the LLM's function-calling API.

The LLM decides which tool to call based on the question and previous results.

### The Agentic Loop

1. **Initialize**: Create message history with system prompt and user question
2. **Loop** (max 10 iterations):
   - Send messages + tool schemas to LLM
   - If LLM returns tool calls:
     - Execute each tool
     - Add tool result to message history as "tool" role message
     - Continue loop
   - If LLM returns only text:
     - Extract answer and source
     - Return JSON and exit
3. **Timeout**: If 10 iterations reached, return best answer so far

### System Prompt Strategy

The system prompt instructs the LLM to:

1. Use `list_files` to explore available documentation
2. Use `read_file` to find answers
3. Include file path references in answers
4. Be concise and direct

### Output Format (Task 2)

```json
{
  "answer": "The answer text from the LLM",
  "source": "wiki/git-workflow.md#resolving-merge-conflicts",
  "tool_calls": [
    {"tool": "list_files", "args": {"path": "wiki"}, "result": "file1.md\nfile2.md\n..."},
    {"tool": "read_file", "args": {"path": "wiki/git-workflow.md"}, "result": "File contents..."}
  ]
}
```

- `answer`: Final answer from LLM
- `source`: File path or section that provided the answer (can be empty for general questions)
- `tool_calls`: Array of all tool calls made (name, args, result)

### Message History Management

Messages are accumulated throughout the loop:

```python
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": question},
]

# After LLM's tool calling response:
messages.append({"role": "assistant", "content": response["content"]})

# After tool execution:
messages.append({
    "role": "tool",
    "tool_call_id": tool_call_id,
    "content": tool_result,
})
```

This allows the LLM to reason over multiple tools and results.

### Error Handling

- **File not found**: Tool returns error message, LLM handles gracefully
- **Path escape attempt**: Blocked with `Path.resolve()` validation
- **Tool execution errors**: Caught and added to message history
- **Max iterations**: Returns best answer with `tool_calls` array showing attempts

### Key Implementation Details

- Tool names are extracted from LLM's function call response
- Tool arguments are JSON-parsed from LLM's response
- Path validation prevents directory traversal attacks
- Large files are truncated to prevent context overflow
- All debug output goes to stderr, only JSON to stdout

## Task 3: System Agent with API Queries

### Architecture Changes

The agent now has three tools:

1. **read_file** - Read documentation and source code
2. **list_files** - Discover available files
3. **query_api** - Query the backend API for runtime data

### New Tool: `query_api`

**Purpose**: Query the backend API to get data about items, interactions, analytics, and system status.

**Parameters**:

- `method` (string): HTTP method (GET, POST, PUT, DELETE)
- `path` (string): API endpoint (e.g., `/items/`, `/analytics/completion-rate`)
- `body` (string, optional): JSON request body for POST/PUT

**Authentication**: Uses `LMS_API_KEY` from environment

**Response Format**: JSON with `status_code` and `body`

### Environment Variables (Task 3)

The agent reads all configuration from environment variables:

- `LLM_API_KEY` - LLM provider API key (`.env.agent.secret`)
- `LLM_API_BASE` - LLM API endpoint (`.env.agent.secret`)
- `LLM_MODEL` - Model name (`.env.agent.secret`)
- `LMS_API_KEY` - Backend API authentication key (`.env.docker.secret`)
- `AGENT_API_BASE_URL` - Backend API base URL (optional, default: `http://localhost:42002`)

### System Prompt Update (Task 3)

The system prompt now teaches the LLM to choose the right tool:

```
You have three tools:
1. read_file/list_files - For questions about code, docs, and architecture
2. query_api - For runtime questions about data and system status

Examples:
- "How many items in database?" → Use query_api on /items/
- "What's the framework?" → Use read_file on backend files
- "Explain the architecture" → Use read_file on architecture docs
```

### Benchmark Questions (Task 3)

The agent must pass 10 local questions in `run_eval.py`:

| # | Question | Primary Tool | Expected Keywords |
|----|----------|--------------|-------------------|
| 0 | Protect a branch on GitHub | read_file | branch, protect |
| 1 | Connect to VM via SSH | read_file | ssh, key OR connect |
| 2 | Python web framework | read_file | FastAPI |
| 3 | API router modules | list_files | items, interactions, analytics, pipeline |
| 4 | Items in database | query_api | number > 0 |
| 5 | 401 status code | query_api | 401 OR 403 |
| 6 | ZeroDivisionError bug | query_api + read_file | ZeroDivisionError OR division by zero |
| 7 | TypeError in top-learners | query_api + read_file | TypeError OR None OR NoneType OR sorted |
| 8 | Request lifecycle | read_file (LLM judge) | ≥4 hops: Caddy → FastAPI → auth → router → ORM → PostgreSQL |
| 9 | ETL idempotency | read_file (LLM judge) | external_id, duplicates skipped |

### Debugging Workflow

**Common Issues**:

- Agent doesn't call `query_api` → Improve tool description or try `--index` flag to test one question
- 401 errors → Verify `LMS_API_KEY` is set in `.env.docker.secret`
- Wrong endpoint format → Check path construction in `query_api`
- Connection refused → Verify backend is running with `docker ps`

**Testing**:

```bash
# Run all benchmarks
uv run run_eval.py

# Test single question
uv run run_eval.py --index 4

# Check backend health
curl -H "Authorization: Bearer my-secret-api-key" http://localhost:42002/items/
```

### Implementation Highlights

- **Stateless**: Each agent run is independent (no persistent state)
- **Environment-driven**: All config from env vars, not hardcoded
- **Secure**: Validates paths, checks API keys, handles errors gracefully
- **Extensible**: Easy to add more tools by defining schemas and implementing functions
- **Debuggable**: Logs tool calls and LLM responses to stderr

---

## Testing

See `tests/` directory for regression tests that verify:

- JSON output structure with answer, source, and tool_calls
- Tool execution (read_file and list_files)
- API query capabilities
- Proper tool call tracking

---

## Future Enhancements

- Support for Qwen Code API on VM (higher rate limits)
- Tool schema auto-discovery
- Streaming responses
- Caching for frequently accessed files
- Parallel tool execution
