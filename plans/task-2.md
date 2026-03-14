# Plan: Task 2 - The Documentation Agent

## Overview

Build an agentic loop that gives the LLM tools to read documentation and navigate the wiki. The agent will:
1. Receive a question from the user
2. Send it to the LLM with tool definitions
3. Execute tool calls if the LLM requests them
4. Feed results back to the LLM
5. Repeat until the LLM provides a final answer
6. Output JSON with `answer`, `source`, and `tool_calls`

## Tool Definitions

### `read_file`

**Purpose:** Read a file from the project repository.

**Parameters:**
- `path` (string, required): Relative path from project root (e.g., `wiki/git-workflow.md`)

**Returns:** File contents as a string, or error message if file doesn't exist.

**Security:** Reject paths containing `../` to prevent directory traversal.

### `list_files`

**Purpose:** List files and directories at a given path.

**Parameters:**
- `path` (string, required): Relative directory path from project root (e.g., `wiki`)

**Returns:** Newline-separated list of entries.

**Security:** Reject paths containing `../` and ensure path stays within project root.

## Agentic Loop Design

```
Question → LLM (with tool schemas) → tool_calls?
                                      │
                                      yes
                                      │
                                      ▼
                              Execute tools → Append results as "tool" messages
                                      │
                                      ▼
                              Back to LLM (max 10 iterations)
                                      │
                                      no (final answer)
                                      │
                                      ▼
                              Extract answer + source → JSON output
```

**Loop constraints:**
- Maximum 10 tool calls per question
- Each iteration: LLM response → execute tools → feed back
- Stop when LLM returns content without tool_calls

## System Prompt Strategy

The system prompt should instruct the LLM to:
1. Use `list_files` to discover relevant wiki files
2. Use `read_file` to read the content and find the answer
3. Include a source reference in the final answer (file path + section anchor)
4. Call tools step by step, not all at once

## Implementation Steps

1. **Define tool schemas** — JSON schemas for `read_file` and `list_files` matching OpenAI function-calling format
2. **Implement tool functions** — Python functions that execute the tools with security checks
3. **Build the agentic loop** — While loop that:
   - Calls LLM with messages + tool schemas
   - Parses tool_calls from response
   - Executes tools and appends results
   - Breaks when no tool_calls
4. **Update response format** — Include `source` field and populate `tool_calls` array
5. **Update system prompt** — Instruct LLM on tool usage and source citation

## Testing Strategy

Add 2 regression tests to `tests/test_agent.py`:

**Test 1: Wiki question requiring read_file**
- Question: "How do you resolve a merge conflict?"
- Expected: `read_file` in tool_calls, `wiki/git-workflow.md` in source

**Test 2: Directory listing question**
- Question: "What files are in the wiki?"
- Expected: `list_files` in tool_calls

## Expected Output Format

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

## Security Considerations

- Path traversal prevention: reject `../` in paths
- Path normalization: use `Path.resolve()` to verify path stays within project root
- File size limits: truncate large files to avoid token limits

## Dependencies

No new dependencies needed — use existing `openai` and `python-dotenv`.
