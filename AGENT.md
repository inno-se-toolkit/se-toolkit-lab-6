# Agent Architecture

## Overview

This project implements a CLI agent (`agent.py`) that answers questions by calling an LLM API with tools. The agent can read documentation files and explore the project structure to find answers.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  agent.py    │────▶│  Qwen Code API (on VM)           │   │
│  │  (CLI)       │◀────│  OpenAI-compatible endpoint      │   │
│  └──────┬───────┘     └──────────────────────────────────┘   │
│         │                                                    │
│         │ Tools:                                             │
│         ├─ read_file(path) ──▶ Read file contents            │
│         ├─ list_files(path) ─▶ List directory entries        │
│         │                                                    │
│         │ Agentic Loop:                                      │
│         │ 1. Send question + tools to LLM                    │
│         │ 2. LLM returns tool calls (or final answer)        │
│         │ 3. Execute tools, append results                   │
│         │ 4. Repeat until answer or max 10 calls             │
│         ▼                                                    │
│  ┌──────────────────────────────────────────────────┐        │
│  │  JSON Output                                     │        │
│  │  {"answer": "...", "source": "...",              │        │
│  │   "tool_calls": [{"tool": "...", ...}]}          │        │
│  └──────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Components

### `agent.py`

Main CLI entry point with agentic loop.

**Key functions:**

| Function | Description |
|----------|-------------|
| `load_config()` | Reads environment variables from `.env.agent.secret` |
| `validate_path(path)` | Validates path is within project root (security) |
| `read_file(path)` | Tool: reads file contents |
| `list_files(path)` | Tool: lists directory entries |
| `execute_tool(name, args)` | Executes a tool by name |
| `call_llm(messages, config)` | Makes HTTP POST to LLM API with tools |
| `run_agentic_loop(question, config)` | Main loop: LLM → tool → LLM → answer |
| `extract_source_from_messages(messages)` | Extracts source reference from conversation |
| `main()` | Entry point |

### Tools

Two tools are registered as function-calling schemas:

#### `read_file(path: str)`

Reads the contents of a file from the project repository.

**Parameters:**
- `path` (string, required): Relative path from project root (e.g., `wiki/git-workflow.md`)

**Returns:**
```json
{"content": "file contents..."}
// or
{"error": "File not found: ..."}
```

**Security:**
- Rejects absolute paths
- Rejects paths with `..` (path traversal)
- Validates resolved path is within project root

#### `list_files(path: str)`

Lists files and directories at a given path.

**Parameters:**
- `path` (string, required): Relative directory path from project root (e.g., `wiki`)

**Returns:**
```json
{"entries": "file1.md\nfile2.md\ndir1/"}
// or
{"error": "Path not found: ..."}
```

**Security:**
- Same path validation as `read_file`
- Skips hidden files and `__pycache__`

### `.env.agent.secret`

Environment configuration file (not committed to git):

```
LLM_API_KEY=my-secret-qwen-key
LLM_API_BASE=http://10.93.25.206:42005/v1
LLM_MODEL=qwen3-coder-plus
```

### LLM Provider

**Provider:** Qwen Code API
- **Model:** `qwen3-coder-plus`
- **Endpoint:** OpenAI-compatible chat completions API
- **Deployment:** Running on VM at `http://10.93.25.206:42005/v1`

## Agentic Loop

The agentic loop enables multi-step reasoning:

```
1. Initialize messages = [system_prompt, user_question]
2. Loop (max 10 iterations):
   a. Call LLM with messages + tool definitions
   b. If LLM returns tool_calls:
      - Execute each tool
      - Append assistant message + tool result to messages
      - Continue loop
   c. If LLM returns content (no tool_calls):
      - This is the final answer
      - Extract answer and source
      - Return JSON and exit
3. If max iterations reached:
   - Return partial answer from last tool result
```

### System Prompt

The system prompt instructs the LLM to:

