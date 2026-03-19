# Task 1: Call an LLM from Code

## LLM Provider

**Provider:** OpenRouter  
**Model:** `meta-llama/llama-3.3-70b-instruct:free`  
**API Endpoint:** `https://openrouter.ai/api/v1/chat/completions`

**Why OpenRouter:**
- Free tier available (50 requests/day)
- No credit card required
- OpenAI-compatible API
- Works from Russia

## Agent Architecture

### Components

1. **Argument Parser** — reads the question from command-line argument (`sys.argv[1]`)
2. **Environment Loader** — reads `.env.agent.secret` for `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL`
3. **HTTP Client** — sends POST request to LLM API using `httpx` or `requests`
4. **Response Parser** — extracts answer from LLM response JSON
5. **Output Formatter** — outputs structured JSON to stdout

### Data Flow

```
CLI argument (question)
    ↓
Load env config (.env.agent.secret)
    ↓
Build HTTP request (POST /v1/chat/completions)
    ↓
Send to LLM API
    ↓
Parse response JSON
    ↓
Output: {"answer": "...", "tool_calls": []}
```

### Error Handling

- Missing API key → exit with error message to stderr
- Network error → retry or exit with error to stderr
- Invalid response → exit with error to stderr
- No argument provided → print usage to stderr

### Output Format

- **stdout:** Only valid JSON with `answer` and `tool_calls` fields
- **stderr:** All debug/log messages

## Dependencies

- `httpx` or `requests` — HTTP client
- `python-dotenv` — load environment from file
- `json` — standard library for JSON parsing

## Testing

One regression test:
- Run `agent.py "test question"` as subprocess
- Parse stdout JSON
- Verify `answer` field exists and is non-empty
- Verify `tool_calls` field exists and is array
