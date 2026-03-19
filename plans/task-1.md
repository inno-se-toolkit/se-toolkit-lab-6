# Task 1 Plan

## Provider

Use Qwen Code API deployed on the VM.

## Model

Use `qwen3-coder-flash`.

## Configuration

Read `LLM_API_KEY`, `LLM_API_BASE`, and `LLM_MODEL` from environment variables via `.env.agent.secret`.

## CLI flow

1. Read the question from the first command-line argument.
2. Send a POST request to the OpenAI-compatible `/chat/completions` endpoint.
3. Pass the question as a user message.
4. Keep the completion short to reduce latency.
5. Extract the assistant response text.
6. Print JSON to stdout with `answer` and `tool_calls`.

## Output

The program returns:

- `answer`: string
- `tool_calls`: empty list

## Error handling

- Missing CLI argument -> print error to stderr and exit non-zero.
- Missing environment variables -> print error to stderr and exit non-zero.
- Failed HTTP request or invalid API response -> print error to stderr and exit non-zero.

## Testing

Create one regression test that runs `agent.py` as a subprocess, parses stdout JSON, and verifies `answer` and `tool_calls`.
