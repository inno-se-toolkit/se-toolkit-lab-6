# Agent Documentation

## Overview
A CLI agent that takes a question and returns a structured JSON answer using an LLM.

## LLM Provider
- Provider: Qwen Code API (via qwen-code-oai-proxy)
- Model: qwen3-coder-plus
- Base URL: configured in .env.agent.secret

## How to Run
```bash
uv run agent.py "Your question here"
```

## Output Format
```json
{"answer": "...", "tool_calls": []}
```

## Architecture
1. Parse question from command-line arguments
2. Load API credentials from .env.agent.secret
3. Send question to LLM via OpenAI-compatible API
4. Return JSON with answer and tool_calls fields
