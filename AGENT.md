# Agent Architecture

## Overview

This agent is a CLI tool that answers questions about the project by calling a Large Language Model (LLM) with **tools**. The agent can:
- List files in directories (`list_files`)
- Read file contents (`read_file`)
- Use an **agentic loop** to iteratively discover and read relevant wiki files

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│  Command Line   │ ──▶ │   agent.py   │ ──▶ │  LLM API    │ ──▶ │  Answer  │
│  "How do I      │     │  (Python +   │     │  (Qwen)     │     │  (JSON   │
│  resolve merge  │     │   Tools)     │     │  + Tools    │     │  + Source│
│  conflict?"     │     └──────────────┘     └─────────────┘     └──────────┘
└─────────────────┘
```

## Components

### 1. Environment Loading

The agent reads configuration from `.env.agent.secret`:

| Variable | Purpose |
|----------|---------|
| `LLM_API_KEY` | API key for authentication |
| `LLM_API_BASE` | Base URL of the LLM API endpoint |
| `LLM_MODEL` | Model name (e.g., `qwen3-coder-plus`) |

### 2. Tools

The agent has two tools that the LLM can call:

#### `read_file`
Reads the contents of a file from the project repository.

- **Parameters:** `path` (string) — relative path from project root
- **Returns:** File contents as string, or error message
- **Security:** Validates path to prevent directory traversal (`..` not allowed)

#### `list_files`
Lists files and directories in a directory.

- **Parameters:** `path` (string) — relative directory path from project root
- **Returns:** Newline-separated list of entries
- **Security:** Validates path to prevent directory traversal

### 3. Agentic Loop

The agent uses an iterative loop to answer questions:

```
1. Send user question + tool definitions to LLM
2. Parse response:
   - If tool_calls: 
     a. Execute each tool
     b. Append assistant message + tool results to conversation
     c. Go to step 1
   - If content (no tool_calls):
     a. Extract answer
     b. Extract source reference
     c. Return JSON and exit
3. Max 10 iterations (prevents infinite loops)
```

**Key insight:** After each tool call, we must append BOTH the assistant's message (with tool_calls) AND the tool response to the conversation history. This lets the LLM understand the full context.

### 4. System Prompt

The system prompt guides the LLM to use tools effectively:

```
You are a documentation assistant for a software engineering lab project.
You have access to tools that let you read files and list directories in the project wiki.

When asked a question:
1. First use `list_files` to discover relevant wiki files in the 'wiki' directory
2. Then use `read_file` to read the contents of relevant files
3. Find the answer in the file contents
4. Provide the answer with a source reference (file path + section anchor)
```

### 5. Output Format

```json
{
  "answer": "Edit the conflicting file, choose which changes to keep, then stage and commit.",
  "source": "wiki/git-workflow.md#resolving-merge-conflicts",
  "tool_calls": [
    {
      "tool": "list_files",
      "args": {"path": "wiki"},
      "result": "api.md\ngit.md\n..."
    },
    {
      "tool": "read_file",
      "args": {"path": "wiki/git.md"},
      "result": "# Git\n\nGit is a version control..."
    }
  ]
}
```

## LLM Provider

**Provider:** Qwen Code API (via qwen-code-oai-proxy)

**Model:** `qwen3-coder-plus`

**Why this choice:**
- Works from Russia without VPN
- 1000 free requests per day
- OpenAI-compatible API with tool calling support
- Strong code understanding capabilities

## Tool Calling Format

The agent uses the OpenAI-compatible tool calling format:

```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "read_file",
        "description": "...",
        "parameters": {
          "type": "object",
          "properties": {...},
          "required": ["path"]
        }
      }
    }
  ],
  "tool_choice": "auto"
}
```

The LLM responds with:
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "tool_calls": [{
        "id": "call_...",
        "function": {
          "name": "read_file",
          "arguments": "{\"path\": \"wiki/git.md\"}"
        }
      }]
    }
  }]
}
```

## Path Security

Both tools validate paths to prevent directory traversal:

```python
def validate_path(path: str) -> Path:
    # Reject paths with '..'
    if ".." in path:
        raise ValueError(f"Path traversal not allowed: {path}")
    
    # Resolve to absolute path
    project_root = Path(__file__).parent.resolve()
    full_path = (project_root / path).resolve()
    
    # Ensure path is within project root
    if not str(full_path).startswith(str(project_root)):
        raise ValueError(f"Path outside project: {path}")
    
    return full_path
```

## Error Handling

| Error | Behavior |
|-------|----------|
| Missing environment variables | Print error to stderr, exit code 1 |
| Network timeout (>60s) | Print error to stderr, exit code 1 |
| Invalid API response | Print error to stderr, exit code 1 |
| Path traversal attempt | Return error message as tool result |
| Max iterations reached | Return partial answer with tool_calls so far |

## Usage

```bash
# Basic usage
uv run agent.py "What files are in the wiki?"

# Question requiring file reading
uv run agent.py "How do you resolve a merge conflict?"

# Example output
{
  "answer": "...",
  "source": "wiki/git.md#merge-conflict",
  "tool_calls": [...]
}
```

## File Structure

```
agent.py              # Main CLI script with tools and agentic loop
.env.agent.secret     # LLM credentials (gitignored)
AGENT.md              # This documentation
plans/task-2.md       # Implementation plan
tests/test_agent.py   # Regression tests (3 tests)
```

## Testing

Run tests with:
```bash
uv run pytest tests/test_agent.py -v
```

Tests:
1. `test_agent_returns_valid_json` — Basic JSON output validation
2. `test_agent_uses_list_files_tool` — Verifies list_files is called for wiki questions
3. `test_agent_uses_read_file_for_merge_conflict` — Verifies read_file and source extraction

## Lessons Learned

1. **Tool message order matters:** When sending tool results back to the LLM, you must first append the assistant's message (with tool_calls), then append the tool response. Skipping the assistant message causes API errors.

2. **Path validation is critical:** Without proper validation, tools could read sensitive files outside the project directory.

3. **System prompt design:** The system prompt needs to explicitly tell the LLM to use tools AND include source references. Without this, the LLM might answer from its training data.

4. **Debug output to stderr:** Keeping stdout clean for JSON parsing while logging to stderr makes debugging much easier.

## Next Steps (Task 3)

In Task 3, the agent will gain:
- `query_api` tool — call the backend HTTP API with authentication
- Ability to answer data-dependent questions (e.g., "How many items are in the database?")
- Environment variable configuration for `LMS_API_KEY` and `AGENT_API_BASE_URL`
