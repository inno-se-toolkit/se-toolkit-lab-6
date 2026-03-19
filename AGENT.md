# Agent Architecture

## Overview

`agent.py` is a minimal CLI agent for Task 1. It accepts a question as the first command-line argument, sends the question to an OpenAI-compatible chat completions API, and prints a single JSON object to stdout.

## LLM Provider

The agent uses Qwen Code API deployed on the VM.

Current model:

- `qwen3-coder-flash`

## Configuration

The agent reads these values from environment variables, with `.env.agent.secret` used as a local convenience file:

- `LLM_API_KEY`
- `LLM_API_BASE`
- `LLM_MODEL`

## Request Flow

1. Parse the question from the CLI arguments.
2. Load LLM configuration from the environment.
3. Send a `POST` request to `<LLM_API_BASE>/chat/completions`.
4. Request a short completion to reduce latency.
5. Extract the assistant message from the API response.
6. Print valid JSON to stdout:

```json
{"answer":"...","tool_calls":[]}
```

## Error Handling

- Missing CLI argument: print to stderr and exit non-zero.
- Missing or invalid environment variables: print to stderr and exit non-zero.
- Failed API request or malformed API response: print to stderr and exit non-zero.

## How To Run

Create the environment file:

```bash
cp .env.agent.example .env.agent.secret
```

Fill in:

- `LLM_API_KEY`
- `LLM_API_BASE`
- `LLM_MODEL`

Run the agent:

```bash
uv run agent.py "What does REST stand for?"
```

## Testing

The regression test runs `agent.py` as a subprocess, provides test LLM environment variables, parses stdout as JSON, and checks that the output contains `answer` and `tool_calls`.