1. Use `list_files` to discover relevant wiki files
2. Use `read_file` to read specific files
3. Find the exact section that answers the question
4. Provide a source reference in format: `path/to/file.md#section-anchor`
5. Limit tool calls to what's necessary

## Data Flow

```
User Question: "How do you resolve a merge conflict?"
       │
       ▼
┌─────────────────────────────────────────┐
│ 1. Build messages with system prompt    │
│    and user question                    │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│ 2. Call LLM API with tool definitions   │
└─────────────────────────────────────────┘
       │
       ▼
    Has tool_calls?
    ┌──────┴──────┐
   yes           no
    │             │
    ▼             │
┌───────────┐     │
│ 3. Execute│     │
│    tools  │     │
│  - read_  │     │
│    file   │     │
│  - list_  │     │
│    files  │     │
└───────────┘     │
    │             │
    │ Append      │
    │ results     │
    │ to messages │
    │             │
    └──────┬──────┘
           │
           ▼
    Loop back to step 2
           │
           ▼ (no tool_calls)
┌─────────────────────────────────────────┐
│ 4. Extract answer and source            │
│    - answer: LLM's text content         │
│    - source: Last read_file path        │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│ 5. Output JSON to stdout                │
│ {"answer": "...",                       │
│  "source": "wiki/git-workflow.md#...",  │
│  "tool_calls": [...]}                   │
└─────────────────────────────────────────┘
```

## Output Format

```json
{
  "answer": "Edit the conflicting file, choose which changes to keep, then stage and commit.",
  "source": "wiki/git-workflow.md#resolving-merge-conflicts",
  "tool_calls": [
    {
      "tool": "list_files",
      "args": {"path": "wiki"},
      "result": {"entries": "git-workflow.md\n..."}
    },
    {
      "tool": "read_file",
      "args": {"path": "wiki/git-workflow.md"},
      "result": {"content": "..."}
    }
  ]
}
```

**Fields:**
- `answer` (string, required): The LLM's text response
- `source` (string, required): Wiki section reference (file path + section anchor)
- `tool_calls` (array, required): All tool calls made during the loop

## Error Handling

- **Missing API key:** Exit with error message to stderr
- **API timeout:** 60 second timeout per LLM call
- **Path traversal:** Rejected with error message in tool result
- **File not found:** Returns error in tool result (doesn't crash)
- **Max tool calls:** Returns partial answer after 10 calls
- **Missing argument:** Show usage message, exit code 1

## Security

Path validation prevents directory traversal attacks:

1. Reject absolute paths
2. Reject paths containing `..`
3. Resolve to absolute path
4. Verify path is within project root using `Path.relative_to()`

## Testing

Run tests with:

```bash
uv run pytest tests/test_agent.py -v
```

**Test coverage:**

| Test | Description |
|------|-------------|
| `test_agent_output` | Verifies JSON structure and required fields |
| `test_agent_missing_argument` | Verifies usage message on missing input |
| `test_documentation_agent_merge_conflict` | Verifies `read_file` is used for merge conflict question |
| `test_documentation_agent_list_wiki` | Verifies `list_files` is used for wiki listing question |

## How to Run

1. Ensure `.env.agent.secret` exists with valid credentials
2. Ensure Qwen Code API is running on VM
3. Run: `uv run agent.py "Your question"`

**Example:**

```bash
uv run agent.py "How do you resolve a merge conflict?"
```

## Task History

### Task 1: Call an LLM from Code

Basic CLI with no tools:
- Simple question → LLM → answer
- Output: `{"answer": "...", "tool_calls": []}`

### Task 2: The Documentation Agent

Added tools and agentic loop:
- Tools: `read_file`, `list_files`
- Agentic loop for multi-step reasoning
- Output: `{"answer": "...", "source": "...", "tool_calls": [...]}`

### Task 3: The System Agent (Future)

Will add:
- `query_api` tool to query the backend LMS API
- Enhanced system prompt with domain knowledge
- Better source extraction
