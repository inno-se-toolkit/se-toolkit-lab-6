# Agent Architecture

## Overview

This agent is a CLI tool that calls an LLM to answer questions. It forms the foundation for the intelligent agent that will be built in subsequent tasks.

## LLM Provider

**Provider:** OpenRouter  
**Model:** `meta-llama/llama-3.3-70b-instruct:free`  
**API:** OpenAI-compatible chat completions API

### Configuration

The agent reads configuration from `.env.agent.secret`:

| Variable | Description |
|----------|-------------|
| `LLM_API_KEY` | OpenRouter API key |
| `LLM_API_BASE` | API base URL (`https://openrouter.ai/api/v1`) |
| `LLM_MODEL` | Model name (`meta-llama/llama-3.3-70b-instruct:free`) |

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│   CLI Arg   │ ──→ │  Env Loader  │ ──→ │ HTTP Client │ ──→ │   LLM API   │
│  (question) │     │ (.env file)  │     │  (httpx)    │     │  (OpenRouter)│
└─────────────┘     └──────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ↓
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│ JSON Output │ ←── │   Formatter  │ ←── │   Parser    │ ←── │  Response   │
│  (stdout)   │     │              │     │             │     │             │
└─────────────┘     └──────────────┘     └─────────────┘     └─────────────┘
```

## Components

### 1. Argument Parser
- Reads question from `sys.argv[1]`
- Validates input and shows usage on error

### 2. Environment Loader
- Loads `.env.agent.secret` from project root
- Extracts `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL`
- Exits with error if any required variable is missing

### 3. HTTP Client
- Uses `httpx` for HTTP requests
- Sends POST to `{LLM_API_BASE}/chat/completions`
- 60 second timeout
- Handles HTTP errors gracefully

### 4. Response Parser
- Parses JSON response from LLM
- Extracts content from `choices[0].message.content`

### 5. Output Formatter
- Outputs structured JSON to stdout
- Format: `{"answer": "...", "tool_calls": []}`
- All debug output goes to stderr

## Usage

```bash
# Run with a question
uv run agent.py "What does REST stand for?"

# Example output
{"answer": "Representational State Transfer.", "tool_calls": []}
```

## Error Handling

| Error | Behavior |
|-------|----------|
| Missing `.env.agent.secret` | Exit with error to stderr |
| Missing API key | Exit with error to stderr |
| Network error | Exit with error to stderr |
| Invalid response | Exit with error to stderr |
| No argument provided | Show usage to stderr |

## Dependencies

- `httpx` — HTTP client for API requests
- Standard library: `json`, `os`, `sys`, `pathlib`

## Testing

Run the regression test:

```bash
pytest backend/tests/unit/test_agent.py
```

The test verifies:
- Agent outputs valid JSON
- `answer` field is present and non-empty
- `tool_calls` field is present and is an array

## Limitations

- Free tier OpenRouter has 50 requests/day limit
- No tool calling support yet (Task 2)
- No agentic loop yet (Task 3)
- No access to project documentation yet (Task 3)
