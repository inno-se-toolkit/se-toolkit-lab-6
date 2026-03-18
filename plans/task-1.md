# Task 1: Call an LLM from Code

## LLM Provider

- **Provider**: OpenRouter (openrouter.ai)
- **Model**: `meta-llama/llama-3.3-70b-instruct:free`
- **API**: OpenAI-compatible chat completions endpoint at `https://openrouter.ai/api/v1`
- **Authentication**: Bearer token via `LLM_API_KEY` environment variable

## Agent Structure

The agent (`agent.py`) will have the following components:

1. **Configuration loading**: Read environment variables from `.env.agent.secret`
   - `LLM_API_KEY` - API key for authentication
   - `LLM_API_BASE` - Base URL for the API
   - `LLM_MODEL` - Model identifier

2. **Input parsing**: Get the question from command-line argument (`sys.argv[1]`)

3. **API client**: Use `httpx` (already in project dependencies) to make HTTP POST request to the LLM API
   - Endpoint: `{LLM_API_BASE}/chat/completions`
   - Headers: `Authorization: Bearer {LLM_API_KEY}`, `Content-Type: application/json`
   - Body: Standard OpenAI chat completion format with user message

4. **Response parsing**: Extract the assistant's message content from the API response

5. **Output formatting**: Write JSON to stdout with required fields:
   - `answer`: The LLM's response text
   - `tool_calls`: Empty array (will be populated in Task 2)

## Error Handling

- **Missing API key**: Exit with error message to stderr, non-zero exit code
- **Missing question argument**: Exit with usage message to stderr
- **API timeout (>60s)**: Exit with timeout error to stderr
- **HTTP error**: Exit with status code and error message to stderr
- **Invalid JSON response**: Exit with parse error to stderr
- **All errors go to stderr**, only valid JSON output goes to stdout

## Testing Strategy

Create one regression test that:
1. Runs `agent.py` as a subprocess with a test question
2. Parses stdout as JSON
3. Verifies `answer` field exists and is non-empty string
4. Verifies `tool_calls` field exists and is an array

## Files to Create

1. `agent.py` - Main CLI agent
2. `AGENT.md` - Documentation of the agent architecture
3. `tests/test_agent.py` - Regression test (or similar location following project conventions)
