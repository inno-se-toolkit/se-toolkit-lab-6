# Agent

A CLI agent with tools for working with documentation.

## Running
uv run agent.py "The question"

## Output
{
"answer": "text",
  "source": "wiki/file.md#section",
  "tool_calls": [...]
}

## Tools
- read_file(path): reads the file
- list_files(path): the list of files in the directory

## Agent cycle
1. Question → LLM with tool diagrams
2. LLM decides: tool_call or response
3. If tool_call → execute → result → LLM
4. Repeat until you answer or 10 calls

## Security
- Blocking../
- Checking paths inside the project

## Variables (.env.agent.secret)
- LLM_API_KEY
- LLM_API_BASE
- LLM_MODEL