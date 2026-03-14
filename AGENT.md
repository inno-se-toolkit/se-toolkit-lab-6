# Agent Documentation

## Overview
A CLI agent that takes a question, optionally uses tools to read project documentation, and returns a structured JSON answer.

## LLM Provider
- Provider: Qwen Code API (via qwen-code-oai-proxy on VM)
- Model: qwen3-coder-plus
- Base URL: configured in .env.agent.secret

## How to Run
```bash
uv run agent.py "Your question here"
```

## Output Format
```json
{"answer": "...", "source": "wiki/file.md#section", "tool_calls": [...]}
```

## Tools
- **read_file**: reads a file from the project directory by relative path
- **list_files**: lists files in a directory by relative path
- Both tools block path traversal outside the project directory

## Agentic Loop
1. Send question + tool definitions to LLM
2. If LLM responds with tool_calls → execute each tool, append results, repeat
3. If LLM responds with text → output final JSON and exit
4. Maximum 10 tool calls per question

## System Prompt
The agent is instructed to use list_files to discover wiki files, then read_file to find the answer, and include the source file path and section anchor.

## Architecture
```
question → LLM → tool_calls? → execute tools → LLM → ... → JSON output
```
