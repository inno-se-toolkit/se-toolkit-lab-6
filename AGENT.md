# Agent Architecture

## Overview

This agent is a CLI tool that connects to a Large Language Model (LLM) to answer user questions. It serves as the foundation for a more advanced agentic system that will be built in subsequent tasks.

## Architecture

### Components

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   User Input    │────▶│   agent.py   │────▶│    LLM API      │
│  (CLI argument) │     │  (Python)    │     │ (Qwen Code API) │
└─────────────────┘     └──────────────┘     └─────────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │  JSON Output │
                       │  (stdout)    │
                       └──────────────┘
```

### Data Flow

1. **Input Parsing**: The agent reads a question from the command-line argument
2. **Environment Loading**: LLM configuration is loaded from environment variables
3. **API Call**: The agent sends the question to the LLM via HTTP POST
4. **Response Parsing**: The LLM response is extracted and formatted
5. **Output**: A JSON object with `answer` and `tool_calls` fields is printed to stdout

## LLM Provider

**Provider:** Google AI Studio (Gemini)  
**Model:** `gemini-2.5-flash`

**Why Google Gemini:**

- Free tier available
- Fast response times
- Strong performance on reasoning tasks
- Reliable API with good uptime

## Configuration

The agent reads the following environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_API_KEY` | API key for authentication | `AIza...` (Google AI Studio) |
| `LLM_API_BASE` | Base URL for the LLM API | `https://generativelanguage.googleapis.com/v1beta` |
| `LLM_MODEL` | Model name to use | `gemini-2.5-flash` |

These variables should be set in `.env.agent.secret` (not committed to git).

**Supported APIs:**

- Google AI Studio (Gemini) - default
- OpenAI-compatible APIs (Qwen Code API, OpenRouter, etc.)

## Usage

```bash
# Set up environment
cp .env.agent.example .env.agent.secret
# Edit .env.agent.secret with your LLM credentials

# Run the agent
uv run agent.py "What does REST stand for?"
```

### Output Format

```json
{"answer": "Representational State Transfer.", "tool_calls": []}
```

- `answer`: The LLM's response to the question
- `tool_calls`: Empty array for Task 1 (will be populated in Task 2)

## Error Handling

- **Missing environment variables**: Exits with error message to stderr
- **API request failure**: Exits with HTTP error details to stderr
- **Invalid response format**: Exits with parsing error to stderr

All error messages go to **stderr**; only valid JSON goes to **stdout**.

## File Structure

```
.
├── agent.py              # Main CLI entry point
├── .env.agent.secret     # LLM configuration (gitignored)
├── .env.agent.example    # Example configuration
├── plans/task-1.md       # Implementation plan
├── test_agent.py         # Regression tests
└── AGENT.md              # This documentation
```

## Testing

Run the regression tests:

```bash
uv run pytest test_agent.py -v
```

The test verifies that:

1. The agent outputs valid JSON
2. The `answer` field is present and non-empty
3. The `tool_calls` field is present and is an array

## Future Work (Tasks 2-3)

- **Task 2**: Add tool support (file read/write, API queries)
- **Task 3**: Implement agentic loop with tool selection and execution
