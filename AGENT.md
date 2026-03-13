# Agent Architecture

## Overview

This agent is a CLI tool that connects to a Large Language Model (LLM) with tool support to answer user questions. It implements an agentic loop that allows the LLM to call tools, reason about results, and iterate until it finds an answer.

## Architecture

### Components (Task 2)

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   User Input    │────▶│   agent.py   │────▶│    LLM API      │
│  (CLI argument) │     │  (Python)    │     │ (Google Gemini) │
└─────────────────┘     └──────────────┘     └─────────────────┘
                              │  ▲
                              │  │
                        ┌─────┴──┴─────┐
                        │    Tools     │
                        │ - read_file  │
                        │ - list_files │
                        └──────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │  JSON Output │
                       │  (stdout)    │
                       └──────────────┘
```

### Agentic Loop

```
Question ──▶ LLM ──▶ tool call? ──yes──▶ execute tool ──▶ back to LLM
                     │
                     no
                     │
                     ▼
                JSON output
```

1. **Send question + tool schemas** to the LLM
2. **Parse LLM response:**
   - If `tool_calls` present: execute tools, append results, go to step 1
   - If no `tool_calls`: extract final answer, output JSON, exit
3. **Maximum 10 iterations** per question

### Data Flow

1. **Input Parsing**: The agent reads a question from the command-line argument
2. **Environment Loading**: LLM configuration is loaded from environment variables
3. **LLM Call with Tools**: The agent sends the question + tool schemas to the LLM
4. **Tool Execution**: If LLM requests tool calls, execute them and feed results back
5. **Final Answer**: When LLM provides answer without tool calls, output JSON
6. **Output**: A JSON object with `answer`, `source`, and `tool_calls` fields

## LLM Provider

**Provider:** Google AI Studio (Gemini)  
**Model:** `gemini-2.5-flash`

**Why Google Gemini:**

- Free tier available
- Fast response times
- Strong performance on reasoning tasks
- Built-in function calling support
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

- Google AI Studio (Gemini) - with full tool support
- OpenAI-compatible APIs (Qwen Code API, OpenRouter, etc.) - limited support

## Tools

### `read_file`

Read the contents of a file from the project repository.

**Parameters:**

- `path` (string, required): Relative path from project root (e.g., `wiki/git-workflow.md`)

**Returns:** File contents as a string, or error message if file doesn't exist.

**Security:** Prevents directory traversal attacks (`../`) by validating paths are within project root.

### `list_files`

List files and directories at a given path.

**Parameters:**

- `path` (string, required): Relative directory path from project root (e.g., `wiki`)

**Returns:** Newline-separated listing of files and directories.

**Security:** Prevents directory traversal attacks by validating paths are within project root.

### Tool Schema (Gemini API)

```python
tools = [
    {
        "functionDeclarations": [
            {
                "name": "read_file",
                "description": "Read the contents of a file...",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "path": {
                            "type": "STRING",
                            "description": "Relative path from project root"
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "list_files",
                "description": "List files and directories...",
                "parameters": {...}
            }
        ]
    }
]
```

## System Prompt

The system prompt instructs the LLM to:

1. Use `list_files` to discover wiki files when needed
2. Use `read_file` to read specific documentation files
3. Include source references (file path) in the answer
4. Call tools iteratively until confident in the answer

Example:

```
You are a documentation assistant with access to two tools:
- list_files: List files in a directory
- read_file: Read the contents of a file

When answering questions about the project:
1. Use list_files to explore the wiki directory structure
2. Use read_file to read relevant documentation files
3. Find the answer and cite the source (file path)
4. Only give a final answer when you have found the information
```

## Usage

```bash
# Set up environment
cp .env.agent.example .env.agent.secret
# Edit .env.agent.secret with your LLM credentials

# Run the agent
uv run agent.py "What files are in the wiki directory?"
uv run agent.py "How do you resolve a merge conflict?"
```

### Output Format

```json
{
  "answer": "Edit the conflicting file, choose which changes to keep, then stage and commit.",
  "source": "wiki/git-workflow.md#resolving-merge-conflicts",
  "tool_calls": [
    {"tool": "list_files", "args": {"path": "wiki"}, "result": "git-workflow.md\n..."},
    {"tool": "read_file", "args": {"path": "wiki/git-workflow.md"}, "result": "..."}
  ]
}
```

- `answer` (string): The LLM's response to the question
- `source` (string): The wiki section reference (file path + section anchor)
- `tool_calls` (array): All tool calls made during the agentic loop

## Error Handling

- **Missing environment variables**: Exits with error message to stderr
- **API request failure**: Exits with HTTP error details to stderr
- **Invalid response format**: Exits with parsing error to stderr
- **Path traversal attempt**: Returns error message instead of file contents
- **Maximum iterations exceeded**: Returns partial answer with available information

All error messages go to **stderr**; only valid JSON goes to **stdout**.

## File Structure

```
.
├── agent.py              # Main CLI entry point with agentic loop
├── .env.agent.secret     # LLM configuration (gitignored)
├── .env.agent.example    # Example configuration
├── plans/task-1.md       # Task 1 implementation plan
├── plans/task-2.md       # Task 2 implementation plan
├── test_agent.py         # Regression tests
├── wiki/                 # Project documentation (agent can read these)
└── AGENT.md              # This documentation
```

## Testing

Run the regression tests:

```bash
uv run pytest test_agent.py -v
```

Tests verify:

1. Agent outputs valid JSON with required fields
2. `read_file` tool works correctly
3. `list_files` tool works correctly
4. Tool calls are logged in output
5. Source field is populated

## Security

### Path Validation

The agent prevents directory traversal attacks:

```python
def is_safe_path(path: str) -> bool:
    abs_path = os.path.normpath(os.path.join(PROJECT_ROOT, path))
    return abs_path.startswith(str(PROJECT_ROOT))
```

This ensures tools cannot access files outside the project directory.

## Future Work (Task 3)

- Add more tools (write_file, query_api, etc.)
- Improve agentic loop with better error handling
- Add source extraction from file content
- Support for multiple LLM providers with tool calling
