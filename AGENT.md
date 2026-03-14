# Lab Assistant Agent

A CLI agent that answers questions using an LLM with tool-calling capabilities.

## Quick Start

```bash
# 1. Configure LLM access
cp .env.agent.example .env.agent.secret
# Edit .env.agent.secret with your LLM credentials

# 2. Install dependencies
uv sync

# 3. Run the agent
uv run agent.py "What does REST stand for?"
```

## Architecture

### Input/Output

**Input:** Command line argument (question)

```bash
uv run agent.py "Your question here"
```

**Output:** JSON to stdout

```json
{
  "answer": "Representational State Transfer.",
  "source": "wiki/api.md#rest",
  "tool_calls": [
    {"tool": "read_file", "args": {"path": "wiki/api.md"}, "result": "..."}
  ]
}
```

**Logs:** All debug output goes to stderr

### Agentic Loop

The agent uses an iterative loop to answer questions:

```
Question → LLM (with tool schemas) → tool_calls?
                                      │
                                      yes
                                      │
                                      ▼
                              Execute tools → Append results as "tool" messages
                                      │
                                      ▼
                              Back to LLM (max 10 iterations)
                                      │
                                      no (final answer)
                                      │
                                      ▼
                              Extract answer + source → JSON output
```

1. Send user question + tool definitions to LLM
2. If LLM returns tool calls → execute each tool, append results, go to step 1
3. If LLM returns text without tool calls → that's the final answer
4. Maximum 10 tool calls per question

## Configuration

### Environment Variables

| Variable | Purpose | Source |
|----------|---------|--------|
| `LLM_API_KEY` | LLM provider API key | `.env.agent.secret` |
| `LLM_API_BASE` | LLM API endpoint URL | `.env.agent.secret` |
| `LLM_MODEL` | Model name | `.env.agent.secret` |
| `LMS_API_KEY` | Backend API key for `query_api` auth | `.env.docker.secret` |
| `AGENT_API_BASE_URL` | Base URL for `query_api` (default: `http://localhost:42002`) | Optional |

## LLM Provider

### OpenRouter API

**Model:** `qwen/qwen3-next-80b-a3b-instruct:free`

- Free tier: 8 requests/minute
- No credit card required
- OpenAI-compatible API

## Tools

The agent has three tools registered as function-calling schemas:

### `read_file`

Read a file from the project repository.

**Parameters:**
- `path` (string): Relative path from project root (e.g., `wiki/git-workflow.md`)

**Returns:** File contents as a string, or error message.

**Security:** Rejects paths containing `../` to prevent directory traversal.

### `list_files`

List files and directories at a given path.

**Parameters:**
- `path` (string): Relative directory path from project root (e.g., `wiki`)

**Returns:** Newline-separated list of entries.

**Security:** Rejects paths containing `../` and verifies path stays within project root.

### `query_api`

Call the backend API to query the running system.

**Parameters:**
- `method` (string): HTTP method (GET, POST, PUT, DELETE)
- `path` (string): API endpoint path (e.g., `/items/`)
- `body` (string, optional): JSON request body for POST/PUT

**Returns:** JSON string with `status_code` and `body`.

**Authentication:** Uses `LMS_API_KEY` from environment variables.

## System Prompt Strategy

The system prompt instructs the LLM to:

1. **Discover first** — Use `list_files` to find relevant files
2. **Read deeply** — Use `read_file` to read documentation and source code
3. **Query the system** — Use `query_api` for data-dependent questions
4. **Cite sources** — Include file path and section anchor in the answer
5. **Think step by step** — Call tools one at a time, not all at once
6. **Know when to stop** — Provide final answer when enough information is gathered

## Code Structure

```
agent.py
├── load_dotenv()                    # Load .env.agent.secret
├── OpenAI client                    # LLM connection
├── Tool implementations:
│   ├── read_file()                  # Read file with security checks
│   ├── list_files()                 # List directory with security checks
│   └── query_api()                  # HTTP API client with auth
├── get_tool_schemas()               # OpenAI function-calling schemas
├── execute_tool()                   # Tool dispatcher with caching
├── call_llm_with_retry()            # LLM call with exponential backoff
├── run_agentic_loop()               # Main loop: LLM → tools → feedback
├── create_system_prompt()           # System instructions
├── create_agent_response()          # JSON formatting
└── main()                           # Entry point
```

## Error Handling

| Error | Behavior |
|-------|----------|
| Missing API key | Exit 1, error JSON |
| Missing API base | Exit 1, error JSON |
| No question | Exit 1, error JSON |
| LLM error | Retry up to 3 times, then exit 1 |
| Tool error | Return error message as tool result |
| Timeout (60s) | Exit 1, error JSON |

## Testing

### Run the agent

```bash
# Real LLM (requires API key)
uv run agent.py "What does REST stand for?"

# Mock mode (no API key needed)
MOCK_MODE=true uv run agent.py "What does REST stand for?"
```

### Run tests

```bash
MOCK_MODE=true uv run pytest tests/test_agent.py -v
```

## Advanced Features

### Retry Logic with Exponential Backoff

Automatically retries failed requests on:
- 429 (Too Many Requests)
- 5xx (Server Errors)
- Connection/Timeout errors

**Backoff formula:**
```
delay = min(BASE_DELAY × 2^attempt + jitter, MAX_DELAY)
```

- `BASE_DELAY`: 1 second
- `MAX_DELAY`: 10 seconds
- `jitter`: 10% randomization

### In-Memory Caching

Caches tool call results to avoid redundant API calls.

**Cache key format:** `{tool_name}:{md5_hash(args)}`

### Security: Path Traversal Prevention

Tools validate paths to prevent accessing files outside the project root:

1. Reject any path containing `..`
2. Normalize path using `Path.resolve()`
3. Verify normalized path starts with project root

### Content Truncation

Large files and API responses are truncated to `MAX_CONTENT_LENGTH` (8000 characters) to avoid token limits.

## Lessons Learned

### Tool Design

- **Clear descriptions matter:** The LLM needs precise tool descriptions to know when to use each tool
- **Parameter naming:** Use intuitive names that match natural language
- **Error messages:** Return helpful error messages as tool results so the LLM can adapt

### Agentic Loop

- **Iteration limit:** The 10-call limit prevents infinite loops while allowing complex multi-step queries
- **Message history:** Appending tool results as "tool" role messages helps the LLM understand the conversation flow
- **Stop condition:** The loop stops when the LLM returns content without tool calls

### Prompt Engineering

- **Explicit instructions:** Tell the LLM exactly how to use tools and cite sources
- **Step-by-step reasoning:** Encourage the LLM to think through the problem
- **Language matching:** Respond in the same language as the question

## Benchmark Performance

The agent is evaluated against 10 local questions plus hidden questions from the autochecker:

| Category | Questions | Tools Required |
|----------|-----------|----------------|
| Wiki lookup | 2 | `read_file` |
| System facts | 3 | `read_file`, `list_files` |
| Data queries | 2 | `query_api` |
| Bug diagnosis | 2 | `query_api`, `read_file` |
| Reasoning | 1 | `read_file` |

**Grading:**
- Keyword matching for factual questions
- LLM-based judging for open-ended reasoning questions
- Tool usage verification (must use correct tools)

## License

Same as project root.
