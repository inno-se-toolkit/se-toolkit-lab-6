# Task 2: The Documentation Agent - Implementation Plan

## Overview

Transform the CLI from Task 1 into an agent that can read project files using tools (`read_file`, `list_files`) and an agentic loop.

## Tool Schemas

### Function Calling Schema Format

The LLM provider (Qwen Code) uses OpenAI-compatible function calling. Each tool needs:
- `name`: function name
- `description`: what the tool does
- `parameters`: JSON Schema for arguments

### `read_file` Schema

```json
{
  "name": "read_file",
  "description": "Read contents of a file from the project repository",
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

### `list_files` Schema

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

## Tool Implementation

### `read_file` Function

```python
def read_file(path: str) -> str:
    # 1. Security: validate path (no ../ traversal)
    # 2. Resolve to absolute path
    # 3. Check file exists
    # 4. Read and return contents
    # 5. Return error message if file doesn't exist
```

### `list_files` Function

```python
def list_files(path: str) -> str:
    # 1. Security: validate path (no ../ traversal)
    # 2. Resolve to absolute path
    # 3. Check directory exists
    # 4. List entries (files and dirs)
    # 5. Return newline-separated string
```

## Path Security

### Security Rules

1. **No path traversal**: Reject paths containing `..`
2. **Must be within project root**: After resolving, verify the path is inside the project directory
3. **Relative paths only**: Paths must be relative to project root (no leading `/`)

### Implementation

```python
import os

def is_safe_path(path: str) -> bool:
    # Reject paths with traversal
    if ".." in path:
        return False
    # Reject absolute paths
    if os.path.isabs(path):
        return False
    # Resolve and verify within project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    resolved = os.path.normpath(os.path.join(project_root, path))
    return resolved.startswith(project_root)
```

## Agentic Loop

### Loop Structure

```
1. Send user question + tool definitions to LLM
2. Parse LLM response:
   - If tool_calls: execute each tool, append results as 'tool' messages, go to step 1
   - If text message: extract answer + source, output JSON, exit
3. Max 10 tool calls per question
```

### Message Format

Messages array sent to LLM:
```python
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": user_question},
    # After tool calls:
    {"role": "assistant", "content": None, "tool_calls": [...]},
    {"role": "tool", "tool_call_id": "...", "content": "tool result"},
    # ... more iterations
]
```

### System Prompt Strategy

The system prompt should instruct the LLM to:
1. Use `list_files` to discover wiki files
2. Use `read_file` to find the answer in specific files
3. Always include a source reference (file path + section anchor)
4. Output the final answer in plain text (not JSON) - we extract answer/source from the text

Example system prompt:
```
You are a documentation assistant. You have access to tools to read files.

When answering questions:
1. First use list_files to explore the wiki directory
2. Then use read_file to read relevant files
3. Find the answer and identify the source (file path + section heading)
4. Provide the answer and cite the source as: "Source: wiki/file.md#section-anchor"

Always include the source reference at the end of your answer.
```

## JSON Output Format

```json
{
  "answer": "The answer text extracted from LLM response",
  "source": "wiki/git-workflow.md#resolving-merge-conflicts",
  "tool_calls": [
    {
      "tool": "list_files",
      "args": {"path": "wiki"},
      "result": "file1.md\nfile2.md"
    },
    {
      "tool": "read_file",
      "args": {"path": "wiki/git-workflow.md"},
      "result": "file contents..."
    }
  ]
}
```

### Extracting Source

The source will be extracted from the LLM's final response by:
1. Looking for patterns like "Source: wiki/file.md#section" or "wiki/file.md#section"
2. If no explicit source found, use the last file read via `read_file`

## Implementation Steps

1. Add tool functions (`read_file`, `list_files`) with path security
2. Define tool schemas for LLM function calling
3. Implement agentic loop:
   - Send initial request with tools
   - Parse response for tool_calls
   - Execute tools and build tool_messages
   - Loop until no tool_calls or max 10 calls
4. Extract answer and source from final LLM response
5. Build and output JSON result
6. Update AGENT.md documentation
7. Write 2 regression tests

## Error Handling

- Tool execution errors: return error message as tool result
- LLM API errors: exit with error message to stderr
- Path security violations: return error message as tool result
- Max tool calls reached: use whatever answer is available

## Testing Strategy

### Test 1: read_file usage
Question: "How do you resolve a merge conflict?"
Expected:
- `read_file` in tool_calls
- `wiki/git-workflow.md` in source

### Test 2: list_files usage
Question: "What files are in the wiki?"
Expected:
- `list_files` in tool_calls
