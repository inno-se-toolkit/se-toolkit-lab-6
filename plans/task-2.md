# Task 2 Plan: The Documentation Agent

## Overview

Task 2 extends the Task 1 agent with **tools** and an **agentic loop**. The agent can now:
1. Discover files in the project using `list_files`
2. Read file contents using `read_file`
3. Loop: call tools → get results → reason → call more tools or answer

## LLM Provider and Model

**Provider:** Qwen Code API (same as Task 1)
**Model:** `qwen3-coder-plus`

Same configuration from `.env.agent.secret`:
- `LLM_API_KEY`
- `LLM_API_BASE`
- `LLM_MODEL`

## Tool Schemas

### 1. `read_file`

**Purpose:** Read contents of a file from the project repository.

**Schema (OpenAI function calling format):**
```json
{
  "name": "read_file",
  "description": "Read the contents of a file in the project repository",
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
- Use Python's `Path.read_text()` to read file
- Validate path: must be within project root (no `../` traversal)
- Return file contents as string
- On error: return error message string

### 2. `list_files`

**Purpose:** List files and directories at a given path.

**Schema:**
```json
{
  "name": "list_files",
  "description": "List files and directories at a given path in the project",
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
- Use `Path.iterdir()` to list entries
- Validate path: must be a directory within project root
- Return newline-separated string of entry names
- On error: return error message string

## Path Security

Both tools must prevent directory traversal attacks:

1. **Resolve to absolute path:** `Path(project_root) / user_path`
2. **Check containment:** Resolved path must start with `project_root`
3. **Reject `..` components:** Check for `..` in path string
4. **Error on violation:** Return error message, don't access file

**Example validation:**
```python
def validate_path(user_path: str, project_root: Path) -> Path:
    if ".." in user_path:
        raise ValueError("Path traversal not allowed")
    full_path = (project_root / user_path).resolve()
    if not str(full_path).startswith(str(project_root.resolve())):
        raise ValueError("Path outside project not allowed")
    return full_path
```

## Agentic Loop

**Algorithm:**

```
1. Initialize messages list with:
   - System prompt (instructions + tool schemas)
   - User question

2. Loop (max 10 iterations):
   a. Call LLM with messages
   b. If response has tool_calls:
      - Execute each tool
      - Append tool results as "tool" role messages
      - Continue loop
   c. If response has text answer:
      - Extract answer and source
      - Break loop

3. Output JSON with answer, source, tool_calls
```

**Pseudocode:**
```python
messages = [system_prompt, {"role": "user", "content": question}]
tool_calls_log = []

for _ in range(MAX_ITERATIONS):
    response = call_llm(messages, tools)
    
    if response.tool_calls:
        for tool_call in response.tool_calls:
            result = execute_tool(tool_call)
            tool_calls_log.append({tool, args, result})
            messages.append({"role": "tool", "content": result})
    else:
        answer = response.content
        source = extract_source(answer, tool_calls_log)
        break
```

## System Prompt

The system prompt guides the LLM to use tools effectively:

```
You are a documentation assistant for a software engineering project.
You have access to the project wiki and source code.

Available tools:
- list_files(path): List files in a directory
- read_file(path): Read contents of a file

When answering questions:
1. First use list_files to discover relevant files
2. Then use read_file to read specific files
3. Find the answer and cite the source (file path + section anchor)
4. Format: "According to [file](#section), ..."

Always include the source reference in your answer.
Maximum 10 tool calls per question.
```

## Output Format

Same as Task 1, with additions:

```json
{
  "answer": "String - the final answer",
  "source": "String - wiki file path with anchor (e.g., 'wiki/git-workflow.md#resolving-conflicts')",
  "tool_calls": [
    {
      "tool": "list_files",
      "args": {"path": "wiki"},
      "result": "file1.md\nfile2.md"
    },
    {
      "tool": "read_file",
      "args": {"path": "wiki/git-workflow.md"},
      "result": "File contents..."
    }
  ]
}
```

## File Structure

```
se-toolkit-lab-6/
├── plans/
│   └── task-2.md          # This plan
├── agent.py               # Updated with tools + loop
├── AGENT.md               # Updated documentation
├── tests/
│   └── test_agent_task2.py  # 2 new regression tests
└── wiki/                   # Documentation to query
    ├── git-workflow.md
    └── ...
```

## Implementation Steps

1. Create `plans/task-2.md` (this file) - commit first
2. Add tool schemas to `agent.py`
3. Implement `read_file` and `list_files` functions
4. Add path validation logic
5. Implement agentic loop (max 10 iterations)
6. Update output JSON to include `source` and `tool_calls`
7. Update `AGENT.md` with tool documentation
8. Add 2 regression tests:
   - Test merge conflict question → expects `read_file`, `wiki/git-workflow.md` in source
   - Test wiki files question → expects `list_files`
9. Run lint/typecheck/tests
10. Commit code, push, create PR

## Success Criteria

- ✅ `plans/task-2.md` committed before code
- ✅ `agent.py` has `read_file` and `list_files` tool schemas
- ✅ Agentic loop executes and populates `tool_calls`
- ✅ `source` field contains wiki reference
- ✅ Path security prevents `../` traversal
- ✅ `AGENT.md` documents tools and loop
- ✅ 2 regression tests pass
- ✅ Git workflow: issue, branch, PR, review, merge
