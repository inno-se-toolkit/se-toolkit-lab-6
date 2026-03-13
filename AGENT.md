# Agent

A simple CLI agent that answers questions using an LLM API.

## Architecture

The agent is a Python script (`agent.py`) that uses an **agentic loop** to interact with an LLM and execute tools.

1. **Input**: A question passed as a command-line argument.
2. **Configuration**: Environment variables loaded from `.env.agent.secret`.
3. **Agentic Loop**:
   - The agent sends the question and a set of **tool definitions** to the LLM.
   - If the LLM requests a tool call, the agent executes it locally and feeds the result back to the LLM.
   - This process repeats until the LLM provides a final answer or reaches a limit of 10 tool calls.
4. **Output**: A JSON object printed to `stdout` containing `answer`, `source` (wiki reference), and a history of `tool_calls`. All logs/errors go to `stderr`.

## Tools

The agent has access to the following tools:

- `list_files(path)`: Lists files and directories at a given path within the project root.
- `read_file(path)`: Reads the content of a file within the project root.

Security: Both tools check that the requested path is within the project directory to prevent directory traversal attacks.

## LLM Provider

- **Provider**: Qwen Code API (running on VM).
- **Model**: `qwen3-coder-plus`.

## System Prompt Strategy

The agent is instructed via a system prompt to:
1. Discover relevant files in the `wiki/` directory using `list_files`.
2. Read the content of those files using `read_file`.
3. Provide a concise answer and cite the source as `wiki/filename.md#section-anchor`.
4. Format the final output as a JSON object.

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
