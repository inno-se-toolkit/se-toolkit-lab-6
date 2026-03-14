\# Agent Documentation



\## Architecture

\- Simple CLI agent that calls Qwen Code API

\- Reads config from `.env.agent.secret`

\- Takes question as command-line argument

\- Outputs JSON with `answer` and `tool\_calls`



\## LLM Provider

\- Qwen Code API running on VM (10.93.26.90:8000)

\- Model: qwen3-coder-plus



\## Usage

```bash

uv run agent.py "What is REST?"



\## Tools (Task 2)

\- `list\_files(path)`: lists files in a directory

\- `read\_file(path)`: reads file contents



\## Agentic Loop

1\. Send question + tool definitions to LLM

2\. If tool\_calls → execute, append results, repeat

3\. If no tool\_calls → output final answer with `source`

4\. Max 10 iterations



\## Security

\- All paths are validated with `safe\_path()` to prevent directory traversal.

