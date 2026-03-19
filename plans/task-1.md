# Task 1 Plan: Call an LLM from Code

## LLM Configuration
- Provider: Qwen Code API (self-hosted on VM)
- Model: qwen3-coder-plus
- API Base: http://10.93.26.71:8080/v1
- Auth: Bearer token from .env.agent.secret (LLM_API_KEY)

## Agent Architecture
1. Parse CLI argument (user question)
2. Load environment variables (LLM_API_KEY, LLM_API_BASE, LLM_MODEL)
3. Build OpenAI-compatible API request
4. Send POST request to LLM
5. Parse response and extract answer
6. Output JSON: {"answer": "...", "tool_calls": []}

## Error Handling
- API timeout: 60 second limit
- Network errors: print to stderr, exit code 1
- Invalid response: print to stderr, exit code 1

## Testing
- Run: uv run agent.py "What is 2+2?"
- Expect: Valid JSON with answer field