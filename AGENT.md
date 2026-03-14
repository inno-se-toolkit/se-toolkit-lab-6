# Agent Architecture — Task 1

## Overview

This document describes the architecture of `agent.py` — a CLI tool that calls an LLM and returns structured JSON output.

## LLM Provider

- **Provider:** Qwen Code API
- **Model:** `qwen3-coder-plus`
- **API Base:** `http://<vm-ip>:42005/v1` (OpenAI-compatible endpoint)
- **Authentication:** API key stored in `.env.agent.secret`

## Architecture

```
User question → agent.py → LLM API → JSON answer
```

### Components

1. **CLI Argument Parsing** — Reads the question from `sys.argv[1]`
2. **Environment Loading** — Loads LLM credentials from `.env.agent.secret`
3. **LLM Client** — OpenAI-compatible client using the `openai` Python package
4. **Response Formatter** — Returns JSON with `answer` and `tool_calls` fields

### Data Flow

```python
Question (CLI arg) 
    → call_llm() 
    → client.chat.completions.create() 
    → JSON response {"answer": "...", "tool_calls": []}
```

## How to Run

```bash
# Run with a question
uv run agent.py "What does REST stand for?"

# Expected output (single JSON line to stdout)
{"answer": "Representational State Transfer.", "tool_calls": []}
```

## Environment Variables

Create `.env.agent.secret` (gitignored) with:

```text
LLM_API_KEY=your-api-key-here
LLM_API_BASE=http://<vm-ip>:42005/v1
LLM_MODEL=qwen3-coder-plus
```

## Output Format

- **stdout:** Single JSON line with `answer` and `tool_calls`
- **stderr:** Debug logs prefixed with `[DEBUG]`
- **Exit code:** 0 on success, 1 on error

## Error Handling

- Timeout: 60 seconds for LLM requests
- Invalid input: Prints usage to stderr, exits with code 1
- API errors: Returns JSON with `error` field, exits with code 1

## Testing

Run regression tests:

```bash
uv run pytest tests/test_agent.py -v
```

Tests verify:
- Valid JSON output with required fields
- Debug logs go to stderr, not stdout
