# Task 2: The Documentation Agent — Implementation Plan

## Overview

Extend the agent from Task 1 with:
1. Two tools: `read_file` and `list_files`
2. Agentic loop that executes tool calls and feeds results back to LLM
3. New output fields: `source` and populated `tool_calls`

## Tool Definitions

### `read_file`

**Purpose:** Read a file from the project repository.

**Parameters:**
- `path` (string, required): Relative path from project root

**Returns:** File contents as string, or error message if file doesn't exist.

**Security:**
- Validate path doesn't contain `../` traversal
- Ensure resolved path is within project root directory

**Schema (OpenAI function calling format):**
```json
{
  "name": "read_file",
  "description": "Read a file from the project repository",
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

### `list_files`

**Purpose:** List files and directories at a given path.

**Parameters:**
- `path` (string, required): Relative directory path from project root

**Returns:** Newline-separated listing of entries.

**Security:**
- Validate path doesn't contain `../` traversal
- Ensure resolved path is within project root directory

**Schema:**
```json
{
  "name": "list_files",
  "description": "List files and directories at a given path",
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

## Agentic Loop

### Flow

```
Question → LLM (with tool definitions) → tool_calls?
    │
    ├─ YES → Execute each tool → Append results as "tool" messages
    │        → Back to LLM with new messages
    │
    └─ NO  → Final answer → Extract answer + source → Output JSON
```

### Implementation Steps

1. **Initial request:**
   - Build messages array with system prompt + user question
   - Include tool definitions in API request
   - Send to LLM

2. **Parse response:**
   - If `tool_calls` present → execute tools
   - If no `tool_calls` → extract answer and source

3. **Execute tools:**
   - For each tool call:
     - Call the appropriate function (`read_file` or `list_files`)
     - Store result in `tool_calls` array for output
     - Append tool result as `"role": "tool"` message

4. **Loop back:**
   - Send updated messages to LLM
   - Repeat until no tool calls or max 10 iterations

5. **Output:**
   - JSON with `answer`, `source`, and `tool_calls`

### System Prompt

The system prompt will instruct the LLM to:
1. Use `list_files` to discover relevant wiki files
2. Use `read_file` to find the answer in specific files
3. Always include a source reference (file path + optional section anchor)
4. Be concise and accurate

Example system prompt:
```
You are a documentation assistant. You have access to project documentation via tools.

When answering questions:
1. First use `list_files` to discover relevant files in the wiki/ directory
2. Then use `read_file` to read specific files and find the answer
3. Always cite your source as "filename.md#section-anchor"
4. If the answer is not in the documentation, say so

Available tools:
- list_files(path): List files in a directory
- read_file(path): Read contents of a file
```

## Path Security

To prevent directory traversal attacks:

```python
def validate_path(path: str, project_root: Path) -> Path:
    """Validate and resolve a path, ensuring it's within project root."""
    # Reject paths with traversal patterns
    if ".." in path or path.startswith("/"):
        raise ValueError(f"Invalid path: {path}")
    
    # Resolve to absolute path
    full_path = (project_root / path).resolve()
    
    # Ensure it's within project root
    if not str(full_path).startswith(str(project_root.resolve())):
        raise ValueError(f"Path outside project root: {path}")
    
    return full_path
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

## Testing Strategy

### Test 1: Merge Conflict Question

**Question:** `"How do you resolve a merge conflict?"`

**Expected:**
- `read_file` in tool_calls
- `wiki/git-workflow.md` in source field
- Non-empty answer

### Test 2: List Files Question

**Question:** `"What files are in the wiki?"`

**Expected:**
- `list_files` in tool_calls
- Non-empty tool_calls array
- Answer mentions wiki files

## Files to Create/Modify

1. `plans/task-2.md` — this plan
2. `agent.py` — update with tools and agentic loop
3. `AGENT.md` — update documentation
4. `backend/tests/unit/test_agent.py` — add 2 new tests

## Acceptance Criteria Checklist

- [ ] `plans/task-2.md` exists with implementation plan
- [ ] `agent.py` defines `read_file` and `list_files` as tool schemas
- [ ] Agentic loop executes tool calls and feeds results back
- [ ] `tool_calls` in output is populated when tools are used
- [ ] `source` field correctly identifies wiki section
- [ ] Tools don't access files outside project directory
- [ ] `AGENT.md` documents tools and agentic loop
- [ ] 2 tool-calling regression tests exist and pass
- [ ] Git workflow followed (issue, branch, PR, review, merge)
