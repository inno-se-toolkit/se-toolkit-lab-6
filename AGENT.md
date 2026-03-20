# Agent Architecture

## Overview

This agent is a CLI tool that answers questions using a Large Language Model (LLM) with tools. It can navigate the project wiki, read files, and provide answers with source references.

## LLM Provider

**Provider:** OpenRouter (alternative: Qwen Code API)

**Model:** `meta-llama/llama-3.3-70b-instruct:free`

**Why OpenRouter:**

- Free tier available (50 requests/day)
- No credit card required
- OpenAI-compatible API endpoint

**Alternative: Qwen Code API**

- 1000 free requests per day
- Requires authentication via Qwen CLI on VM
- Model: `qwen3-coder-plus`

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐     ┌──────────────┐
│   User      │────▶│  agent.py   │────▶│  OpenRouter     │────▶│ Llama 3.3    │
│  (CLI arg)  │     │  (Local)    │     │   (Cloud API)   │     │   (Cloud)    │
└─────────────┘     └─────────────┘     └─────────────────┘     └──────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Tools     │
                    │ - read_file │
                    │ - list_files│
                    └─────────────┘
```

## Components

### 1. Environment Configuration (`.env.agent.secret`)

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_API_KEY` | API key for authentication | `sk-or-v1-...` |
| `LLM_API_BASE` | Base URL of LLM API | `https://openrouter.ai/api/v1` |
| `LLM_MODEL` | Model name | `meta-llama/llama-3.3-70b-instruct:free` |

### 2. Tools

#### `read_file`

Reads a file from the project repository.

**Parameters:**

- `path` (string): Relative path from project root

**Security:**

- Blocks path traversal (`../`)
- Blocks absolute paths
- Validates path is within project root

#### `list_files`

Lists files and directories at a given path.

**Parameters:**

- `path` (string): Relative directory path from project root

**Security:**

- Same as `read_file`
- Only lists directories, not file contents

### 3. Agentic Loop

```
1. Send user question + system prompt to LLM
2. Parse response for tool calls (TOOL_CALL: format)
3. If tool calls found:
   a. Execute each tool
   b. Append results to messages
   c. Go to step 1
4. If no tool calls:
   a. Extract answer and source
   b. Return JSON
5. Max 10 iterations
```

### 4. System Prompt

The system prompt instructs the LLM to:

1. Use `list_files` to discover relevant wiki files
2. Use `read_file` to read content from relevant files
3. Find the answer and identify the source
4. Use format: `TOOL_CALL: tool_name({"arg": "value"})`

## Usage

```bash
# Run with a question
uv run agent.py "How do you resolve a merge conflict?"

# Output (stdout only)
{
  "answer": "To resolve a merge conflict...",
  "source": "wiki/git-workflow.md#resolving-merge-conflicts",
  "tool_calls": [
    {"tool": "list_files", "args": {"path": "wiki"}, "result": "..."},
    {"tool": "read_file", "args": {"path": "wiki/git-workflow.md"}, "result": "..."}
  ]
}
```

## Output Format

| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | The LLM's answer to the question |
| `source` | string | Wiki file reference (e.g., `wiki/git-workflow.md#section`) |
| `tool_calls` | array | List of tool calls made during execution |

## Error Handling

| Error | Behavior |
|-------|----------|
| Missing arguments | Exit 1, usage message to stderr |
| Missing env vars | Exit 1, error message to stderr |
| Network timeout | Return JSON with error message, exit 1 |
| HTTP error | Return JSON with error message, exit 1 |
| Path traversal attempt | Return error from tool, continue loop |
| Max iterations | Return partial answer with tool_calls log |

## Files

- `agent.py` — Main agent CLI with tools and agentic loop
- `.env.agent.secret` — Environment configuration (gitignored)
- `plans/task-1.md` — Task 1 implementation plan
- `plans/task-2.md` — Task 2 implementation plan
- `tests/test_agent.py` — Regression tests
- `AGENT.md` — This documentation

## Testing

Run tests:

```bash
uv run pytest tests/test_agent.py -v
```

## Security

- Path validation prevents directory traversal
- All paths resolved relative to project root
- Tools cannot access files outside project

## Limitations

- Maximum 10 tool calls per question
- 60 second timeout per LLM request
- Free tier rate limits (OpenRouter: 50/day)
