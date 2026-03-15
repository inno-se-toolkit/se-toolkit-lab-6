# Task 1: Call an LLM from Code - Implementation Plan

## LLM Provider Choice
- **Provider**: Qwen Code API (running locally on VM)
- **Model**: qwen3-coder-plus
- **API Base**: http://localhost:3000/v1 (for VM) or http://<vm-ip>:3000/v1 (for local)
- **Reason**: Free tier (1000 requests/day), OpenAI-compatible API, works without credit card

## Agent Structure
The agent will:
1. Read configuration from environment variables (LLM_API_KEY, LLM_API_BASE, LLM_MODEL)
2. Take question as command-line argument
3. Send request to LLM API using OpenAI-compatible format
4. Parse response and output JSON with format: {"answer": "...", "tool_calls": []}
5. Use stderr for debug logging, stdout only for JSON output

## Implementation Details
- Use `requests` library for HTTP calls
- Use `python-dotenv` for loading .env file
- Error handling with appropriate exit codes
- 60-second timeout for LLM response
