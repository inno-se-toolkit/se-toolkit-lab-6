# Plan for Task 1: Call an LLM from Code

## LLM Provider

**Provider:** Qwen Code API (recommended)
**Model:** `qwen3-coder-plus`

### Configuration
- API key from `.env.agent.secret` (LLM_API_KEY)
- Base URL: `http://<vm-ip>:<port>/v1` (LLM_API_BASE)
- Model: `qwen3-coder-plus` (LLM_MODEL)

## Architecture

### Input
- Question passed as first command-line argument: `uv run agent.py "question"`

### Processing Flow
1. Parse command-line argument (sys.argv[1])
2. Load environment variables from `.env.agent.secret`
3. Create OpenAI-compatible client using `openai` package
4. Send user question to LLM with minimal system prompt
5. Receive response and extract the answer text

### Output
- Single JSON line to stdout: `{"answer": "...", "tool_calls": []}`
- All debug output to stderr
- Exit code 0 on success

## Error Handling
- Missing argument → print usage to stderr, exit 1
- Missing env vars → print error to stderr, exit 1
- API error → print error to stderr, exit 1
- Timeout (60s) → handled by HTTP client timeout

## Dependencies
- `openai` package for API calls (OpenAI-compatible client)
- `python-dotenv` for loading `.env.agent.secret`
- `json` for output formatting

## Testing
- One regression test: run agent.py, parse JSON output, verify `answer` and `tool_calls` fields exist
