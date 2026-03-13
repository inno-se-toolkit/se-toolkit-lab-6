# Agent Architecture

## Overview

This agent is a CLI tool that answers questions by calling a Large Language Model (LLM). It forms the foundation for the more advanced agents in Tasks 2–3, which will add tools and an agentic loop.

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│  Command Line   │ ──▶ │   agent.py   │ ──▶ │  LLM API    │ ──▶ │  Answer  │
│  "What is REST?"│     │  (Python)    │     │  (Qwen)     │     │  (JSON)  │
└─────────────────┘     └──────────────┘     └─────────────┘     └──────────┘
```

## Components

### 1. Environment Loading

The agent reads configuration from `.env.agent.secret`:

| Variable | Purpose |
|----------|---------|
| `LLM_API_KEY` | API key for authentication |
| `LLM_API_BASE` | Base URL of the LLM API endpoint |
| `LLM_MODEL` | Model name (e.g., `qwen3-coder-plus`) |

### 2. Argument Parsing

The agent accepts a single command-line argument — the user's question:

```bash
uv run agent.py "Your question here"
```

### 3. LLM Client

The agent makes an HTTP POST request to the LLM API:

- **Endpoint:** `{LLM_API_BASE}/chat/completions`
- **Method:** POST
- **Headers:** `Authorization: Bearer {LLM_API_KEY}`, `Content-Type: application/json`
- **Body:**
  ```json
  {
    "model": "qwen3-coder-plus",
    "messages": [{"role": "user", "content": "<question>"}]
  }
  ```

### 4. Response Parsing

The agent extracts the answer from the LLM response:

```python
answer = data["choices"][0]["message"]["content"]
```

### 5. Output

The agent outputs a single JSON line to stdout:

```json
{"answer": "...", "tool_calls": []}
```

All debug and error output goes to **stderr** to keep stdout clean for JSON parsing.

## LLM Provider

**Provider:** Qwen Code API (via qwen-code-oai-proxy)

**Model:** `qwen3-coder-plus`

**Why this choice:**
- Works from Russia without VPN
- 1000 free requests per day
- OpenAI-compatible API (easy integration)
- Strong code understanding capabilities

## Error Handling

| Error | Behavior |
|-------|----------|
| Missing environment variables | Print error to stderr, exit code 1 |
| Network timeout (>60s) | Print error to stderr, exit code 1 |
| Invalid API response | Print error to stderr, exit code 1 |
| Missing question argument | Print usage to stderr, exit code 1 |

## Usage

```bash
# Basic usage
uv run agent.py "What does REST stand for?"

# Example output
{"answer": "Representational State Transfer.", "tool_calls": []}
```

## File Structure

```
agent.py              # Main CLI script
.env.agent.secret     # LLM credentials (gitignored)
AGENT.md              # This documentation
plans/task-1.md       # Implementation plan
```

## Next Steps (Tasks 2–3)

In Task 2, the agent will gain:
- `read_file` tool — read files from the project
- `list_files` tool — list directory contents
- Agentic loop — iterate between tool calls and LLM reasoning

In Task 3, the agent will gain:
- `query_api` tool — call the backend HTTP API
- Ability to answer data-dependent questions
