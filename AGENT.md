# Agent Architecture

## Overview

This is a simple CLI agent that connects to an LLM and returns structured JSON answers. It serves as the foundation for more complex agent functionality in later tasks.

## LLM Provider

**Provider:** Qwen Code API
**Model:** `qwen3-coder-plus`

The agent uses an OpenAI-compatible API endpoint, which allows it to work with various providers that support the same interface.

## Configuration

The agent reads configuration from `.env.agent.secret` in the project root:

| Variable | Description |
|----------|-------------|
| `LLM_API_KEY` | API key for the LLM provider |
| `LLM_API_BASE` | Base URL of the API endpoint (e.g., `http://vm-ip:port/v1`) |
| `LLM_MODEL` | Model name to use (e.g., `qwen3-coder-plus`) |

## How It Works

### Input
```bash
uv run agent.py "What does REST stand for?"
```

### Processing Flow
1. Parse command-line argument (the question)
2. Load environment variables from `.env.agent.secret`
3. Create HTTP client with OpenAI-compatible endpoint
4. Send POST request to `/chat/completions` with:
   - System prompt: "You are a helpful assistant..."
   - User message: the question
5. Extract the answer from the LLM response

### Output
```json
{"answer": "Representational State Transfer.", "tool_calls": []}
```

- Only valid JSON is written to stdout
- All debug/progress messages go to stderr
- Exit code 0 on success

## Dependencies

- `openai` - OpenAI-compatible API client (not used directly, using httpx instead)
- `httpx` - HTTP client for API calls
- `python-dotenv` - Environment variable loading
- `json` - JSON serialization (stdlib)

## Usage

### Setup
1. Copy `.env.agent.example` to `.env.agent.secret`
2. Fill in your LLM credentials:
   - `LLM_API_KEY` - your API key
   - `LLM_API_BASE` - API endpoint URL
   - `LLM_MODEL` - model name

### Run
```bash
uv run agent.py "Your question here"
```

## Error Handling

| Error | Behavior |
|-------|----------|
| Missing argument | Print usage to stderr, exit 1 |
| Missing env vars | Print error to stderr, exit 1 |
| API error | Print error to stderr, exit 1 |
| Timeout (>60s) | HTTP client timeout, exit 1 |

## Testing

Run the regression test:
```bash
pytest backend/tests/agent/test_task1.py
```

The test verifies:
- `agent.py` runs successfully
- Output is valid JSON
- `answer` field exists
- `tool_calls` field exists and is an array
