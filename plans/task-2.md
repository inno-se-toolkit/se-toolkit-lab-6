# Task 2 Plan: The Documentation Agent

## Overview

Extend the agent from Task 1 with tools (`read_file`, `list_files`) and an agentic loop that allows the LLM to iteratively explore the wiki and find answers.

## Architecture

### Tools

Two tools to implement:

1. **`read_file(path: str)`**
   - Reads file contents from the project repository
   - Security: prevent path traversal (no `../`)
   - Returns: file contents as string or error message

2. **`list_files(path: str)`**
   - Lists files/directories at a given path
   - Security: prevent directory traversal
   - Returns: newline-separated list of entries

### Agentic Loop

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  User Question ──▶ Build messages with tool definitions     │
│                          │                                   │
│                          ▼                                   │
│                    Call LLM API                              │
│                          │                                   │
│                          ▼                                   │
│              Has tool_calls?                                 │
│              ┌──────┴──────┐                                 │
│             yes           no                                 │
│              │             │                                 │
│              ▼             │                                 │
│    Execute tools   ───────┤                                 │
│    Append results         │                                 │
│    (max 10 calls)         │                                 │
│              │             │                                 │
│              └──────┬──────┘                                 │
│                     │                                        │
│                     ▼                                        │
│              Final answer                                    │
│              Extract answer + source                         │
│                     │                                        │
│                     ▼                                        │
│              JSON Output                                     │
│              {"answer": "...", "source": "...",              │
│               "tool_calls": [...]}                           │
└─────────────────────────────────────────────────────────────┘
```

### Loop Flow

1. Send user question + system prompt + tool definitions to LLM
2. Parse LLM response:
   - If `tool_calls` present → execute each tool, append results as `tool` role, repeat
   - If no tool calls → extract answer and source, output JSON
3. Limit: maximum 10 tool calls per question

### System Prompt Strategy

The system prompt should instruct the LLM to:
- Use `list_files` to discover wiki directory structure
- Use `read_file` to read relevant wiki files
- Find the specific section that answers the question
- Include source reference in format: `wiki/filename.md#section-anchor`
- Only call tools when needed; give final answer when found

## Implementation Steps

1. **Define Tool Schemas**
   - Create JSON schemas for `read_file` and `list_files`
   - Register them in the LLM API request

2. **Implement Tool Functions**
   - `read_file(path)`: validate path, read file, return contents
   - `list_files(path)`: validate path, list directory, return entries

3. **Security Validation**
   - Resolve path to absolute
   - Check it's within project root
   - Reject paths with `..` or absolute paths

4. **Build Agentic Loop**
   - Maintain conversation history (messages list)
   - Loop until no tool calls or max 10 iterations
   - Track all tool calls for output

5. **Extract Answer and Source**
   - Parse final LLM response
   - Extract answer text
   - Extract or infer source reference

6. **Update Output Format**
   - Add `source` field to JSON output
   - Populate `tool_calls` with full history

## Testing

Add 2 regression tests:

1. **Test merge conflict question**
   - Question: "How do you resolve a merge conflict?"
   - Expected: `read_file` in tool_calls, `wiki/git-workflow.md` in source

2. **Test wiki listing question**
   - Question: "What files are in the wiki?"
   - Expected: `list_files` in tool_calls

## Files to Modify

- `agent.py` - Add tools and agentic loop
- `AGENT.md` - Document new architecture
- `tests/test_agent.py` - Add 2 new tests

## Security Considerations

- Validate all paths are within project root
- Use `Path.resolve()` to get absolute paths
- Reject any path traversal attempts
- Handle errors gracefully (return error message, don't crash)
