# Agent Architecture

## Overview

This agent is a CLI tool that uses an LLM to answer questions about the project documentation. It has an **agentic loop** that allows it to use tools to read files and explore the project structure.

## Architecture

```
User Question → System Prompt + Tools → LLM → Tool Calls? → Execute Tools → Results → LLM → Final Answer
```

### Components

1. **Environment Loading**: Loads LLM credentials from `.env.agent.secret`
2. **Tool Definitions**: `read_file` and `list_files` with JSON schemas
3. **Agentic Loop**: Iteratively calls LLM, executes tools, and feeds results back
4. **JSON Output**: Structured response with answer, source, and tool_calls

## Tools

The agent has two tools for navigating the project repository:

### `read_file`

Reads the contents of a file from the project repository.

**Parameters:**
- `path` (string, required): Relative path from project root (e.g., `wiki/git-workflow.md`)

**Returns:** File contents as a string, or an error message if the file doesn't exist.

**Security:** Rejects paths containing `..` (path traversal) or absolute paths.

### `list_files`

Lists files and directories at a given path.

**Parameters:**
- `path` (string, required): Relative directory path from project root (e.g., `wiki`)

**Returns:** Newline-separated listing of entries (directories first, then files), or an error message.

**Security:** Rejects paths containing `..` (path traversal) or absolute paths.

## Agentic Loop

The agentic loop enables the agent to iteratively gather information before answering:

```python
while tool_call_count < MAX_TOOL_CALLS:
    1. Send messages + tool schemas to LLM
    2. If LLM returns tool_calls:
       - Execute each tool
       - Append results as 'tool' role messages
       - Continue loop
    3. If LLM returns text (no tool_calls):
       - This is the final answer
       - Extract answer and source
       - Output JSON and exit
```

### Message Format

Messages sent to the LLM follow the OpenAI chat format:

```python
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "How do you resolve a merge conflict?"},
    # After tool calls:
    {"role": "assistant", "content": None, "tool_calls": [...]},
    {"role": "tool", "tool_call_id": "call_1", "content": "file contents..."},
    # ... more iterations
]
```

### Maximum Tool Calls

The loop stops after 10 tool calls maximum to prevent infinite loops.

## System Prompt Strategy

The system prompt instructs the LLM to:

1. **Explore first**: Use `list_files` to discover wiki directories
2. **Read relevant files**: Use `read_file` to find answers
3. **Cite sources**: Always include a source reference with section anchor
4. **Format**: Use `wiki/filename.md#section-anchor` format

Example system prompt guidance:
- "First use list_files to explore relevant directories"
- "Then use read_file to read specific files"
- "Include source reference: wiki/filename.md#section-anchor"

## Output Format

The agent outputs JSON with three fields:

```json
{
  "answer": "Edit the conflicting file, choose which changes to keep, then stage and commit.",
  "source": "wiki/git-workflow.md#resolving-merge-conflicts",
  "tool_calls": [
    {
      "tool": "list_files",
      "args": {"path": "wiki"},
      "result": "git-workflow.md\n..."
    },
    {
      "tool": "read_file",
      "args": {"path": "wiki/git-workflow.md"},
      "result": "# Git workflow\n\n..."
    }
  ]
}
```

### Fields

- **answer** (string): The LLM's final answer to the question
- **source** (string): Reference to the wiki section (e.g., `wiki/git-workflow.md#section`)
- **tool_calls** (array): All tool calls made during the conversation

### Source Extraction

The source is extracted by:
1. Looking for explicit `Source: wiki/filename.md#anchor` in the response
2. Falling back to the last `read_file` call if no explicit source

## Path Security

Tools enforce security to prevent accessing files outside the project:

1. **No path traversal**: Paths containing `..` are rejected
2. **No absolute paths**: Paths starting with `/` are rejected
3. **Within project root**: Resolved paths must be within the project directory

```python
def is_safe_path(path: str) -> bool:
    if ".." in path:
        return False
    if os.path.isabs(path):
        return False
    resolved = os.path.normpath(os.path.join(project_root, path))
    return resolved.startswith(project_root)
```

## Usage

```bash
uv run agent.py "How do you resolve a merge conflict?"
```

## Error Handling

- **Missing credentials**: Exit with error message to stderr
- **File not found**: Return error message as tool result
- **Path traversal attempt**: Return error message as tool result
- **LLM API errors**: Exit with error message to stderr
- **Max tool calls**: Use whatever answer is available
