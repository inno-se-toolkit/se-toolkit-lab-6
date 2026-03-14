# Agent Documentation

## Overview

This project implements a CLI agent that connects to an LLM (Large Language Model) and answers questions. The agent is the foundation for more advanced features in subsequent tasks, including tool integration and agentic loops.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ┌──────────────┐     ┌──────────────────────────────────┐  │
│  │  agent.py    │────▶│  LLM Provider (Qwen Code API)    │  │
│  │  (CLI)       │◀────│  OpenAI-compatible API           │  │
│  └──────┬───────┘     └──────────────────────────────────┘  │
│         │                                                    │
│         │                                                    │
│  ┌──────┴───────┐                                            │
│  │  .env.agent  │  Configuration file                        │
│  │  .secret     │  (API key, base URL, model)                │
│  └──────────────┘                                            │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. agent.py

Main CLI entry point that:
- Parses command-line arguments (question)
- Loads configuration from `.env.agent.secret`
- Calls the LLM API via HTTP
- Returns structured JSON output

### 2. Configuration (.env.agent.secret)

Environment file containing:
- `LLM_API_KEY` — API key for authentication
- `LLM_API_BASE` — Base URL of the LLM API endpoint
- `LLM_MODEL` — Model name to use (e.g., `qwen3-coder-plus`)

### 3. LLM Provider

**Provider:** Qwen Code API (self-hosted on VM)
**Model:** `qwen3-coder-plus`

The API follows the OpenAI-compatible chat completions format:
- Endpoint: `POST /chat/completions`
- Authentication: Bearer token in `Authorization` header
- Request format:
  ```json
  {
    "model": "qwen3-coder-plus",
    "messages": [
      {"role": "system", "content": "..."},
      {"role": "user", "content": "Question"}
    ],
    "max_tokens": 1024
  }
  ```

## Usage

### Basic Usage

```bash
uv run agent.py "What does REST stand for?"
```

### Output Format

The agent outputs a single JSON line to stdout:

```json
{"answer": "Representational State Transfer.", "tool_calls": []}
```

Fields:
- `answer` (string): The LLM's response
- `tool_calls` (array): Empty for Task 1, populated in Task 2

### Error Handling

- Debug/progress output goes to stderr
- Exit code 0 on success
- Non-zero exit code on errors (missing config, API failure, etc.)
- 60-second timeout for API calls

## Setup

### Prerequisites

1. Python 3.14.2
2. `uv` package manager
3. Access to Qwen Code API (or alternative LLM provider)

### Configuration

1. Copy the example environment file:
   ```bash
   cp .env.agent.example .env.agent.secret
   ```

2. Edit `.env.agent.secret` and fill in:
   - `LLM_API_KEY`: Your API key
   - `LLM_API_BASE`: API base URL (e.g., `http://<vm-ip>:8080/v1`)
   - `LLM_MODEL`: Model name (default: `qwen3-coder-plus`)

### Running Tests

```bash
uv run pytest backend/tests/agent/test_agent_task1.py -v
```

## File Structure

```
se-toolkit-lab-6/
├── agent.py                 # Main CLI agent
├── AGENT.md                 # This documentation
├── .env.agent.example       # Example environment file
├── .env.agent.secret        # Actual configuration (gitignored)
├── plans/
│   └── task-1.md           # Implementation plan
└── backend/
    └── tests/
        └── agent/
            └── test_agent_task1.py  # Regression test
```

## Dependencies

- `httpx`: HTTP client for API calls
- `python-dotenv`: Environment variable loading
- `pydantic`: (future) for structured output validation

## Future Enhancements (Tasks 2-3)

- **Task 2:** Add tools (`read_file`, `list_files`, `query_api`)
- **Task 3:** Implement agentic loop for multi-step reasoning
- Populate `tool_calls` array with executed tool information
