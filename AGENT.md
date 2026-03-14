# Documentation for the `agent.py`

## Environment variables

The agent reads environment variables from `.env.agent.secret`.

| Variable | Description |
| -------- | ----------- |
| `LLM_API_KEY` | Authentication key for the LLM provider |
| `LLM_API_BASE` | Base URL for the LLM provider API |
| `LLM_MODEL` | Model name for the LLM provider |
| `LLM_TEMPERATURE` | Temperature for the LLM provider |

All variables are required.

## User input

```bash
uv run agent.py "Your prompt here"
```

## Agentic Loop

1. Send user prompt to LLM API
2. Parse response for text and tool use blocks
3. Execute requested tools and collect results
4. Send tool results back to LLM
5. Repeat until no more tool calls

## Tools

Tools are defined in `agent/tools.json`:

| Tool | Description |
| ---- | ----------- |
| `list_files` | List files/directories in a path |
| `read_file_content` | Read content of a file |

## Output

Console output with colors:

- **Green** — Assistant text
- **Yellow** — Tool execution
- **Blue** — Tool results

## Error handling

Catches network errors, timeouts, HTTP errors, and general exceptions. Exits with code `1` on error.