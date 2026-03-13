# Documentation for the `agent.py`

## Environment variables

The agent reads environment variables from `.env.agent.secret`.

| Variable | Description |
| -------- | ----------- |
| `LLM_API_KEY` | Authentication key for the LLM provider |
| `LLM_API_BASE` | Base URL for the LLM provider API |
| `LLM_MODEL` | Model name for the LLM provider |
| `LLM_TEMPERATURE` | Temperature for the LLM provider |

## User input

The agent takes a user input from the command line.

```bash
uv run agent.py "Hello, how are you?"
```

## API calls

The agent makes API calls to the LLM provider.

## Output

The agent prints the response as a JSON object of the following format:

```json
{
  "answer": "Hello, how are you?",
  "tool_calls": []
}
```

- `answer` is the LLM response.
- `tool_calls` is an empty array.