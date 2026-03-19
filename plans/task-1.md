# Task 1: Call an LLM from Code — Implementation Plan

## LLM Provider Choice

**Provider:** Qwen Code API (deployed on VM)

**Reasoning:**
- 1000 free requests per day
- Works from Russia without VPN
- No credit card required
- OpenAI-compatible API endpoint

**Model:** `qwen3-coder-plus` — recommended for strong tool calling capabilities (will be used in Task 2)

## Architecture

```
User (CLI) → agent.py → Qwen Code API (VM) → Qwen 3 Coder (Cloud)
```

### Components

1. **Environment Configuration** (`.env.agent.secret`)
   - `LLM_API_KEY` — API key for authentication
   - `LLM_API_BASE` — Base URL of Qwen Code API on VM (`http://<vm-ip>:42005/v1`)
   - `LLM_MODEL` — Model name (`qwen3-coder-plus`)

2. **Agent CLI** (`agent.py`)
   - Parse command-line argument (question)
   - Load environment variables from `.env.agent.secret`
   - Send POST request to LLM API (`/v1/chat/completions`)
   - Parse response and extract answer
   - Output JSON to stdout: `{"answer": "...", "tool_calls": []}`
   - All debug output to stderr

### Data Flow

1. User runs: `uv run agent.py "What is REST?"`
2. `agent.py` reads `.env.agent.secret` for API credentials
3. `agent.py` sends HTTP POST to `LLM_API_BASE/chat/completions`
4. Qwen Code API proxies request to Qwen cloud
5. Response received, parsed
6. JSON output to stdout

## Error Handling

- Network errors: catch and return error message in JSON
- Missing environment variables: exit with error message to stderr
- Invalid JSON response: exit with error code 1

## Testing Strategy

1. **Unit test:** Verify JSON output structure
2. **Integration test:** Run `agent.py` with a sample question, check response

## Files to Create

- `plans/task-1.md` — this plan
- `.env.agent.secret` — environment configuration
- `agent.py` — main agent CLI
- `AGENT.md` — documentation
- `tests/test_agent.py` — regression test (1 test)
