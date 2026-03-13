# Task 1 Plan: Call an LLM from Code

## Overview

Build a CLI program (`agent.py`) that takes a question as a command-line argument, sends it to an LLM via the OpenAI-compatible API, and returns a structured JSON response.

## LLM Provider and Model

- **Provider**: Qwen Code API (self-hosted on VM)
- **Model**: `qwen3-coder-plus`
- **API Base**: `http://localhost:42005/v1`
- **API Key**: Stored in `.env.agent.secret`

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  CLI Input  │────▶│   agent.py   │────▶│  Qwen Code API  │
│  (question) │     │  (parse,     │     │  (LLM inference)│
│             │     │   call LLM)  │     │                 │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ JSON Output │
                    │  (stdout)   │
                    └─────────────┘
```

## Implementation Steps

### 1. Environment Setup
- Read configuration from `.env.agent.secret`
- Use `python-dotenv` to load environment variables
- Validate required variables: `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL`

### 2. CLI Interface
- Accept question as first command-line argument
- Handle missing argument with usage message
- Exit with code 1 on error, 0 on success

### 3. LLM Integration
- Use `httpx` or `requests` to call the chat completions API
- Follow OpenAI-compatible format:
  - Endpoint: `POST /v1/chat/completions`
  - Headers: `Authorization: Bearer <key>`, `Content-Type: application/json`
  - Body: `{"model": "...", "messages": [{"role": "user", "content": "..."}]}`

### 4. Response Parsing
- Extract answer from LLM response (`choices[0].message.content`)
- Format as JSON: `{"answer": "...", "tool_calls": []}`
- Output to stdout (only valid JSON)
- Debug output to stderr

### 5. Error Handling
- Network errors: print to stderr, exit 1
- Invalid API response: print to stderr, exit 1
- Missing environment variables: print to stderr, exit 1

## Data Flow

1. User runs: `uv run agent.py "What is REST?"`
2. Agent loads `.env.agent.secret`
3. Agent constructs API request to LLM
4. LLM returns response
5. Agent parses response and outputs JSON to stdout

## Testing Strategy

Create one regression test (`tests/test_task1.py`):
- Run `agent.py` as subprocess with a test question
- Parse stdout as JSON
- Assert `answer` field exists and is non-empty
- Assert `tool_calls` field exists and is an array

## Files to Create/Modify

- `agent.py` - main CLI (new)
- `plans/task-1.md` - this plan (new)
- `AGENT.md` - documentation (new)
- `tests/test_task1.py` - regression test (new)
- `.env.agent.secret` - environment config (already created)

## Acceptance Criteria Checklist

- [ ] Plan document exists
- [ ] `agent.py` outputs valid JSON with `answer` and `tool_calls`
- [ ] API key loaded from `.env.agent.secret`
- [ ] Debug output goes to stderr
- [ ] Exit code 0 on success
- [ ] 1 regression test passes
