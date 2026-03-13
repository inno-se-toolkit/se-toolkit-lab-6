# Agent: LLM Caller

## What is this?

A Python script that asks questions to an AI and returns JSON answers.

## LLM Provider

- **Provider**: Qwen Code API (on VM)
- **Model**: qwen3-coder-plus
- **API**: <http://10.93.26.107:42005/v1>

## Setup

```bash
# Install dependencies
uv add openai python-dotenv

# Create config
cp .env.agent.example .env.agent.secret
# Edit .env.agent.secret with your VM details
