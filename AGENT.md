# Agent

A simple CLI agent that answers questions using an LLM API.

## Architecture

The agent is a Python script (`agent.py`) that uses the OpenAI-compatible chat completions API to interact with an LLM.

1. **Input**: A question passed as a command-line argument.
2. **Configuration**: Environment variables loaded from `.env.agent.secret`.
3. **Execution**: The script sends the question to the configured LLM and receives a text response.
4. **Output**: A JSON object printed to `stdout` in the format `{"answer": "...", "tool_calls": []}`. All logs/errors go to `stderr`.

## LLM Provider

- **Provider**: Qwen Code API (running on VM).
- **Model**: `qwen3-coder-plus`.

## Setup

1. Create and configure `.env.agent.secret`:
   ```bash
   cp .env.agent.example .env.agent.secret
   ```
2. Set the following variables in `.env.agent.secret`:
   - `LLM_API_KEY`: Your Qwen API key.
   - `LLM_API_BASE`: `http://<vm-ip>:42005/v1`
   - `LLM_MODEL`: `qwen3-coder-plus`

## Usage

Run the agent with a question:

```bash
uv run agent.py "What is REST?"
```

The output will be:

```json
{"answer": "Representational State Transfer.", "tool_calls": []}
```
