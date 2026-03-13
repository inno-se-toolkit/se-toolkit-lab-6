# Task 2 Plan — Documentation Agent

## Tools

The agent will have two tools:

1. list_files
Lists files in a directory.

Parameters:

- path (string)

1. read_file
Reads a file from the repository.

Parameters:

- path (string)

## Agentic loop

1. Send question and tool schemas to the LLM.
2. If the LLM requests tool_calls:
   - execute tool
   - append result to messages
   - call LLM again
3. If the LLM returns text without tool_calls:
   - extract answer and source
   - return JSON output.

Maximum 10 tool calls.

## Security

Paths will be validated to avoid `../` traversal outside the project directory.
