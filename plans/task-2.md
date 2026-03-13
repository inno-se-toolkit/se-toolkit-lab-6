# Task 2 Plan: The Documentation Agent

## Overview

In Task 1, the agent could only call the LLM directly. In Task 2, we add **tools** and an **agentic loop** so the agent can:
1. Discover wiki files using `list_files`
2. Read file contents using `read_file`
3. Return answers with source references

## Tool Definitions

### `read_file`

**Purpose:** Read a file from the project repository.

**Schema:**
```json
{
  "name": "read_file",
  "description": "Read the contents of a file from the project repository.",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Relative path from project root (e.g., 'wiki/git.md')"
      }
    },
    "required": ["path"]
  }
}
```

**Implementation:**
- Use Python's `pathlib.Path` to read file contents
- Security: validate path doesn't contain `..` (path traversal)
- Security: ensure resolved path is within project root
- Return file contents as string, or error message if file doesn't exist

### `list_files`

**Purpose:** List files and directories at a given path.

**Schema:**
```json
{
  "name": "list_files",
  "description": "List files and directories in a directory.",
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
- Use `os.listdir()` or `pathlib.Path.iterdir()`
- Security: validate path doesn't contain `..`
- Security: ensure resolved path is within project root
- Return newline-separated list of entries

## Path Security

Both tools must prevent directory traversal attacks:

```python
def validate_path(path: str) -> Path:
    """Validate and resolve a relative path safely."""
    # Reject paths with traversal
    if ".." in path:
        raise ValueError(f"Path traversal not allowed: {path}")
    
    # Resolve to absolute path
    project_root = Path(__file__).parent
    full_path = (project_root / path).resolve()
    
    # Ensure path is within project root
    if not str(full_path).startswith(str(project_root)):
        raise ValueError(f"Path outside project: {path}")
    
    return full_path
```

## Agentic Loop

The loop executes until the LLM provides a final answer or we hit the limit:

```
1. Send question + tool definitions to LLM
2. Parse response:
   - If tool_calls: execute tools, append results, go to step 1
   - If content (no tool_calls): extract answer, return JSON
3. Max 10 iterations (tool calls)
```

**Pseudocode:**
```python
def run_agent(question: str) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    
    tool_calls_log = []
    max_iterations = 10
    
    for _ in range(max_iterations):
        # Call LLM with messages + tool definitions
        response = call_llm(messages, tools=TOOL_DEFINITIONS)
        
        # Check for tool calls
        if response.has_tool_calls:
            for tool_call in response.tool_calls:
                result = execute_tool(tool_call)
                tool_calls_log.append({
                    "tool": tool_call.name,
                    "args": tool_call.args,
                    "result": result
                })
                # Append tool result to messages
                messages.append({"role": "tool", "content": result, "tool_call_id": ...})
            continue  # Loop back to LLM
        else:
            # Final answer
            answer = response.content
            source = extract_source(answer, tool_calls_log)
            return {
                "answer": answer,
                "source": source,
                "tool_calls": tool_calls_log
            }
    
    # Hit max iterations
    return {"answer": "Max iterations reached", "source": "", "tool_calls": tool_calls_log}
```

## System Prompt

The system prompt guides the LLM to use tools effectively:

```
You are a documentation assistant. You have access to tools that let you read files 
and list directories in a project wiki.

When asked a question:
1. First use `list_files` to discover relevant wiki files
2. Then use `read_file` to read the contents of relevant files
3. Find the answer in the file contents
4. Provide the answer with a source reference (file path + section anchor)

Always include the source reference in your final answer.
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

**Test 1:** Question about merge conflicts
- Input: `"How do you resolve a merge conflict?"`
- Expected: `read_file` in tool_calls, `wiki/git-workflow.md` in source

**Test 2:** Question about wiki contents
- Input: `"What files are in the wiki?"`
- Expected: `list_files` in tool_calls

## File Changes

| File | Change |
|------|--------|
| `agent.py` | Add tool definitions, tool implementations, agentic loop |
| `AGENT.md` | Document tools, loop, system prompt |
| `tests/test_agent.py` | Add 2 new test functions |
| `plans/task-2.md` | This plan |

## Next Steps

1. ✅ Create this plan (commit before code)
2. Implement `read_file` and `list_files` tools
3. Implement agentic loop
4. Update system prompt
5. Test manually with wiki questions
6. Add 2 regression tests
7. Update `AGENT.md`
