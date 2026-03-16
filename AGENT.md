# Agent Documentation

## Overview

`agent.py` is a CLI tool that connects to an LLM and answers questions by reading project documentation, analyzing source code, and querying the deployed backend API. It uses an agentic loop with three tools (`read_file`, `list_files`, `query_api`) to discover information and provide answers with source references.

## Architecture

```
Question → LLM (with 3 tool schemas) → tool_call?
    │
    ├─ yes → Execute tool (read_file/list_files/query_api) → Append result → Back to LLM
    │
    └─ no  → Final answer → Extract answer + source → Output JSON
```

Maximum 10 tool calls per question.

## LLM Provider

**Provider:** Qwen Code API  
**Model:** `qwen3-coder-plus`

## Configuration

Create `.env.agent.secret` for LLM credentials:

```env
LLM_API_KEY=your-api-key-here
LLM_API_BASE=http://<vm-ip>:<port>/v1
LLM_MODEL=qwen3-coder-plus
```

Create `.env.docker.secret` for backend API credentials:

```env
LMS_API_KEY=your-backend-api-key
AGENT_API_BASE_URL=http://localhost:42002
```

### Environment Variables

| Variable | Purpose | Source |
|----------|---------|--------|
| `LLM_API_KEY` | LLM provider API key | `.env.agent.secret` |
| `LLM_API_BASE` | LLM API endpoint URL | `.env.agent.secret` |
| `LLM_MODEL` | Model name | `.env.agent.secret` |
| `LMS_API_KEY` | Backend API key for query_api | `.env.docker.secret` |
| `AGENT_API_BASE_URL` | Backend URL (optional) | `.env.docker.secret` or default |

## Usage

```bash
uv run agent.py "How do you resolve a merge conflict?"
```

### Output

```json
{
  "answer": "Edit the conflicting file, choose which changes to keep, then stage and commit.",
  "source": "wiki/git-workflow.md#resolving-merge-conflicts",
  "tool_calls": [
    {"tool": "read_file", "args": {"path": "wiki/git-workflow.md"}, "result": "..."}
  ]
}
```

## Tools

### read_file

Read file contents from the project.

**Parameters:** `path` (string) - Relative path from project root

**Security:** Rejects absolute paths and `..` traversal

### list_files

List files and directories.

**Parameters:** `path` (string) - Relative directory path

**Security:** Same path validation as read_file

### query_api

Call the deployed backend API with authentication.

**Parameters:**
- `method` (string) - GET, POST, PUT, DELETE
- `path` (string) - API path (e.g., `/items/`)
- `body` (string, optional) - JSON request body

**Authentication:** Uses `LMS_API_KEY` as `X-API-Key` header

**Returns:** JSON with `status_code` and `body`

## System Prompt

The system prompt guides tool selection:

- Use `list_files`/`read_file` for wiki questions, source code analysis, configuration
- Use `query_api` for live data queries, testing endpoints, status codes, counts

## Agentic Loop

1. Initialize messages with system prompt + user question
2. Call LLM with all 3 tool schemas
3. If tool calls returned:
   - Execute each tool
   - Append results as tool messages
   - Repeat from step 2
4. If no tool calls: extract answer, break
5. Extract source from answer or infer from last read_file
6. Output JSON

## Error Handling

- Missing config: Exit 1, error to stderr
- Timeout (>60s): Exit 1, error to stderr
- HTTP error: Exit 1, status code to stderr
- Tool error: Return error message, continue loop
- Max tool calls: Use whatever answer available

## Testing

```bash
uv run pytest tests/test_agent.py -v
```

Tests verify:
- Valid JSON output with required fields
- Correct tool usage for specific questions
- Source references in answers

## Benchmark Results

The agent is evaluated against 10 local questions and additional hidden questions covering:
- Wiki lookup questions (read_file)
- Source code analysis (read_file, list_files)
- API data queries (query_api)
- Error diagnosis (query_api + read_file)
- Reasoning questions (LLM judge)

## Lessons Learned

Building this agent taught me several important lessons about working with LLMs and tool-calling systems.

**First, the system prompt is critical.** Initially, my agent would call the wrong tool for certain questions. For example, it would try to use `read_file` to get live database counts instead of `query_api`. The fix was making the system prompt much more explicit about when to use each tool, with concrete examples of API paths. I organized the prompt into clear categories: wiki questions, source code questions, live data questions, bug diagnosis questions, and reasoning questions. Each category has specific step-by-step instructions.

**Second, environment variable handling is tricky.** I initially hardcoded the backend URL, which worked locally but would fail the autochecker. The key insight is that the autochecker injects its own values, so the agent must read from environment variables, not hardcoded strings. I also learned that `LMS_API_KEY` (backend auth) and `LLM_API_KEY` (LLM provider auth) are completely separate credentials from different files. The agent reads `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL` from `.env.agent.secret` (or environment), and `LMS_API_KEY`, `AGENT_API_BASE_URL` from `.env.docker.secret` (or environment).

**Third, the LLM sometimes returns `content: null` when making tool calls, not `content: ""`.** Using `msg.get("content") or ""` instead of `msg.get("content", "")` fixed crashes where the agent would fail on `None` values. This is a subtle but important distinction — the field exists but is null, not missing.

**Fourth, path security matters.** The `safe_path` function prevents directory traversal attacks by rejecting `..` and verifying resolved paths stay within the project root. This is essential when the agent can read arbitrary files. The function also rejects absolute paths to ensure all file access is relative to the project root.

**Fifth, tool descriptions need to be specific.** Vague descriptions like "Read a file" led to inconsistent tool selection. I updated the descriptions to include concrete examples: "Relative path from project root (e.g., 'wiki/github.md', 'backend/app/main.py', 'Dockerfile')". This helped the LLM understand exactly what format paths should be in.

**Sixth, iteration is key.** The first version of the agent failed several benchmark questions. Each failure revealed a bug or ambiguity: wrong tool selection, missing authentication, incorrect source extraction. Running `run_eval.py` repeatedly and fixing one issue at a time led to a working agent. The key was to fix one failing question at a time, understand why it failed, and make targeted improvements.

**Seventh, the agentic loop needs proper error handling.** Tool calls can fail for many reasons: network errors, file not found, API errors. Each tool returns error messages as strings, which are fed back to the LLM. The LLM can then decide to retry with different parameters or try a different approach. This resilience is crucial for handling real-world failures.

**Eighth, source extraction is important for grading.** The agent extracts source references from the answer using regex patterns, or infers them from the last `read_file` tool call. This allows the autochecker to verify that the agent actually read the relevant files.

## Tool Selection Strategy

The agent uses a clear decision tree for tool selection:

1. **Wiki questions** → `list_files("wiki")` → `read_file("wiki/<topic>.md")`
2. **Source code questions** → `read_file("backend/app/<file>.py")` or `read_file("Dockerfile")`
3. **Live data questions** → `query_api(method="GET", path="/items/")`
4. **Bug diagnosis** → `query_api()` to get error → `read_file()` to find bug
5. **Reasoning questions** → Multiple `read_file()` calls to gather context

This strategy is encoded in the system prompt with explicit examples for each category.

## File Structure

```
se-toolkit-lab-6/
├── agent.py              # Main agent CLI
├── .env.agent.example    # LLM credentials template
├── .env.agent.secret     # LLM credentials (local)
├── .env.docker.secret    # Backend credentials (local)
├── AGENT.md              # This documentation
├── plans/
│   ├── task-1.md         # Task 1 plan
│   ├── task-2.md         # Task 2 plan
│   └── task-3.md         # Task 3 plan
└── tests/
    └── test_agent.py     # Regression tests
```
