# Task 1 Plan: Call an LLM from Code

## LLM Provider

**Provider:** Qwen Code API
- **Model:** `qwen3-coder-plus`
- **API Type:** OpenAI-compatible chat completions API
- **Why Qwen Code:** 1000 free requests per day, available in Russia, no credit card required

## Configuration

The agent reads configuration from environment variables:

| Variable       | Source              | Purpose              |
| -------------- | ------------------- | -------------------- |
| `LLM_API_KEY`  | `.env.agent.secret` | API authentication   |
| `LLM_API_BASE` | `.env.agent.secret` | API endpoint URL     |
| `LLM_MODEL`    | `.env.agent.secret` | Model name to use    |

## Agent Architecture

### Data Flow

```
CLI argument → agent.py → HTTP POST → LLM API → JSON parse → stdout
                              ↑
                         env vars
```

### Components

1. **Config Loader**
   - Read `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL` from environment
   - Validate all required variables are present
   - Exit with error if missing

2. **LLM Client**
   - Use `httpx` library (already in project dependencies)
   - POST request to `{LLM_API_BASE}/chat/completions`
   - Headers: `Authorization: Bearer {LLM_API_KEY}`, `Content-Type: application/json`
   - Body: messages array with system + user prompt
   - Timeout: 60 seconds

3. **Response Parser**
   - Extract `choices[0].message.content` from API response
   - Parse as JSON, validate `answer` and `tool_calls` fields
   - Output single JSON line to stdout

4. **Error Handling**
   - HTTP errors → stderr message, exit code 1
   - JSON parse errors → stderr message, exit code 1
   - Timeout → stderr message, exit code 1
   - All debug output → stderr only

### Prompt Design

**System prompt:** Instruct the model to respond with valid JSON containing `answer` and `tool_calls` fields.

**User prompt:** The question from command-line argument.

## Testing Strategy

**1 regression test:**
- Run `agent.py "What is 2+2?"` as subprocess
- Parse stdout as JSON
- Assert `answer` field exists and is non-empty string
- Assert `tool_calls` field exists and is array

## Files to Create

1. `plans/task-1.md` — this plan
2. `agent.py` — main CLI agent
3. `.env.agent.secret` — local config (copy from `.env.agent.example`)
4. `AGENT.md` — documentation
5. `backend/tests/unit/test_agent_task1.py` — regression test

## Acceptance Criteria Checklist

- [ ] Plan committed before code
- [ ] `agent.py` outputs valid JSON with `answer` and `tool_calls`
- [ ] Config from env vars only (no hardcoding)
- [ ] API key in `.env.agent.secret`
- [ ] `AGENT.md` documents architecture
- [ ] 1 regression test passes
- [ ] Git workflow followed
