# Agent Architecture

## Overview

This project implements a CLI agent (`agent.py`) that answers questions by calling an LLM API. The agent is the foundation for a more advanced agentic system with tool use (Tasks 2-3).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  agent.py    │────▶│  Qwen Code API (on VM)           │   │
│  │  (CLI)       │◀────│  OpenAI-compatible endpoint      │   │
│  └──────┬───────┘     └──────────────────────────────────┘   │
│         │                                                    │
│         │ 1. Read question from command line                 │
│         │ 2. Load config from .env.agent.secret              │
│         │ 3. Call LLM via HTTP POST                          │
│         │ 4. Parse response and output JSON                  │
│         ▼                                                    │
│  ┌──────────────────┐                                        │
│  │  JSON Output     │                                        │
│  │  {"answer": "...", "tool_calls": []}                     │
│  └──────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

## Components

### `agent.py`

Main CLI entry point. Responsibilities:
- Parse command-line arguments
- Load LLM configuration from `.env.agent.secret`
- Call the LLM API via HTTP
- Format and output structured JSON response

**Key functions:**
- `load_config()` - Reads environment variables from `.env.agent.secret`
- `call_llm(question, config)` - Makes HTTP POST to LLM API
- `main()` - Entry point, orchestrates the flow

### `.env.agent.secret`

Environment configuration file (not committed to git):
- `LLM_API_KEY` - API key for LLM authentication
- `LLM_API_BASE` - Base URL of the LLM API endpoint
- `LLM_MODEL` - Model name (default: `qwen3-coder-plus`)

### LLM Provider

**Provider:** Qwen Code API
- **Model:** `qwen3-coder-plus`
- **Endpoint:** OpenAI-compatible chat completions API
- **Deployment:** Running on VM at `http://10.93.25.206:42005/v1`

**Why Qwen Code:**
- 1000 free requests per day
- Works from Russia without VPN
- No credit card required
- Strong tool calling support (for future tasks)

## Data Flow

1. User runs: `uv run agent.py "What is REST?"`
2. Agent parses the question from command line
3. Agent loads config from `.env.agent.secret`
4. Agent sends POST request to `{LLM_API_BASE}/chat/completions`
5. LLM returns response with answer
6. Agent formats output as JSON: `{"answer": "...", "tool_calls": []}`
7. JSON output goes to stdout, debug info to stderr

## Output Format

```json
{
  "answer": "Representational State Transfer.",
  "tool_calls": []
}
```

**Fields:**
- `answer` (string, required): The LLM's text response
- `tool_calls` (array, required): Empty for Task 1, populated in Task 2

## Error Handling

- **Missing API key:** Exit with error message to stderr
- **API timeout:** 60 second timeout
- **Invalid response:** Exit with non-zero code
- **Missing argument:** Show usage message

## Testing

Run tests with:

```bash
uv run pytest tests/test_agent.py -v
```

**Test coverage:**
- `test_agent_output` - Verifies JSON structure and required fields
- `test_agent_missing_argument` - Verifies usage message on missing input

## How to Run

1. Ensure `.env.agent.secret` exists with valid credentials
2. Ensure Qwen Code API is running on VM
3. Run: `uv run agent.py "Your question"`

## Future Improvements (Tasks 2-3)

- Add tools: `read_file`, `list_files`, `query_api`
- Implement agentic loop for multi-step reasoning
- Add system prompt with domain knowledge
- Support conversation history
