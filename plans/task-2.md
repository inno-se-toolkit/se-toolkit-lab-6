# Task 2: The Documentation Agent - Implementation Plan

## Overview

In Task 2, we transform the basic agent into a true agent with:

- **Tools**: `read_file` and `list_files` functions the LLM can call
- **Agentic Loop**: The LLM decides which tool to call, we execute it, and loop until the LLM provides a final answer
- **Tool Definitions**: JSON schemas that describe tools to the LLM (function calling)
- **Tool Results**: Feed results back to the LLM for further reasoning

## Architecture Changes from Task 1

### Input/Output

Input: Same as Task 1 (question string)

Output: Extended JSON with new fields:

```json
{
  "answer": "Final answer from LLM",
  "source": "wiki/git-workflow.md#section-title",
  "tool_calls": [
    {
      "tool": "list_files",
      "args": {"path": "wiki"},
      "result": "file1.md\nfile2.md\n..."
    },
    {
      "tool": "read_file",
      "args": {"path": "wiki/git-workflow.md"},
      "result": "File contents..."
    }
  ]
}
```

### The Agentic Loop

```
┌─────────────────────────────────────────────────┐
│  1. Start with user question + tool definitions │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  2. Send to LLM, get response                   │
└────────────┬────────────────────────────────────┘
             │
             ▼
      ┌──────────────┐
      │ Tool calls?  │
      └──────┬───┬──┘
             │   │
        YES  │   │  NO
             ▼   ▼
    ┌────────────────┐    ┌─────────────────────┐
    │ Execute tool   │    │ Extract final answer│
    │ Get result     │    │ Output JSON & exit  │
    └────────┬───────┘    └─────────────────────┘
             │
             ▼
    ┌────────────────────────┐
    │ Add tool result to     │
    │ message history as     │
    │ "assistant" message    │
    └────────┬───────────────┘
             │
             ▼
      ┌──────────────────┐
      │ Hit max 10 calls?│
      └────┬──────────┬──┘
       YES │          │ NO
           │          │ Loop back to step 2
           ▼          │
    ┌─────────────┐   │
    │ Extract     │   │
    │ final answer│───┘
    └─────────────┘
```

## Tool Definitions

### Tool 1: `read_file`

**Purpose**: Read file contents from the project repository.

**Schema**:
```json
{
  "name": "read_file",
  "description": "Read a file from the project repository to find answers",
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

**Implementation**:

- Check path doesn't escape project root (no `../` attacks)
- Return file contents if exists
- Return error message if file not found

**Security**: Must enforce project root boundary - no reading `../../../etc/passwd`

### Tool 2: `list_files`

**Purpose**: List files and directories to discover what files are available.

**Schema**:
```json
{
  "name": "list_files",
  "description": "List files and directories at a given path",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Directory path from project root (e.g., 'wiki')"
      }
    },
    "required": ["path"]
  }
}
```

**Implementation**:

- List all entries (files and folders) in the directory
- Return newline-separated list
- Handle missing directory gracefully

**Security**: Same boundary checks as `read_file`

## Implementation Strategy

### Code Structure

1. **Tool Definitions** (in `agent.py`):

   - `build_tool_schemas()`: Return list of tool schemas for function calling
   - `execute_tool(tool_name, args)`: Execute a tool and return result

2. **Agentic Loop** (in `agent.py`):

   - `run_agent_loop(question, config, max_iterations=10)`
   - Initialize message history with user question
   - While iterations < max:
     - Call LLM with current messages + tool schemas
     - If LLM responds with tool calls:
       - Execute each tool
       - Add results to message history
       - Continue loop
     - If LLM responds with text (no tools):
       - Extract final answer
       - Extract source reference (file path)
       - Break loop
   - Return JSON with answer, source, tool_calls

3. **System Prompt**:

   - Instruct LLM to use `list_files` to discover available files
   - Instruct LLM to use `read_file` to find answers
   - Instruct LLM to include file paths in answers
   - Give examples of good tool use

### System Prompt Strategy

```
You are a helpful assistant that answers questions about a software project.
You have access to tools to read files and list directories.

When asked a question:
1. Use list_files to discover what files are available
2. Use read_file to read relevant files
3. Extract the answer
4. Always cite your source by including the file path

Example:
Q: "How do I resolve a merge conflict?"
A: "Edit the conflicting file, choose which changes to keep, then stage and commit.
   Source: wiki/git-workflow.md#resolving-merge-conflicts"
```

### Tool Call Parsing

The LLM returns tool calls in its response. We need to:

1. Check if `tool_calls` field exists in LLM response
2. For each tool call:
   - Extract `tool` name
   - Extract `arguments` (JSON object)
   - Execute tool with those arguments
   - Add result to message history

### Message History Management

```python
messages = [
    {"role": "user", "content": question},
]

# After LLM response with tool calls:
messages.append({
    "role": "assistant",
    "tool_calls": [...]  # LLM's tool calls
})

# Add tool results:
for result in tool_results:
    messages.append({
        "role": "tool",
        "tool_call_id": result["id"],
        "content": result["output"]
    })
```

## Testing Strategy

### Test 1: list_files usage

Question: "What files are in the wiki?"

Expected:

- Tool calls includes `list_files`
- Answer mentions file names
- Exit without error

### Test 2: read_file usage

Question: "How do you resolve a merge conflict?"

Expected:

- Tool calls includes `list_files` AND `read_file`
- Answer includes information from git-workflow.md
- Source field includes file path
- Answer contains keywords: "merge", "conflict", "resolve"

## Error Handling & Edge Cases

- **File not found**: Tool returns error message, LLM handles gracefully
- **Path escape attempt**: Reject with clear error
- **Max iterations exceeded**: Return best answer so far
- **Tool execution error**: Catch exception, add error message to message history
- **LLM returns null content**: Use `(msg.get("content") or "")` instead of direct access

## Security Considerations

- **Path Traversal**: Validate all paths against project root using `Path.resolve()`
- **Reading sensitive files**: Could limit to `wiki/` and `backend/` directories
- **Rate Limiting**: Each tool call is one iteration toward 10-call limit

## Success Criteria

- Agentic loop runs without errors
- Tool calls are properly executed and results are fed back
- Source field correctly identifies the file that answered the question
- agent.py handles both sync and async gracefully
- Tests pass showing tool usage patterns

## Next Task (Task 3)

- Add `query_api` tool for backend queries
- Expand system prompt to choose between wiki vs API tools
- Run full benchmark and optimize
