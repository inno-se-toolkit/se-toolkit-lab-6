# Agent Documentation

## Overview

This agent is a CLI tool that connects to an LLM (Qwen Code API) and returns structured JSON answers. It is the foundation for the agentic system that will be extended with tools and an agentic loop in Tasks 2-3.

## Architecture

### Components

1. **Config Loader** (`load_config()`)
   - Reads `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL` from environment variables
   - Validates all required variables are present
   - Exits with error code 1 if any are missing

2. **LLM Client** (`call_lllm()`)
   - Uses `httpx` library for HTTP requests
   - Sends POST request to `{LLM_API_BASE}/chat/completions`
   - Includes system prompt instructing JSON response format
   - 60-second timeout
   - Handles HTTP errors and timeouts

3. **Response Parser** (`parse_response()`)
   - Extracts content from API response
   - Handles markdown code blocks in response
   - Validates `answer` and `tool_calls` fields exist
   - Returns structured dict

4. **Main Entry Point** (`main()`)
   - Parses command-line argument (question)
   - Orchestrates the flow: config → LLM call → parse → output
   - Outputs JSON to stdout, debug info to stderr

### Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   CLI arg   │ ──→ │   agent.py  │ ──→ │  LLM API    │ ──→ │  JSON out   │
│  (question) │     │             │     │  (Qwen)     │     │  (stdout)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                          │
                          ↓
                   ┌─────────────┐
                   │  env vars   │
                   │  (config)   │
                   └─────────────┘
```

## LLM Provider

**Provider:** Qwen Code API
- **Model:** `qwen3-coder-plus`
- **API Compatibility:** OpenAI chat completions API
- **Why Qwen Code:**
  - 1000 free requests per day
  - Available in Russia
  - No credit card required
  - Strong tool-calling capabilities (for future tasks)

## Configuration

Create `.env.agent.secret` in the project root:

```bash
cp .env.agent.example .env.agent.secret
```

Fill in the values:

```env
LLM_API_KEY=your-api-key-here
LLM_API_BASE=http://<vm-ip>:<port>/v1
LLM_MODEL=qwen3-coder-plus
```

| Variable       | Required | Description           |
| -------------- | -------- | --------------------- |
| `LLM_API_KEY`  | Yes      | Qwen Code API key     |
| `LLM_API_BASE` | Yes      | API endpoint URL      |
| `LLM_MODEL`    | Yes      | Model name to use     |

> **Note:** The autochecker injects its own credentials during evaluation. Never hardcode these values.

## Usage

### Basic Usage

```bash
uv run agent.py "What does REST stand for?"
```

### Output Format

```json
{"answer": "Representational State Transfer.", "tool_calls": []}
```

### Exit Codes

- `0` — Success
- `1` — Error (missing config, HTTP error, JSON parse error, timeout)

## Output Streams

- **stdout:** Only valid JSON (for programmatic use)
- **stderr:** All debug/progress/error messages

This design allows piping the output to other tools:

```bash
uv run agent.py "Question" | jq .answer
```

## Error Handling

The agent handles the following error cases:

| Error Type          | Behavior                              |
| ------------------- | ------------------------------------- |
| Missing env vars    | Error message to stderr, exit 1       |
| HTTP error          | Error message to stderr, exit 1       |
| Timeout (>60s)      | Error message to stderr, exit 1       |
| Invalid JSON        | Error message to stderr, exit 1       |
| Missing fields      | Error message to stderr, exit 1       |

## Testing

Run the regression test:

```bash
uv run pytest backend/tests/unit/test_agent_task1.py -v
```

The test verifies:
- Agent runs successfully
- Output is valid JSON
- `answer` field exists and is non-empty
- `tool_calls` field exists and is an array

## Development

### Adding New Features

When extending the agent in Tasks 2-3:

1. **Tools:** Add tool definitions and execution logic
2. **Agentic Loop:** Implement ReAct or similar loop for multi-step reasoning
3. **Prompt Engineering:** Enhance system prompt with tool descriptions

### Code Style

- Type hints for all functions
- Docstrings for all public functions
- Error messages to stderr
- Functional decomposition for testability

## Files

| File               | Purpose                    |
| ------------------ | -------------------------- |
| `agent.py`         | Main CLI agent             |
| `.env.agent.secret`| Local configuration        |
| `AGENT.md`         | This documentation         |
| `plans/task-1.md`  | Implementation plan        |
