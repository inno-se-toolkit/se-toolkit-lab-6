# Agent Architecture

## Overview

This project implements a CLI agent (`agent.py`) that answers questions using an LLM (Large Language Model). The agent connects to a Qwen Code API endpoint and returns structured JSON responses.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  User (CLI)     │────▶│   agent.py       │────▶│  Qwen Code API      │
│  (question)     │     │  (Python CLI)    │     │  (LLM inference)    │
└─────────────────┘     └──────────────────┘     └─────────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  JSON Response   │
                        │  (stdout)        │
                        └──────────────────┘
```

## Components

### 1. `agent.py`

The main CLI program that:
- Parses command-line arguments (the user's question)
- Loads configuration from `.env.agent.secret`
- Calls the LLM API with the question
- Returns a structured JSON response

**Input:**
```bash
uv run agent.py "Your question here"
```

**Output:**
```json
{"answer": "The answer from the LLM", "tool_calls": []}
```

### 2. Configuration (`.env.agent.secret`)

Environment variables for LLM access:

```bash
LLM_API_KEY=my-secret-qwen-key
LLM_API_BASE=http://localhost:42005/v1
LLM_MODEL=qwen3-coder-plus
```

### 3. LLM Provider

**Provider:** Qwen Code API (self-hosted via `qwen-code-oai-proxy`)

- **Model:** `qwen3-coder-plus`
- **API Format:** OpenAI-compatible chat completions
- **Endpoint:** `POST /v1/chat/completions`

## Data Flow

1. User runs `uv run agent.py "What is REST?"`
2. `agent.py` loads `.env.agent.secret` using `python-dotenv`
3. Agent constructs HTTP POST request to LLM API:
   ```json
   {
     "model": "qwen3-coder-plus",
     "messages": [
       {"role": "system", "content": "You are a helpful assistant..."},
       {"role": "user", "content": "What is REST?"}
     ]
   }
   ```
4. LLM returns response with answer
5. Agent parses response and outputs JSON to stdout

## Error Handling

- **Missing config:** Exit code 1 with error message to stderr
- **Network errors:** Exit code 1 with error message to stderr
- **Invalid LLM response:** Exit code 1 with error message to stderr
- **Timeout (>60s):** Exit code 1 with timeout message to stderr

## Output Format

All output goes to **stdout** as a single JSON line:
```json
{"answer": "...", "tool_calls": []}
```

All debug/logging output goes to **stderr**.

## How to Run

1. Ensure `.env.agent.secret` exists with valid credentials
2. Run: `uv run agent.py "Your question"`

Example:
```bash
uv run agent.py "What does REST stand for?"
```

## Dependencies

- `httpx` - HTTP client for API calls
- `python-dotenv` - Environment variable loading
- `uv` - Python package manager and runner

## Testing

Run the regression test:
```bash
uv run pytest tests/test_task1.py -v
```

## Future Extensions (Tasks 2-3)

In subsequent tasks, the agent will be extended with:
- **Tools:** `read_file`, `list_files`, `query_api`
- **Agentic loop:** Iterative tool use until final answer
- **System prompt:** Domain knowledge for answering questions about the lab
