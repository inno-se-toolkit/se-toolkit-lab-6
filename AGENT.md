# Agent Architecture

## Overview

This is a simple LLM-powered question answering agent. It takes a question as a command-line argument, sends it to an LLM via an OpenAI-compatible API, and returns a structured JSON response.

## LLM Provider

- **Provider:** Qwen Code API
- **Model:** `qwen3-coder-plus`
- **API Type:** OpenAI-compatible chat completions API

Qwen Code provides 1000 free requests per day and works without a credit card.

## Architecture

```
User question → agent.py → LLM API → JSON answer
```

### Components

1. **Configuration Loader** (`load_config`)
   - Reads `.env.agent.secret` from the project root
   - Extracts `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL`
   - Validates that all required values are present

2. **LLM Client** (`call_llm`)
   - Makes HTTP POST request to `{api_base}/chat/completions`
   - Uses Bearer token authentication
   - Sends the user question as a chat message
   - Parses the response and extracts the answer
   - Handles timeouts (60s) and HTTP errors

3. **CLI Interface** (`main`)
   - Parses command-line arguments
   - Orchestrates the flow: config → LLM call → output
   - Outputs JSON to stdout
   - Sends debug info to stderr

## Output Format

The agent outputs a single JSON line to stdout:

```json
{"answer": "Representational State Transfer.", "tool_calls": []}
```

- `answer` (string): The LLM's response to the question
- `tool_calls` (array): Empty for Task 1, will contain tool invocations in Task 2

## Environment Configuration

Create `.env.agent.secret` in the project root:

```bash
cp .env.agent.example .env.agent.secret
```

Fill in the values:

```
LLM_API_KEY=your-qwen-api-key-here
LLM_API_BASE=http://localhost:8000/v1
LLM_MODEL=qwen3-coder-plus
```

> **Note:** This file is gitignored. Never commit API keys.

## Usage

```bash
uv run agent.py "What does REST stand for?"
```

All debug output goes to stderr, JSON result goes to stdout.

## Dependencies

- `httpx` — HTTP client for API calls
- `python-dotenv` — Environment variable loading

## Error Handling

- Missing API key → exit code 1, error to stderr
- Missing question argument → exit code 1, usage message to stderr
- API timeout (60s) → exit code 1, error to stderr
- HTTP error → exit code 1, error details to stderr
- Unexpected response format → exit code 1, error to stderr

## Future Extensions (Tasks 2-3)

- Add tool definitions and tool calling support
- Implement the agentic loop (plan → act → observe)
- Add domain knowledge from the wiki
- Expand the system prompt
