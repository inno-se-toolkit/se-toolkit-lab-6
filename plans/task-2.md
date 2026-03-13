# Plan for Task 2: The Documentation Agent

## Overview

This task extends the Task 1 agent with tools (`read_file`, `list_files`) to navigate the project wiki and implement an agentic loop.

## Tool Schemas

### Approach
Define tools as Python functions with JSON schemas that describe their parameters to the LLM.

### Tool Definitions

1. **`read_file`**
   - Description: Read contents of a file from the project repository
   - Parameters: `path` (string) — relative path from project root
   - Returns: file contents as string, or error message

2. **`list_files`**
   - Description: List files and directories at a given path
   - Parameters: `path` (string) — relative directory path from project root
   - Returns: newline-separated listing of entries

### LLM Function Calling Format
Use OpenAI-compatible function calling format:
```python
tools = [{
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "...",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "..."}},
            "required": ["path"]
        }
    }
}]
```

## Agentic Loop Implementation

### Flow
1. Send user question + tool definitions to LLM
2. Parse response:
   - If `tool_calls` present → execute each tool, append results as `tool` role messages, repeat step 1
   - If text message (no tool calls) → extract answer and source, output JSON and exit
3. Maximum 10 tool calls per question (safety limit)

### Message History
Maintain a conversation history:
- Start with system prompt + user question
- After each tool call: append `tool` role message with result
- Continue until LLM returns final answer

### System Prompt Strategy
Tell the LLM to:
- Use `list_files` to discover wiki files
- Use `read_file` to find the answer
- Include source reference (file path + section anchor) in the answer

## Path Security

### Threat
User or LLM might try to read files outside project directory using `../` traversal.

### Solution
1. Resolve the full absolute path using `Path.resolve()`
2. Check that the resolved path starts with the project root directory
3. Reject any path that escapes the project boundary

```python
def validate_path(relative_path: str) -> Path:
    project_root = Path(__file__).parent
    full_path = (project_root / relative_path).resolve()
    if not str(full_path).startswith(str(project_root)):
        raise ValueError("Path traversal not allowed")
    return full_path
```

## Output Format

```json
{
  "answer": "The answer text",
  "source": "wiki/git-workflow.md#resolving-merge-conflicts",
  "tool_calls": [
    {"tool": "list_files", "args": {"path": "wiki"}, "result": "..."},
    {"tool": "read_file", "args": {"path": "wiki/git-workflow.md"}, "result": "..."}
  ]
}
```

## Testing Strategy

1. Test that `read_file` is called when asking about specific wiki content
2. Test that `list_files` is called when asking about directory contents
3. Verify `source` field contains correct wiki path
4. Verify path security rejects `../` traversal

## Implementation Steps

1. Create tool functions (`read_file`, `list_files`) with path validation
2. Build tool schemas for LLM request
3. Implement agentic loop with message history
4. Update system prompt to guide LLM tool usage
5. Update JSON output to include `source` and populated `tool_calls`
6. Write 2 regression tests
