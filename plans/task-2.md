# Task 2: The Documentation Agent - Implementation Plan

## Overview

Task 2 extends the agent from Task 1 by adding two tools (`read_file`, `list_files`) and implementing an agentic loop. The agent can now navigate the project wiki, read documentation, and answer questions with proper source references.

## Tool Definitions

### `read_file`

**Purpose:** Read the contents of a file from the project repository.

**Parameters:**
- `path` (string, required): Relative path from project root (e.g., `wiki/git-workflow.md`)

**Returns:** File contents as a string, or error message if file doesn't exist.

**Security:**
- Must not read files outside project directory (no `../` traversal)
- Validate path is within project root

### `list_files`

**Purpose:** List files and directories at a given path.

**Parameters:**
- `path` (string, required): Relative directory path from project root (e.g., `wiki`)

**Returns:** Newline-separated listing of files and directories.

**Security:**
- Must not list directories outside project directory
- Validate path is within project root

## Tool Schema (Function Calling)

For Google Gemini API, tools are defined as:

```python
tools = [
    {
        "functionDeclarations": [
            {
                "name": "read_file",
                "description": "Read the contents of a file from the project repository.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "path": {
                            "type": "STRING",
                            "description": "Relative path from project root (e.g., wiki/git-workflow.md)"
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "list_files",
                "description": "List files and directories at a given path.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "path": {
                            "type": "STRING",
                            "description": "Relative directory path from project root (e.g., wiki)"
                        }
                    },
                    "required": ["path"]
                }
            }
        ]
    }
]
```

## Agentic Loop

```
1. Send user question + tool schemas to LLM
2. Parse LLM response:
   - If tool_calls present:
     a. Execute each tool with provided arguments
     b. Append tool results to conversation history
     c. Send back to LLM for next iteration
     d. Repeat until no more tool calls or max 10 iterations
   - If no tool_calls (final answer):
     a. Extract answer from response
     b. Determine source from tool_calls history
     c. Output JSON and exit
```

### Maximum Iterations

- Limit: 10 tool calls per question
- If exceeded, use whatever answer is available

## System Prompt

The system prompt instructs the LLM to:

1. Use `list_files` to discover wiki files when needed
2. Use `read_file` to read specific documentation files
3. Include source references (file path + section anchor) in the answer
4. Call tools iteratively until confident in the answer

Example:
```
You are a documentation assistant. You have access to two tools:
- list_files: List files in a directory
- read_file: Read the contents of a file

When answering questions:
1. First explore the wiki structure with list_files
2. Read relevant files with read_file
3. Find the answer and cite the source (file path and section)
4. Only give a final answer when you have found the information

Always include the source field with the file path that contains the answer.
```

## Path Security

To prevent directory traversal attacks:

```python
def is_safe_path(path: str) -> bool:
    """Check if path is within project directory."""
    # Resolve to absolute path
    abs_path = os.path.normpath(os.path.join(PROJECT_ROOT, path))
    # Check it starts with project root
    return abs_path.startswith(PROJECT_ROOT)
```

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

## Files to Create/Update

1. `plans/task-2.md` - This plan (create first)
2. `agent.py` - Add tools and agentic loop
3. `AGENT.md` - Update with tool documentation
4. `test_agent.py` - Add 2 more regression tests

## Testing Strategy

Add 2 regression tests:

1. **Test read_file tool:**
   - Question: "How do you resolve a merge conflict?"
   - Expected: `read_file` in tool_calls, `wiki/git-workflow.md` in source

2. **Test list_files tool:**
   - Question: "What files are in the wiki?"
   - Expected: `list_files` in tool_calls

## Acceptance Criteria Checklist

- [ ] Plan written before code
- [ ] `read_file` and `list_files` tool schemas defined
- [ ] Agentic loop executes tool calls and feeds results back
- [ ] `tool_calls` populated in output
- [ ] `source` field identifies wiki section
- [ ] Path security prevents `../` traversal
- [ ] 2 regression tests pass
- [ ] Git workflow: issue → branch → PR → approval → merge
