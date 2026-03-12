# The System Agent

In Task 2 you built an agent that reads documentation. But documentation can be outdated — the real system is the source of truth. In this task you will give your agent a new tool (`query_api`) so it can talk to your deployed backend, and teach it to answer two new kinds of questions: static system facts (framework, ports, status codes) and data-dependent queries (item count, scores).

## What you will add

You will add a `query_api` tool to the agent you built in Task 2. The agentic loop stays the same — you are just adding one more tool the LLM can call. The agent can now send requests to your deployed backend in addition to reading files.

## CLI interface

Same rules as Task 2. The only change: `source` is now optional (system questions may not have a wiki source).

```bash
uv run agent.py "How many items are in the database?"
```

```json
{
  "answer": "There are 120 items in the database.",
  "tool_calls": [
    {"tool": "query_api", "args": {"method": "GET", "path": "/items/"}, "result": "{\"status_code\": 200, ...}"}
  ]
}
```

## New tool: `query_api`

Call your deployed backend API. Register it as a function-calling schema alongside your existing tools.

- **Parameters:** `method` (string — GET, POST, etc.), `path` (string — e.g., `/items/`), `body` (string, optional — JSON request body).
- **Returns:** JSON string with `status_code` and `body`.
- **Authentication:** use `LMS_API_KEY` from `.env.docker.secret` (the backend key, not the LLM key).

Update your system prompt so the LLM knows when to use wiki tools vs `query_api` vs `read_file` on source code.

> **Note:** Two distinct keys: `LMS_API_KEY` (in `.env.docker.secret`) protects your backend endpoints. `LLM_API_KEY` (in `.env.agent.secret`) authenticates with your LLM provider. Don't mix them up.

## Pass the benchmark

Once `query_api` works, run the evaluation benchmark and iterate until your agent passes.

```bash
uv run run_eval.py
```

The script fetches questions from the autochecker API, runs your agent on each one, and checks the answer. On failure it shows a feedback hint.

```
  ✓ [1/26] How do you resolve a merge conflict?
  ✓ [2/26] What is a Docker volume used for?
  ✓ [3/26] What framework does the backend use?

  ✗ [4/26] You change your Python code and run 'docker compose up -d'...
    feedback: Think about when Docker rebuilds the image vs reuses the old one.

3/26 passed
```

Fix the failing question, re-run, move on to the next one.

> **Note:** The autochecker bot tests your agent with additional hidden questions not present in `run_eval.py`. These include multi-step challenges that require chaining tools. You need a genuinely working agent — not hard-coded answers.

### Debugging workflow

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Agent doesn't use a tool when it should | Tool description too vague for the LLM | Improve the tool's description in the schema |
| Tool called but returns an error | Bug in tool implementation | Fix the tool code, test it in isolation |
| Tool called with wrong arguments | LLM misunderstands the schema | Clarify parameter descriptions |
| Agent times out | Too many tool calls or slow LLM | Reduce max iterations, try a faster model |
| Answer is close but doesn't match | Phrasing doesn't contain expected keyword | Adjust system prompt to be more precise |

## Deliverables

### 1. Plan (`plans/task-3.md`)

Before writing code, create `plans/task-3.md`. Describe how you will define the `query_api` tool schema, handle authentication, and update the system prompt.

After running the benchmark once, add your initial score, first failures, and iteration strategy.

### 2. Tool and agent updates (update `agent.py`)

Add `query_api` as a function-calling schema, implement it with authentication, and update the system prompt. Then iterate until the benchmark passes.

### 3. Documentation (update `AGENT.md`)

Update `AGENT.md` to document the `query_api` tool, its authentication, how the LLM decides between wiki and system tools, lessons learned from the benchmark, and your final eval score. At least 200 words.

### 4. Tests (5 more tests)

Add 5 regression tests for system agent tools. Example questions:

- `"What framework does the backend use?"` → expects `read_file` in tool_calls.
- `"How many items are in the database?"` → expects `query_api` in tool_calls.

### 5. Deployment

Deploy the final agent to your VM. Make sure both `.env.agent.secret` (LLM key) and `.env.docker.secret` (backend API key) are configured.

The autochecker bot will run the full benchmark including hidden questions. You need at least **75%** to pass.

## Acceptance criteria

- [ ] `plans/task-3.md` exists with the implementation plan and benchmark diagnosis.
- [ ] `agent.py` defines `query_api` as a function-calling schema.
- [ ] `query_api` authenticates with `LMS_API_KEY`.
- [ ] The agent answers static system questions correctly (framework, ports, status codes).
- [ ] The agent answers data-dependent questions with plausible values.
- [ ] `run_eval.py` passes all local questions.
- [ ] `AGENT.md` documents the final architecture and lessons learned (at least 200 words).
- [ ] 5 tool-calling regression tests exist and pass.
- [ ] The agent works on the VM via SSH.
- [ ] The agent passes the autochecker bot benchmark (≥75%).
- [ ] [Git workflow](../../../wiki/git-workflow.md): issue `[Task] The System Agent`, branch, PR with `Closes #...`, partner approval, merge.
