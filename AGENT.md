# Agent Documentation

## Overview
This agent is a simple CLI tool that connects to an LLM (Qwen Code API) and answers questions. It serves as the foundation for building a more complex agent with tools and agentic loops.

## LLM Provider
- **Provider**: Qwen Code API
- **Model**: qwen3-coder-plus (configurable via environment)
- **API Base**: Configurable via environment (default: http://localhost:3000/v1)
- **Authentication**: Bearer token via LLM_API_KEY

## Configuration
The agent reads configuration from environment variables:
- `LLM_API_KEY`: API key for authentication
- `LLM_API_BASE`: Base URL for the OpenAI-compatible API
- `LLM_MODEL`: Model name to use (e.g., qwen3-coder-plus)

## Usage
```bash
# Set up environment variables
export LLM_API_KEY=your-api-key
export LLM_API_BASE=http://localhost:3000/v1
export LLM_MODEL=qwen3-coder-plus

# Or use .env.agent.secret file
cp .env.agent.example .env.agent.secret
# Edit .env.agent.secret with your values

# Run the agent
uv run agent.py "What does REST stand for?"

## Tools

The agent now has two tools for accessing documentation:

### 1. list_files
- **Description**: Lists files and directories at a given path
- **Parameters**: `path` (string) - relative path from project root
- **Security**: Prevents directory traversal attacks
- **Use**: First tool to call to discover available wiki files

### 2. read_file
- **Description**: Reads contents of a file
- **Parameters**: `path` (string) - relative path from project root
- **Security**: Validates path to stay within project root
- **Use**: Read wiki files to find answers

## Agentic Loop

The agent follows this loop:
1. Send question + tool definitions to LLM
2. If LLM requests tools → execute them, append results, repeat (max 10 times)
3. If LLM responds with text → that's the final answer
4. Output JSON with answer, source, and all tool_calls

## System Prompt
The system prompt instructs the LLM to:
- Use list_files first to discover wiki contents
- Then read_file to examine relevant files
- Include source references
- Stop when answer is found

## Output Format
```json
{
  "answer": "Edit the conflicting file, choose which changes to keep, then stage and commit.",
  "source": "wiki/git-workflow.md#resolving-merge-conflicts",
  "tool_calls": [
    {"tool": "list_files", "args": {"path": "wiki"}, "result": "git-workflow.md\n..."},
    {"tool": "read_file", "args": {"path": "wiki/git-workflow.md"}, "result": "..."}
  ]
}
