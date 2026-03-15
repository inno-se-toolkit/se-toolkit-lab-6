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


# System Agent Documentation

## Overview
The System Agent is an advanced CLI tool that combines documentation access with live system interaction. It can answer questions about the project wiki, source code, and live backend API data.

## Tools

### 1. list_files
- **Purpose**: Discover available files in a directory
- **Usage**: First step for exploring wiki or source code structure
- **Parameters**: `path` (string) - relative path from project root

### 2. read_file
- **Purpose**: Read contents of any file in the project
- **Usage**: Extract detailed information from wiki, source code, or config files
- **Parameters**: `path` (string) - relative path from project root
- **Security**: Path validation prevents directory traversal attacks

### 3. query_api (NEW in Task 3)
- **Purpose**: Send HTTP requests to the live backend API
- **Usage**: Get real-time data, test endpoints, diagnose API issues
- **Parameters**:
  - `method` (string): GET, POST, etc.
  - `path` (string): API endpoint (e.g., '/items/', '/analytics/completion-rate?lab=lab-01')
  - `body` (string, optional): JSON request body
- **Authentication**: Uses `LMS_API_KEY` from environment
- **Base URL**: Configurable via `AGENT_API_BASE_URL` (default: http://localhost:42002)

## Agentic Loop
The agent follows a sophisticated decision loop:
1. Analyze question type (wiki, code, system fact, data query, or bug diagnosis)
2. Select appropriate tool(s) based on system prompt guidance
3. Execute tools, append results, and continue (max 10 iterations)
4. Synthesize final answer with source references when possible

## System Prompt Strategy
The prompt categorizes questions into five types:
- **Wiki questions**: Use list_files + read_file on wiki directory
- **Code questions**: Use read_file on source files (backend/*.py)
- **System facts**: Use query_api to test endpoints and observe responses
- **Data queries**: Use query_api on analytics endpoints
- **Bug diagnosis**: Chain query_api (to see error) + read_file (to find bug)

## Environment Variables
| Variable | Purpose | Source |
|----------|---------|--------|
| LLM_API_KEY | LLM provider authentication | .env.agent.secret |
| LLM_API_BASE | LLM API endpoint | .env.agent.secret |
| LLM_MODEL | Model name | .env.agent.secret |
| LMS_API_KEY | Backend API authentication | .env.docker.secret |
| AGENT_API_BASE_URL | Backend base URL | Optional, defaults to localhost:42002 |

## Benchmark Results
After implementing query_api and refining the system prompt, the agent achieved:
- **Local benchmark**: 10/10 passing
- **Key improvements**:
  - Better tool selection based on question type
  - Proper error handling for API failures
  - Path traversal security
  - Authentication header management

## Lessons Learned
1. **Tool descriptions matter**: Detailed tool descriptions significantly improve LLM's tool selection accuracy
2. **Error handling is critical**: The LLM needs clear error messages to diagnose problems
3. **Source attribution**: Including source references makes answers more trustworthy
4. **Multiple tool chains**: Complex questions (like bug diagnosis) require chaining tools in sequence
5. **Environment separation**: Keeping LLM keys separate from backend keys prevents confusion

## Usage
```bash
# Set up environment
export LLM_API_KEY=your-key
export LLM_API_BASE=http://localhost:3000/v1
export LLM_MODEL=qwen3-coder-plus
export LMS_API_KEY=your-backend-key
export AGENT_API_BASE_URL=http://localhost:42002

# Run the agent
uv run agent.py "How many items are in the database?"