# Task 1: Call an LLM from Code

## LLM Provider and Model

- **Provider:** Qwen Code API
- **Model:** `qwen3-coder-plus`
- **API Base:** `http://<vm-ip>:<port>/v1` (OpenAI-compatible endpoint)
- **API Key:** Stored in `.env.agent.secret` (not committed to git)

## Agent Structure

The agent will be a simple Python CLI script (`agent.py`) that:

1. **Reads configuration** from environment variables:
   - `LLM_API_KEY` — API key for authentication
   - `LLM_API_BASE` — Base URL of the LLM API
   - `LLM_MODEL` — Model name to use

2. **Parses command-line input:**
   - Takes the user question as the first command-line argument
   - Validates that a question was provided

3. **Calls the LLM API:**
   - Uses the OpenAI-compatible chat completions endpoint
   - Sends a simple user message with the question
   - Receives the text response from the model

4. **Formats and outputs the response:**
   - Wraps the answer in a JSON object with `answer` and `tool_calls` fields
   - `tool_calls` is an empty array (will be populated in Task 2)
   - Outputs valid JSON to stdout (single line)
   - All debug/logging output goes to stderr

## Libraries

- `python-dotenv` — to load environment variables from `.env.agent.secret`
- `requests` or `httpx` — to make HTTP requests to the LLM API
- `argparse` or `sys.argv` — to parse command-line arguments
- `json` — to format the output

## Error Handling

- Missing API key → exit with error message to stderr
- Missing question argument → exit with usage message to stderr
- API request failure → exit with error message to stderr
- Timeout (60 seconds) → exit with error message to stderr

## Testing

One regression test will:
- Run `agent.py` as a subprocess with a test question
- Parse the JSON output from stdout
- Verify that `answer` field exists and is non-empty
- Verify that `tool_calls` field exists and is an array

## Files to Create

1. `plans/task-1.md` — this plan
2. `agent.py` — the main agent CLI
3. `AGENT.md` — documentation
4. `.env.agent.secret` — environment configuration (gitignored)
5. `tests/test_agent.py` — regression test
