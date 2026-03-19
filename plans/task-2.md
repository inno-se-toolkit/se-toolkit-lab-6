# Task 2: The Documentation Agent – Implementation Plan

## Overview
Implement an agentic loop that allows the LLM to call `read_file` and `list_files` tools to navigate the wiki and answer documentation questions. The agent will loop: send question → LLM decides tools to call → execute tools → feed results back → repeat until answer found.

## Tool Schemas
Define two tools as JSON schemas for OpenAI-compatible function calling:

### read_file
- **Purpose**: Read file contents from the project repository
- **Parameters**:
  - `path` (string): Relative path from project root (e.g., "wiki/git.md")
- **Returns**: File contents as string, or error message if file doesn't exist
- **Security**: Reject paths with `..` or absolute paths to prevent directory traversal

### list_files
- **Purpose**: List files and directories at a given path
- **Parameters**:
  - `path` (string): Relative directory path from project root (e.g., "wiki")
- **Returns**: Newline-separated listing of entries
- **Security**: Reject paths with `..` or absolute paths

## Agentic Loop Implementation

### Flow
1. Send user question + 2 tool schemas to LLM
2. Parse LLM response:
   - If `tool_calls` field exists → execute each tool call, append tool results as "tool" role messages, increment counter, go to step 1
   - If only text content → extract as final answer, go to step 4
   - If counter reaches 10 → use accumulated answer, go to step 4
3. Output JSON with:
   - `answer`: Final text answer from LLM
   - `source`: Wiki file/section reference (e.g., "wiki/git.md#resolving-merge-conflicts")
   - `tool_calls`: List of all executed tools with args and results

### Path Security
- Normalize path: resolve to absolute, check it's within project root
- Reject if contains `..`, starts with `/`, or contains `\` on Windows
- Return error message if validation fails

### Source Extraction
- Instruct LLM in system prompt to include source reference in final response
- Parse source from LLM's answer text (look for markdown links or explicit file references)
- Extract first wiki file mention or default to empty string

## Code Structure

### New Functions
- `_get_tool_schemas()`: Return list of tool definitions
- `_call_tool(tool_name, args)`: Execute read_file or list_files with security checks
- `_run_agentic_loop(question)`: Main loop that calls LLM, processes tool calls, tracks counter
- `_extract_source(answer, tool_calls)`: Parse wiki reference from answer/tools

### Modified Functions
- `_call_llm()`: Add tools parameter, process tool_calls in response
- `main()`: Call `_run_agentic_loop()` instead of `_call_llm()`, add source to output

## Testing Strategy

### Test 1: read_file tool call
- Question: "How do you resolve a merge conflict?"
- Verify: `tool_calls` contains `read_file` entry, source contains "git-workflow.md"

### Test 2: list_files tool call
- Question: "What files are in the wiki?"
- Verify: `tool_calls` contains `list_files` entry

## System Prompt Strategy
Include directive:
- "Use list_files to discover relevant wiki files"
- "Read files with read_file to find answers"
- "Include the source file path with a section anchor in your response (e.g., #section-name)"
- "Stay focused on the wiki as the source of truth"
