# Task 2: The Documentation Agent

## Implementation Plan

### 1. Tool Schemas

Define two tools as function-calling schemas for the LLM:

**read_file:**
- Description: Read contents of a file from the project
- Parameters: `path` (string, required) - relative path from project root
- Security: Validate path doesn't escape project directory

**list_files:**
- Description: List files and directories at a given path
- Parameters: `path` (string, required) - relative directory path from project root
- Security: Validate path doesn't escape project directory

Schema format follows OpenAI function-calling spec:
```python
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

### 2. Agentic Loop

Implement loop in `agent.py`:

1. Send user question + system prompt + tool schemas to LLM
2. Parse response:
   - If `tool_calls` present: execute each tool, append results to messages, repeat
   - If text answer: extract answer + source, return JSON
3. Max 10 iterations to prevent infinite loops
4. Track all tool calls with args and results for output

Message format:
```python
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": question}
]
# After each tool call:
messages.append({"role": "tool", "content": result, "tool_call_id": id})
```

### 3. Path Security

Prevent directory traversal:

1. Resolve absolute path: `os.path.abspath(os.path.join(project_root, requested_path))`
2. Check prefix: `resolved_path.startswith(project_root)`
3. Reject paths containing `..` or starting with `/`
4. For `list_files`: verify path is a directory
5. For `read_file`: verify path is a file

### 4. System Prompt Strategy

Tell the LLM:
- You have access to `read_file` and `list_files` tools
- Always use `list_files` to discover wiki structure first
- Use `read_file` to find specific information
- Include source reference in format: `wiki/filename.md#section-anchor`
- Answer must be based on actual file contents, not assumptions

### 5. Output Format

```json
{
    "answer": "The answer text from LLM",
    "source": "wiki/git-workflow.md#resolving-merge-conflicts",
    "tool_calls": [
        {"tool": "list_files", "args": {"path": "wiki"}, "result": "..."},
        {"tool": "read_file", "args": {"path": "wiki/git-workflow.md"}, "result": "..."}
    ]
}
```

### 6. Testing

Add 2 regression tests:

1. **Merge conflict question:**
   - Input: "How do you resolve a merge conflict?"
   - Expect: `read_file` in tool_calls, `wiki/git-workflow.md` in source

2. **Wiki listing question:**
   - Input: "What files are in the wiki?"
   - Expect: `list_files` in tool_calls

Tests will run `agent.py` as subprocess, parse JSON output, verify fields.
