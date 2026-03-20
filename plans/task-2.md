# Task 2: The Documentation Agent — Implementation Plan

## Overview

Extend the agent from Task 1 with tools (`read_file`, `list_files`) and an agentic loop. The agent will be able to navigate the project wiki and find answers with source references.

## Tool Definitions

### 1. `read_file`

**Purpose:** Read contents of a file from the project repository.

**Parameters:**
- `path` (string, required): Relative path from project root (e.g., `wiki/git-workflow.md`)

**Returns:** File contents as string, or error message if file doesn't exist.

**Security:**
- Block paths containing `../` (path traversal)
- Ensure resolved path is within project directory

**Schema (OpenAI function calling):**
```json
{
  "name": "read_file",
  "description": "Read a file from the project repository",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {"type": "string", "description": "Relative path from project root"}
    },
    "required": ["path"]
  }
}
```

### 2. `list_files`

**Purpose:** List files and directories at a given path.

**Parameters:**
- `path` (string, required): Relative directory path from project root (e.g., `wiki`)

**Returns:** Newline-separated list of entries.

**Security:**
- Block paths containing `../`
- Ensure resolved path is within project directory
- Only list directories, not read file contents

**Schema:**
```json
{
  "name": "list_files",
  "description": "List files and directories at a given path",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {"type": "string", "description": "Relative directory path from project root"}
    },
    "required": ["path"]
  }
}
```

## Agentic Loop

```
1. Send user question + system prompt + tool schemas to LLM
2. Parse response:
   - If tool_calls: execute each tool, append results, go to step 1
   - If text answer: extract answer + source, return JSON
3. Max 10 tool calls per question
```

### Message Flow

```
User: "How do you resolve a merge conflict?"

[Iteration 1]
→ LLM: [tool_calls: list_files(path="wiki")]
← Tool result: "git-workflow.md\nissues.md\n..."

[Iteration 2]
→ LLM: [tool_calls: read_file(path="wiki/git-workflow.md")]
← Tool result: "# Git Workflow\n\n## Resolving merge conflicts\n..."

[Iteration 3]
→ LLM: [text answer: "To resolve...", source: "wiki/git-workflow.md#resolving-merge-conflicts"]
← Output JSON
```

## System Prompt

The system prompt will instruct the LLM to:
1. Use `list_files` to discover relevant wiki files
2. Use `read_file` to read content from relevant files
3. Find the answer and identify the source (file path + section anchor)
4. Return the answer with source reference

## Output Format

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

## Security

- Validate all paths: reject `../`, absolute paths, paths outside project root
- Use `pathlib.Path.resolve()` to get absolute path and verify it's within project
- Return error message if path validation fails

## Files to Update/Create

- `plans/task-2.md` — this plan
- `agent.py` — add tools and agentic loop
- `AGENT.md` — document tools and loop
- `tests/test_agent.py` — add 2 more tests

## Testing Strategy

1. Test `read_file` tool: Ask about merge conflicts, verify `read_file` in tool_calls
2. Test `list_files` tool: Ask about wiki files, verify `list_files` in tool_calls
3. Test source field: Verify source contains file path and section anchor
