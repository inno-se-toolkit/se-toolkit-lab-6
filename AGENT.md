# LLM Agent Documentation

## Overview
This agent (`agent.py`) is a simple CLI tool that sends questions to an LLM and returns structured JSON responses. It's the foundation for more complex agents with tool-calling capabilities in later tasks.

## Architecture
- **Input**: Question as command-line argument
- **Processing**: Sends question to LLM API
- **Output**: JSON with `answer` and `tool_calls` fields

## LLM Provider: Qwen Code API
- **Provider**: Qwen Code (1000 free requests/day)
- **Model**: qwen3-coder-plus
- **API Compatibility**: OpenAI-compatible chat completions API
- **Authentication**: API key stored in `.env.agent.secret`

## Setup Instructions

### 1. Environment Configuration
Copy the example environment file and edit it:
```bash
cp .env.agent.example .env.agent.secret