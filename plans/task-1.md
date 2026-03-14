# Task 1 Plan: Call an LLM from Code

## Overview

Build a CLI agent (`agent.py`) that takes a question as input, sends it to an LLM, and returns a structured JSON response.

## LLM Provider

**Provider**: Qwen Code API (deployed on VM)
- **Model**: `qwen3-coder-plus`
- **API Base**: `http://10.93.25.206:42005/v1`
- **API Key**: Stored in `.env.agent.secret` (not hardcoded)

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  CLI Input  │────▶│   agent.py       │────▶│  Qwen Code API  │
│  (question) │     │  (Python CLI)    │     │  (on VM)        │
└─────────────┘     └──────────────────┘     └─────────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ JSON Output │
                    │ (to stdout) │
                    └─────────────┘
```

## Implementation Steps

1. **Environment Setup**
   - Read LLM configuration from `.env.agent.secret`
   - Use `python-dotenv` to load environment variables

2. **LLM Client**
   - Use OpenAI-compatible API format (chat completions)
   - Install `openai` or `httpx` for HTTP requests
   - Send POST request to `{LLM_API_BASE}/chat/completions`

3. **CLI Interface**
   - Parse command-line argument (question)
   - Handle missing argument with usage message

4. **Response Processing**
   - Extract answer from LLM response
   - Format as JSON: `{"answer": "...", "tool_calls": []}`
   - Output to stdout (valid JSON only)
   - Debug output to stderr

5. **Error Handling**
   - Handle API errors gracefully
   - Timeout after 60 seconds
   - Exit code 0 on success, non-zero on error

## Testing

- Run `uv run agent.py "What is 2+2?"`
- Verify JSON output has `answer` and `tool_calls` fields
- Check that only valid JSON goes to stdout

## Files to Create

- `agent.py` - Main CLI agent
- `tests/test_agent.py` - Regression test
- `AGENT.md` - Documentation (after implementation)
