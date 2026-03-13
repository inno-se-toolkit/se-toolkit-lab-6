# Agent Architecture

## Overview

This agent is a CLI tool that connects to an LLM (Qwen Code API) and returns structured JSON answers to user questions. It forms the foundation for the more advanced agent with tools that will be built in Tasks 2-3.

## Architecture

```
User question (CLI arg) → agent.py → LLM API → JSON answer (stdout)
```

## Components

### 1. Settings (`AgentSettings`)

Loads configuration from `.env.agent.secret` using `pydantic-settings`:

- `LLM_API_KEY` — API key for authentication
- `LLM_API_BASE` — Base URL of the LLM endpoint
- `LLM_MODEL` — Model name to use

### 2. LLM Client (`call_llm`)

Makes HTTP POST requests to the OpenAI-compatible chat completions endpoint:

- **Endpoint:** `{LLM_API_BASE}/chat/completions`
- **Timeout:** 60 seconds
- **Request format:** Standard OpenAI chat completions API
- **Response parsing:** Extracts `choices[0].message.content`

### 3. CLI Interface (`main`)

- Parses command-line arguments (question as first argument)
- Validates settings file exists
- Calls the LLM and formats the response
- Outputs JSON to stdout, debug info to stderr

## LLM Provider

**Provider:** Qwen Code API (via qwen-code-oai-proxy on VM)

**Model:** `qwen3-coder-plus`

**Why this choice:**
- 1000 free requests per day
- Available from Russia
- No credit card required
- OpenAI-compatible API

## Usage

```bash
# Basic usage
uv run agent.py "What does REST stand for?"

# Output (stdout)
{"answer": "Representational State Transfer.", "tool_calls": []}
```

## Output Format

The agent outputs a single JSON line to stdout:

```json
{
  "answer": "The LLM's response text",
  "tool_calls": []
}
```

- `answer`: The text response from the LLM
- `tool_calls`: Empty array for Task 1 (will be populated in Task 2)

**Important:** Only valid JSON goes to stdout. All debug/progress output goes to stderr.

## Configuration

Create `.env.agent.secret` from `.env.agent.example`:

```bash
cp .env.agent.example .env.agent.secret
```

Fill in your credentials:

```env
LLM_API_KEY=your-api-key-here
LLM_API_BASE=http://<vm-ip>:<port>/v1
LLM_MODEL=qwen3-coder-plus
```

## Error Handling

- Missing settings file → exit code 1 with error message to stderr
- HTTP errors → raised as exceptions with details to stderr
- Invalid LLM response format → exit code 1 with parsing error to stderr
- Timeout (>60s) → httpx timeout exception

## Dependencies

- `httpx` — HTTP client for API requests
- `pydantic-settings` — Environment variable parsing
- Standard library: `json`, `os`, `sys`, `pathlib`
