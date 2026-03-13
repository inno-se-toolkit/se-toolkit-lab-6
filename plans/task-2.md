# Plan for Task 2: The Documentation Agent

## Overview

Extend the Task 1 agent with tools (`read_file`, `list_files`) and an agentic loop that allows the LLM to iteratively query the wiki documentation before providing a final answer.

## Tool Definitions

### `read_file`
**Purpose:** Read contents of a file from the project repository.

**Schema:**
```json
{
  "name": "read_file",
  "description": "Read a file from the project repository. Use this to read documentation files from the wiki directory.",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Relative path from project root (e.g., 'wiki/git-workflow.md')"
      }
    },
    "required": ["path"]
  }
}
```

**Implementation:**
- Accept `path` parameter
- Validate path does not contain `../` (path traversal protection)
- Resolve path relative to project root
- Check file exists and is within project directory
- Return file contents as string, or error message

### `list_files`
**Purpose:** List files and directories at a given path.

**Schema:**
```json
{
  "name": "list_files",
  "description": "List files and directories in a given directory path within the project.",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Relative directory path from project root (e.g., 'wiki')"
      }
    },
    "required": ["path"]
  }
}
```

**Implementation:**
- Accept `path` parameter
- Validate path does not contain `../` or starting with `/`
- Resolve path relative to project root
- Check directory exists and is within project directory
- Return newline-separated list of entries

## Path Security

Both tools must prevent accessing files outside the project directory:

1. Reject any path containing `../` or starting with `/`
2. Resolve the path using `os.path.realpath()`
3. Verify resolved path starts with project root
4. Return error message if validation fails

## Agentic Loop

```
Question → LLM → tool_calls? → yes → execute tools → append results → back to LLM
                                      │
                                      no
                                      │
                                      ▼
                                 JSON output
```

**Algorithm:**
1. Initialize conversation with system prompt + user question
2. Loop (max 10 iterations):
   - Send conversation history to LLM with tool schemas
   - Parse LLM response
   - If `tool_calls` present:
     - Execute each tool call
     - Append tool results to conversation as `tool` role messages
     - Continue loop
   - If no `tool_calls` (text response):
     - Extract answer and source
     - Break loop
3. Output JSON with `answer`, `source`, `tool_calls`

## System Prompt

The system prompt should instruct the LLM to:
- Use `list_files` to discover wiki files
- Use `read_file` to find specific information
- Include the source reference (file path + section anchor) in the final answer
- Call tools iteratively until it finds the answer
- Never make up information — only use what's in the wiki

Example:
```
You are a documentation assistant. You have access to two tools:
- list_files: List files in a directory
- read_file: Read contents of a file

When asked a question about the project:
1. Use list_files to explore the wiki directory
2. Use read_file to read relevant documentation
3. Find the exact section that answers the question
4. Include the source as "wiki/filename.md#section-anchor"

Only answer based on the wiki content. If you cannot find the answer, say so.
```

## Output Format

```json
{
  "answer": "String - the final answer from LLM",
  "source": "String - wiki file path with section anchor (e.g., 'wiki/git-workflow.md#resolving-merge-conflicts')",
  "tool_calls": [
    {
      "tool": "list_files",
      "args": {"path": "wiki"},
      "result": "git-workflow.md\n..."
    },
    {
      "tool": "read_file",
      "args": {"path": "wiki/git-workflow.md"},
      "result": "..."
    }
  ]
}
```

## Error Handling

| Error | Behavior |
|-------|----------|
| Path traversal attempt | Return error message, do not access file |
| File not found | Return error message, LLM can try another path |
| LLM returns invalid tool call | Log error to stderr, continue loop |
| Max iterations (10) reached | Output whatever answer we have |
| API timeout | Exit 1 with error to stderr |

## Testing

Add 2 regression tests:

1. **Test `read_file` usage:**
   - Question: `"How do you resolve a merge conflict?"`
   - Verify: `read_file` in tool_calls, `wiki/git-workflow.md` in source

2. **Test `list_files` usage:**
   - Question: `"What files are in the wiki?"`
   - Verify: `list_files` in tool_calls

## Dependencies

No new dependencies needed — use existing `httpx`, `json`, `os` modules.

## Implementation Steps

1. Create `plans/task-2.md` (this file) — commit before code
2. Add tool function implementations (`read_file`, `list_files`)
3. Add tool schemas for LLM function calling
4. Implement agentic loop with max 10 iterations
5. Update system prompt
6. Update output JSON to include `source` field
7. Update `AGENT.md` documentation
8. Add 2 regression tests
9. Run tests and verify
