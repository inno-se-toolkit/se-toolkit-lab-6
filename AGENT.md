# Agent CLI — Documentation

## Overview

This project implements a command-line interface (CLI) agent (`agent.py`) that accepts questions from the user, sends them to a Large Language Model (LLM), and returns a structured response in JSON format.

At the current stage (Task 1), the agent performs basic plumbing: parse input, call the LLM, and format output. Tools and the agentic loop will be added in subsequent tasks (Tasks 2–3).

---

## Quick Start

### 1. Set Up the Environment

Create a configuration file for the LLM:

```bash
cp .env.agent.example .env.agent.secret
```

Edit the `.env.agent.secret` file and fill in the required parameters:

- `LLM_API_KEY` — your API key from the LLM provider
- `LLM_API_BASE` — base URL of the API endpoint
- `LLM_MODEL` — name of the model to use

### 2. Run the Agent

```bash
uv run agent.py "Your question here"
```

### 3. Example Output

```json
{"answer": "Representational State Transfer.", "tool_calls": []}
```

---

## LLM Provider

**Provider:** Qwen Code API (deployed on VM)

**Model:** `qwen3-coder-plus`

**Configuration:**

- `LLM_API_KEY` — API key for authentication
- `LLM_API_BASE` — OpenAI-compatible endpoint URL (example: `http://10.93.25.160:42005/v1`)
- `LLM_MODEL` — model name (`qwen3-coder-plus`)

---

## Architecture

### Component Flow

```
User CLI → agent.py → VM Proxy (port 42005) → Qwen Cloud LLM
```

### How It Works

1. **Input Parsing** — the agent reads the question from the first command-line argument
2. **Configuration Loading** — LLM credentials are loaded from `.env.agent.secret`
3. **LLM Call** — a POST request is sent to the OpenAI-compatible `/chat/completions` endpoint
4. **Response Formatting** — the LLM response is wrapped in a JSON object with `answer` and `tool_calls` fields
5. **Output** — a single JSON line is printed to stdout

### Output Routing

- **stdout** — only the final JSON response
- **stderr** — all debug, progress, and error messages

This separation allows the agent to be used in pipelines and scripts that parse JSON output.

---

## Project Structure

```
se-toolkit-lab-6/
├── agent.py              # Main CLI script
├── .env.agent.example    # Configuration template
├── .env.agent.secret     # Actual configuration (gitignored)
├── AGENT.md              # This documentation
└── backend/tests/        # Agent tests
```

---

## Input and Output Specification

### Input

One command-line argument containing the question:

```bash
uv run agent.py "What does REST stand for?"
```

### Output

A single JSON line with two required fields:

```json
{"answer": "Representational State Transfer.", "tool_calls": []}
```

**Fields:**

- `answer` (string) — the LLM's text response
- `tool_calls` (array) — empty array in Task 1, populated with tool invocations in Task 2+

---

## Error Handling

The agent exits with code 1 and prints an error message to stderr in the following cases:

- Missing `.env.agent.secret` file
- Missing required environment variables (`LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL`)
- HTTP errors (4xx, 5xx) from the LLM provider
- Request timeout (exceeds 60 seconds)
- Network errors during the request

On successful execution, the agent exits with code 0.

---

## Testing

Run the regression test:

```bash
uv run pytest backend/tests/unit/test_agent.py -v
```

The test verifies:

- `agent.py` executes successfully
- Output is valid JSON
- Required fields `answer` and `tool_calls` are present

---

## Future Extensions

### Task 2: Tools

- Define available tools (search, file operations, API calls)
- Populate `tool_calls` array with tool invocations from the LLM

### Task 3: Agentic Loop

- Implement the full loop: question → plan → tool calls → execute → answer
- Support multi-step reasoning and tool execution

---

## Requirements

- Python 3.10+
- Package manager `uv`
- Access to Qwen Code API (or compatible LLM provider)
- Configured `.env.agent.secret` file

---

## License

This project is part of a software engineering educational course.
