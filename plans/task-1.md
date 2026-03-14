# Task 1 Plan: Call an LLM from Code

## LLM Provider and Model

**Provider:** Qwen Code API (self-hosted on VM)
**Model:** `qwen3-coder-plus`

**Rationale:**
- 1000 free requests per day (sufficient for development and testing)
- Works from Russia without restrictions
- No credit card required
- OpenAI-compatible API format
- Strong tool calling capabilities (needed for Tasks 2-3)

**Environment variables** (stored in `.env.agent.secret`):
- `LLM_API_KEY` — API key for Qwen Code
- `LLM_API_BASE` — Base URL of Qwen Code API on VM (e.g., `http://<vm-ip>:8080/v1`)
- `LLM_MODEL` — Model name (`qwen3-coder-plus`)

## Agent Structure

### Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  CLI Input  │ ──▶ │  agent.py        │ ──▶ │  Qwen Code API  │
│  (question) │     │  (Python CLI)    │     │  (LLM)          │
└─────────────┘     └──────────────────┘     └─────────────────┘
                           │
                           ▼
                    ┌──────────────────┐
                    │  JSON Output     │
                    │  {answer, tools} │
                    └──────────────────┘
```

### Components

1. **Environment Loading**
   - Use `python-dotenv` to load `.env.agent.secret`
   - Read `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL`

2. **LLM Client**
   - Use `httpx` (already in dependencies) for HTTP requests
   - OpenAI-compatible chat completions format:
     ```json
     POST /chat/completions
     {
       "model": "qwen3-coder-plus",
       "messages": [{"role": "user", "content": "<question>"}],
       "max_tokens": 1024
     }
     ```

3. **Response Parsing**
   - Extract `choices[0].message.content` from API response
   - Format as JSON: `{"answer": "<content>", "tool_calls": []}`

4. **CLI Interface**
   - Parse command-line argument (question)
   - Validate input (non-empty question)
   - Output JSON to stdout, debug info to stderr
   - Exit code 0 on success, non-zero on error

5. **Error Handling**
   - Timeout: 60 seconds for API call
   - Network errors: return error JSON to stderr
   - Empty response: handle gracefully

### File Structure

```
se-toolkit-lab-6/
├── plans/
│   └── task-1.md          # This plan
├── .env.agent.secret      # LLM credentials (gitignored)
├── agent.py               # Main CLI agent
├── AGENT.md               # Documentation
└── backend/
    └── tests/
        └── agent/
            └── test_agent_task1.py  # Regression test
```

### Implementation Steps

1. Create `.env.agent.secret` from `.env.agent.example`
2. Implement `agent.py` with:
   - Argument parsing (`sys.argv`)
   - Environment loading (`python-dotenv`)
   - HTTP client (`httpx`)
   - JSON output formatting
3. Create `AGENT.md` documentation
4. Write regression test using `pytest` + `subprocess`
5. Test locally: `uv run agent.py "What is REST?"`
6. Commit plan first, then code (git workflow)

### Success Criteria

- `uv run agent.py "What does REST stand for?"` outputs valid JSON
- JSON contains `answer` (string) and `tool_calls` (empty array)
- Response time < 60 seconds
- API key not hardcoded (loaded from `.env.agent.secret`)
