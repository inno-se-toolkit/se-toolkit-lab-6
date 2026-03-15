# Agent Documentation

## Overview
This agent is a simple CLI tool that connects to an LLM (Qwen Code API) and answers questions. It serves as the foundation for building a more complex agent with tools and agentic loops.

## LLM Provider
- **Provider**: Qwen Code API
- **Model**: qwen3-coder-plus (configurable via environment)
- **API Base**: Configurable via environment (default: http://localhost:3000/v1)
- **Authentication**: Bearer token via LLM_API_KEY

## Configuration
The agent reads configuration from environment variables:
- `LLM_API_KEY`: API key for authentication
- `LLM_API_BASE`: Base URL for the OpenAI-compatible API
- `LLM_MODEL`: Model name to use (e.g., qwen3-coder-plus)

## Usage
```bash
# Set up environment variables
export LLM_API_KEY=your-api-key
export LLM_API_BASE=http://localhost:3000/v1
export LLM_MODEL=qwen3-coder-plus

# Or use .env.agent.secret file
cp .env.agent.example .env.agent.secret
# Edit .env.agent.secret with your values

# Run the agent
uv run agent.py "What does REST stand for?"
