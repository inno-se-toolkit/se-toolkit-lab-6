# AGENT.md

## Overview
This agent is a simple CLI program for Task 1 of Lab 6.

It:
1. Accepts a question from the command line.
2. Sends the question to an OpenAI-compatible LLM API.
3. Prints a structured JSON response to stdout.

## LLM provider
Qwen Code API

## Model
`qwen3-coder-plus`

## Files
- `agent.py` — main CLI agent
- `.env.agent.secret` — secret LLM configuration
- `plans/task-1.md` — implementation plan

## Environment variables
The agent reads these values from `.env.agent.secret`:
- `LLM_API_KEY`
- `LLM_API_BASE`
- `LLM_MODEL`

## Run
```bash
uv run agent.py "What does REST stand for?"