# Task plan 2

## Tools
- read_file: reads the file along the path (with security check)
- list_files: shows the contents of the directory

## Tool diagram (OpenAI function calling)
- read_file: {path: string}
- list_files: {path: string}

## Agent cycle
1. Send a question + tool diagrams to LLM
2. If LLM returned tool_calls → run tools
3. Return the results to LLM as role=tool messages
4. Repeat until there is no final answer or 10 calls have been reached.
5. Return JSON with answer, source, tool_calls

## Path safety
- Prohibit ../ (going outside the project)
- Check that the path starts from the root of the project

## System prompt
Use list_files to search for wiki files, then read_file to read the response. Specify the source as path#anchor.
