# Task 1: Call an LLM from Code - Implementation Plan

## LLM Provider and Model

**Provider:** Qwen Code API (deployed on VM)

**Why Qwen Code:**
- 1000 free requests per day
- Works from Russia
- No credit card required
- Recommended by the lab

**Model:** `qwen3-coder-plus`

**API Endpoint:** OpenAI-compatible chat completions API at `http://<vm-ip>:<port>/v1/chat/completions`

## Environment Setup

1. Copy `.env.agent.example` to `.env.agent.secret`
2. Fill in:
   - `LLM_API_KEY` - QWEN_API_KEY from `~/qwen-code-oai-proxy/.env` on VM
   - `LLM_API_BASE` - `http://<vm-ip>:<port>/v1`
   - `LLM_MODEL` - `qwen3-coder-plus`

## Agent Architecture

### Components

1. **Environment Loading**
   - Use `python-dotenv` to load variables from `.env.agent.secret`
   - Read `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL`

2. **Command-Line Interface**
   - Use `sys.argv` to get the question argument
   - Validate that a question was provided

3. **LLM Client**
   - Use `requests` library to make HTTP POST to the API
   - Send JSON payload with model and messages
   - Include API key in `Authorization: Bearer <key>` header

4. **Response Parsing**
   - Parse JSON response from API
   - Extract `choices[0].message.content` as the answer

5. **Output Formatting**
   - Build output JSON: `{"answer": "<content>", "tool_calls": []}`
   - Print to stdout using `json.dumps()`
   - All debug/logging output goes to stderr

### Data Flow

```
Command line argument → agent.py → HTTP POST → Qwen API → JSON response → Parse → Output JSON
```

## Error Handling

Potential errors to handle:
- Missing command-line argument → print usage to stderr, exit non-zero
- Missing `.env.agent.secret` or missing variables → error to stderr
- Network error / API unreachable → error to stderr
- API returns error status → error to stderr
- Invalid JSON response → error to stderr

## Implementation Steps

1. Set up `.env.agent.secret` with valid credentials
2. Create basic agent structure with argument parsing
3. Implement LLM API call using requests
4. Parse response and format JSON output
5. Add error handling
6. Test with sample questions
7. Write regression test

## Testing

Create one regression test that:
- Runs `uv run agent.py "What is 2+2?"` as subprocess
- Captures stdout
- Parses JSON output
- Asserts `answer` field exists and is non-empty
- Asserts `tool_calls` field exists and is an empty list

## Dependencies

Add to `pyproject.toml`:
- `python-dotenv` - for loading environment variables
- `requests` or `httpx` - for HTTP requests
