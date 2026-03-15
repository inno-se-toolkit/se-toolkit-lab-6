# Task 2: The Documentation Agent - Implementation Plan

## Tool Implementation

### read_file tool
- **Purpose**: Read contents of a file from the project repository
- **Parameters**: 
  - `path` (string): relative path from project root
- **Security**: Prevent directory traversal attacks
  - Normalize path using `os.path.normpath`
  - Ensure resolved path starts with project root
  - Block paths containing `..`
- **Returns**: File contents or error message

### list_files tool
- **Purpose**: List files and directories at a given path
- **Parameters**:
  - `path` (string): relative directory path from project root
- **Security**: Same path validation as read_file
- **Returns**: Newline-separated listing of entries

## Agentic Loop Design

The agent will follow this loop:

1. **Initial Request**: Send user question + tool definitions to LLM
2. **Parse Response**: Check if LLM wants to call tools
3. **Tool Execution**: If `tool_calls` present:
   - Execute each tool with provided arguments
   - Append results as `tool` role messages
   - Go back to step 1 (max 10 iterations)
4. **Final Answer**: If no tool calls, extract answer and source
5. **Output**: JSON with answer, source, and all tool_calls

## System Prompt Strategy

The prompt will instruct the LLM to:
- Use `list_files` first to discover wiki contents
- Use `read_file` to examine relevant files
- Include source reference (file path + section anchor)
- Stop when answer is found

## Tool Schemas (OpenAI-compatible)

```json
{
  "type": "function",
  "function": {
    "name": "read_file",
    "description": "Read contents of a file",
    "parameters": {
      "type": "object",
      "properties": {
        "path": {
          "type": "string",
          "description": "Relative path from project root"
        }
      },
      "required": ["path"]
    }
  }
}
