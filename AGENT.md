# Agent Architecture

## Overview

This agent is a CLI tool that answers questions using a Large Language Model (LLM). It serves as the foundation for the more advanced agents built in Tasks 2–3.

## LLM Provider

**Provider:** Qwen Code API

**Deployment:** Remote (on VM)

**Model:** `qwen3-coder-plus`

**Why Qwen Code:**
- 1000 free requests per day
- Works from Russia without VPN
- No credit card required
- OpenAI-compatible API endpoint

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐     ┌──────────────┐
│   User      │────▶│  agent.py   │────▶│ Qwen Code API   │────▶│ Qwen 3 Coder │
│  (CLI arg)  │     │  (Local)    │     │   (VM:42005)    │     │   (Cloud)    │
└─────────────┘     └─────────────┘     └─────────────────┘     └──────────────┘
```

## Components

### 1. Environment Configuration (`.env.agent.secret`)

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_API_KEY` | API key for authentication | `my-secret-api-key` |
| `LLM_API_BASE` | Base URL of Qwen Code API | `http://10.93.26.94:42005/v1` |
| `LLM_MODEL` | Model name | `qwen3-coder-plus` |

### 2. Agent CLI (`agent.py`)

**Input:** Question as command-line argument

**Output:** JSON to stdout with structure:
```json
{"answer": "...", "tool_calls": []}
```

**Process:**
1. Parse command-line argument (question)
2. Load environment variables from `.env.agent.secret`
3. Send POST request to `LLM_API_BASE/chat/completions`
4. Parse LLM response
5. Extract answer from response
6. Output JSON to stdout
7. All debug output to stderr

## Usage

```bash
# Run with a question
uv run agent.py "What does REST stand for?"

# Output (stdout only)
{"answer": "REST stands for Representational State Transfer...", "tool_calls": []}
```

## Error Handling

| Error | Behavior |
|-------|----------|
| Missing arguments | Exit 1, usage message to stderr |
| Missing env vars | Exit 1, error message to stderr |
| Network timeout | Return JSON with error message, exit 1 |
| HTTP error | Return JSON with error message, exit 1 |
| Invalid response | Return JSON with error message, exit 1 |

## Files

- `agent.py` — Main agent CLI
- `.env.agent.secret` — Environment configuration (gitignored)
- `plans/task-1.md` — Implementation plan
- `tests/test_agent.py` — Regression tests

## Testing

Run tests:
```bash
uv run pytest tests/test_agent.py -v
```

## Future Extensions (Tasks 2–3)

- Add tools (file read, API query, etc.)
- Implement agentic loop
- Add system prompt with domain knowledge
- Support for multi-turn conversations
