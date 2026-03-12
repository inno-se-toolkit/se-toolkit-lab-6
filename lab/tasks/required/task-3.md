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

## Deploy to your VM

Before running the benchmark, deploy your application to the VM so the autochecker can query your API.

### Clean up the previous lab

1. [Connect to your VM](../../../wiki/vm.md#connect-to-the-vm).
2. Navigate to the previous lab's project directory:

   ```terminal
   cd ~/se-toolkit-lab-5
   ```

3. Stop and remove all containers and volumes:

   ```terminal
   docker compose --env-file .env.docker.secret down -v
   ```

4. Go back to the home directory:

   ```terminal
   cd ~
   ```

> [!NOTE]
> If you didn't do Lab 5, try `cd ~/se-toolkit-lab-4` instead.
> If neither directory exists, skip the cleanup.

### Deploy the application

1. Clone your fork on the VM:

   ```terminal
   cd ~
   git clone https://github.com/<your-github-username>/se-toolkit-lab-6.git
   cd se-toolkit-lab-6
   ```

2. Create and configure the environment file:

   ```terminal
   cp .env.docker.example .env.docker.secret
   nano .env.docker.secret
   ```

   Set your autochecker API credentials and `LMS_API_KEY` (same values as your local `.env.docker.secret`).

   Save and exit: `Ctrl+X`, then `y`, then `Enter`.

3. Start the services:

   ```terminal
   docker compose --env-file .env.docker.secret up --build -d
   ```

4. Populate the database — open `http://<your-vm-ip>:42002/docs`, authorize with your `LMS_API_KEY`, and call `POST /pipeline/sync`.

## Pass the benchmark

Once `query_api` works, run the evaluation benchmark locally and iterate until your agent passes.

```bash
uv run run_eval.py
```

The script runs your agent against 10 local questions across all classes (wiki lookup, system facts, data queries, bug diagnosis, reasoning). On failure it shows a feedback hint.

```
  ✓ [1/10] According to the project wiki, what steps are needed to protect a branch?
  ✓ [2/10] What Python web framework does this project use?
  ✓ [3/10] How many items are in the database?

  ✗ [4/10] Query the /analytics/completion-rate endpoint for lab-99...
    feedback: Try GET /analytics/completion-rate?lab=lab-99. Read the error, then find the buggy line.

3/10 passed
```

Fix the failing question, re-run, move on to the next one.

> [!NOTE]
> The autochecker tests your agent with 10 additional hidden questions not present in `run_eval.py`. These include multi-step challenges that require chaining tools (e.g., query an API error, then read the source code to diagnose the bug). You need a genuinely working agent — not hard-coded answers.

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

Deploy the final agent to your VM. Make sure both `.env.agent.secret` (LLM key) and `.env.docker.secret` (backend API key) are configured on the VM.

The autochecker will run the full benchmark including hidden questions. You need at least **75%** to pass.

## Acceptance criteria

- [ ] `plans/task-3.md` exists with the implementation plan and benchmark diagnosis.
- [ ] `agent.py` defines `query_api` as a function-calling schema.
- [ ] `query_api` authenticates with `LMS_API_KEY`.
- [ ] The agent answers static system questions correctly (framework, ports, status codes).
- [ ] The agent answers data-dependent questions with plausible values.
- [ ] `run_eval.py` passes all 10 local questions.
- [ ] `AGENT.md` documents the final architecture and lessons learned (at least 200 words).
- [ ] 5 tool-calling regression tests exist and pass.
- [ ] The application is deployed and running on the VM.
- [ ] The agent passes the autochecker bot benchmark (≥75%).
- [ ] [Git workflow](../../../wiki/git-workflow.md): issue `[Task] The System Agent`, branch, PR with `Closes #...`, partner approval, merge.
