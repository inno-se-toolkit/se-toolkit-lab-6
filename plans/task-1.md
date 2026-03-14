# Task 1: Call an LLM from Code

## LLM Provider
- Provider: Qwen Code API (via qwen-code-oai-proxy on VM)
- Model: qwen3-coder-plus
- Base URL: http://10.93.26.16:42005/v1

## Implementation Plan
1. Parse the question from command-line arguments
2. Load API credentials from .env.agent.secret
3. Send the question to the LLM via OpenAI-compatible API
4. Parse the response
5. Output JSON with `answer` and `tool_calls` fields to stdout
