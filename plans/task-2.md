# Plan: Task 2 - The Documentation Agent

## Objective
Enhance `agent.py` by adding an **agentic loop** and two tools (`read_file`, `list_files`) to allow the agent to navigate the project wiki and answer questions based on its content.

## Strategy
- **Tools Implementation**:
  - `list_files(path)`: List entries in a directory. Security: Ensure the path is inside the project and not escaping with `..`.
  - `read_file(path)`: Read a file's content. Security: Ensure the path is inside the project and not escaping with `..`.
- **Tool Schemas**: Define JSON schemas for the tools using the OpenAI format.
- **Agentic Loop**:
  - Send the user question and tool definitions.
  - While tool calls are requested (max 10) and no final answer is provided:
    - Execute the tool calls.
    - Append the tool results as `tool` messages.
    - Call the LLM again.
- **System Prompt**: Instruct the LLM to use `list_files` to discover relevant wiki files and `read_file` to find the answer. It must also provide the `source` as a file path and section anchor (e.g., `wiki/git-workflow.md#resolving-merge-conflicts`).
- **Output**: Update the JSON output to include `source` and the history of `tool_calls` (name, args, result).

## Path Security
- Use `os.path.abspath` and `os.path.commonpath` to verify that any requested path is within the project root.
- Raise an error if the path attempts to escape via `..`.

## Components
1. **`agent.py`**:
   - Refactor to include tool definitions and the agentic loop.
   - Implement the security logic for paths.
   - Handle structured output from the LLM if possible, or extract it from the last message.
2. **`AGENT.md`**: Update documentation to explain the loop and tools.
3. **Tests**: Add `tests/test_agent_docs.py` with 2 tests:
   - Verifying `read_file` and `source` for a specific question about wiki content.
   - Verifying `list_files` for a broad discovery question.
