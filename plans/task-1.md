# Task 1 Plan: Call an LLM from Code

## LLM Provider

**Provider:** Qwen Code API (via qwen-code-oai-proxy on VM)

**Model:** `qwen3-coder-plus`

**API Endpoint:** `http://127.0.0.1:42005/v1`

**Authentication:** API key stored in `.env.agent.secret` (not hardcoded)

**Why this choice:**
- Works from Russia
- 1000 free requests per day
- OpenAI-compatible API (easy to integrate)
- Already deployed on the VM

## Agent Architecture

### Input/Output Flow

```
Command line argument → agent.py → LLM API → JSON response → stdout
```

### Components

1. **Environment Loading**
   - Read `.env.agent.secret` using `python-dotenv` or `os.environ`
   - Extract: `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL`

2. **Argument Parsing**
   - Use `sys.argv[1]` to get the user question
   - Validate that a question was provided

3. **LLM Client**
   - Use `httpx` or `requests` to call the OpenAI-compatible API
   - Endpoint: `{LLM_API_BASE}/chat/completions`
   - Headers: `Authorization: Bearer {LLM_API_KEY}`, `Content-Type: application/json`
   - Body: `{"model": LLM_MODEL, "messages": [{"role": "user", "content": question}]}`

4. **Response Parsing**
   - Extract `choices[0].message.content` from API response
   - Format as JSON: `{"answer": "...", "tool_calls": []}`

5. **Output**
   - Print JSON to stdout (single line)
   - All debug/logging output to stderr
   - Exit code 0 on success

### Error Handling

- Network errors → print error to stderr, exit code 1
- Invalid API response → print error to stderr, exit code 1
- Missing environment variables → print error to stderr, exit code 1
- Timeout (>60 seconds) → let it fail naturally

## File Structure

```
agent.py              # Main CLI script
.env.agent.secret     # LLM credentials (gitignored)
plans/task-1.md       # This plan
AGENT.md              # Documentation (to be created)
tests/test_agent.py   # Regression test (to be created)
```

## Testing Strategy

1. Run `uv run agent.py "What is 2+2?"` manually
2. Verify JSON output has `answer` and `tool_calls` fields
3. Write regression test:
   - Run `agent.py` as subprocess
   - Parse stdout as JSON
   - Assert `answer` is a non-empty string
   - Assert `tool_calls` is an empty list

## Next Steps

1. ✅ Create this plan
2. Create `agent.py` with basic LLM integration
3. Test manually with a simple question
4. Create `AGENT.md` documentation
5. Write 1 regression test
