# Agent Architecture

## Overview

This agent is a CLI tool that answers questions by calling an LLM (Qwen Code API).

## LLM Provider

- **Provider:** Qwen Code API (self-hosted on VM)
- **Model:** qwen3-coder-plus
- **API Base:** http://10.93.26.71:8080/v1
- **Authentication:** Bearer token from `.env.agent.secret`

## How It Works

1. User runs: `uv run agent.py "Your question"`
2. Agent reads the question from command-line arguments
3. Agent loads configuration from `.env.agent.secret`:
   - `LLM_API_KEY` — API key for authentication
   - `LLM_API_BASE` — Base URL of the LLM API
   - `LLM_MODEL` — Model name to use
4. Agent sends a POST request to the LLM API
5. Agent parses the response and extracts the answer
6. Agent outputs JSON to stdout: `{"answer": "...", "tool_calls": []}`

## File Structure

- `agent.py` — Main agent CLI
- `.env.agent.secret` — LLM configuration (gitignored)
- `plans/task-1.md` — Implementation plan

## Usage

```bash
uv run agent.py "What is 2+2?"