# Task 2 Plan

## Goal
Upgrade the Task 1 CLI into a documentation agent that can use tools to inspect the project wiki and answer documentation questions.

## Tools
I will implement two tools:

1. `list_files(path)`
   - Lists files and directories inside the project.
   - Returns a newline-separated list.
   - Will be restricted to paths inside the project root.

2. `read_file(path)`
   - Reads a file from the project.
   - Returns the file contents or an error message.
   - Will reject paths outside the project root.

## Tool schemas
I will register both tools in the LLM request as function-calling schemas with clear descriptions and JSON parameters.

## Agentic loop
The agent will:
1. Send the user question, system prompt, and tool schemas to the LLM.
2. If the LLM returns tool calls, execute them.
3. Append each tool result as a tool message.
4. Repeat until the LLM returns a final text answer or the maximum number of tool calls is reached.

## Output
The final JSON output will contain:
- `answer`
- `source`
- `tool_calls`

## Source strategy
The system prompt will instruct the model to:
- use `list_files` to explore the wiki,
- use `read_file` to read relevant wiki files,
- include a source reference in the format `path#section-anchor`.

## Security
Both tools will resolve paths relative to the project root and reject any path traversal such as `../`.

## Tests
I will add 2 regression tests:
- one for a wiki content question that should use `read_file`
- one for a directory listing question that should use `list_files`
