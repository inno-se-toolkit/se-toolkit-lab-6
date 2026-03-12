# Lab plan — Build Your Own Agent

**Topic:** Agent loop, LLM tool calling, CLI development, course review
**Date:** 2026-03-12

## Main goals

- Demystify the agent loop by building one from scratch.
- Reinforce understanding of all course material (labs 1-6) through a wiki-based agent and evaluation benchmark.
- Teach LLM API integration and tool calling as a transferable skill.

## Design principles

| Principle | Implication |
|-----------|-------------|
| Deterministic first, open-ended later | Task 2 has deterministic answers (wiki sections). Task 3 starts with static system facts, then adds data-dependent queries and hidden chain questions. |
| Learn by debugging, not by one-shotting | Students iterate against a benchmark. They see what fails, diagnose why, fix it, re-run. |
| Specify interfaces, not implementations | We define CLI input/output format, tool schemas, eval criteria. How they build the agent is up to them. |
| Build on what exists | The agent operates on the lab's own backend running locally via Docker Compose. No VM deployment. |

## Feedback addressed

| Concern | Source | Resolution |
|---------|--------|------------|
| Tool use behavior depends on the model | Colleague 1 | LLM setup + tool calling verification moved to Setup. Recommend specific models known to work. |
| Weak models give inconsistent results ("pay-to-win") | Colleague 1 | Task 2 answers are deterministic (wiki sections). Model quality matters less when the answer is a fact. |
| Answers aren't deterministic or verifiable by students | Colleague 2 | Task 2: wiki section = deterministic. Task 3: static system facts = deterministic. Data queries use range checks. |
| Students will hardcode if error messages show expected answers | Colleague 2 | Show feedback hints (not exact expected values). Hidden chain-of-tool questions can't be hardcoded. LLM judge for open-ended hidden questions. |
| Tool use questions come too late in benchmark | Colleague 1 | Task 2 requires tools from the start (read_file, list_files for wiki). Conceptual warm-up questions (tier 1) don't need tools. |

## Learning outcomes

By the end of this lab, students should be able to:

- [Understand] Explain how an agentic loop works: user input → LLM → tool call → execute → feed result → repeat until final answer.
- [Apply] Integrate with an LLM API using the OpenAI-compatible chat completions format with tool/function calling.
- [Apply] Implement tools that read files, list directories, and query HTTP APIs, then register them as function-calling schemas.
- [Apply] Build a CLI that accepts structured input and produces structured output (JSON).
- [Analyze] Debug agent behavior by examining tool call traces, identifying prompt issues, and fixing tool implementations.
- [Evaluate] Assess agent quality against a benchmark, iterating on prompts and tools to improve pass rate.

In simple words:

> 1. I can explain how an agent loop works — prompt, tool call, execute, feed back, repeat.
> 2. I can call an LLM API with tool definitions and handle structured responses.
> 3. I can build tools that read files, list directories, and query APIs, and wire them into an agent.
> 4. I can build a CLI that takes a question and outputs a JSON answer.
> 5. I can debug why my agent gives wrong answers by tracing tool calls and fixing prompts.
> 6. I can iterate on my agent until it passes a benchmark, improving prompts and tools along the way.

## Lab story

You have a running Learning Management Service from the previous lab — a backend, a database full of analytics data, and a frontend dashboard. Your project has a wiki full of documentation that nobody reads. You will build a CLI agent that reads the docs for you, answers questions about the course, and then connects to the live system to do something actually useful — analyze logs and diagnose bugs.

A senior engineer explains the assignment:

> 1. Start with the basics — call an LLM from code and get a structured JSON answer.
> 2. Give it tools to read files and navigate the wiki — now it's an actual agent, not just a chatbot.
> 3. Connect it to the live system, then iterate until it passes the evaluation benchmark.

## Required tasks

### Task 1 — Call an LLM from Code

**Purpose:**

Build the foundation: a CLI that connects to an LLM and returns structured JSON. No tools, no agentic loop — just the plumbing students will build on in Tasks 2–3.

**Summary:**

Students create `agent.py` in the project root. It takes a question as a CLI argument, sends it to an LLM (OpenRouter recommended, free tier), and outputs JSON with `answer` and `tool_calls` (empty array for now). Students set up LLM credentials in `.env.agent.secret`, write a plan, document in AGENT.md, and create 5 regression tests.

**Acceptance criteria:**

- `agent.py` outputs valid JSON with `answer` and `tool_calls`.
- API key stored in `.env.agent.secret`, not hardcoded. LLM config read from env vars.
- AGENT.md documents the solution. 1 regression test passes.
- PR merged closing the linked issue.

---

### Task 2 — The Documentation Agent

**Purpose:**

Turn the LLM wrapper into an actual agent by adding tools (`read_file`, `list_files`) and the agentic loop. The agent navigates the project wiki to answer questions.

**Summary:**

Students implement the agentic loop: send the question + tool definitions to the LLM, execute tool calls, feed results back, repeat until a final answer. The agent uses `read_file` and `list_files` to navigate `wiki/`, find the relevant section, and return `answer`, `source` (wiki section reference), and `tool_calls`.

**Acceptance criteria:**

- `read_file` and `list_files` defined as tool schemas.
- Agentic loop executes tool calls and feeds results back.
- `source` identifies the wiki section that answers the question.
- Tools restricted to project directory. AGENT.md updated. 2 more tests.
- PR merged closing the linked issue.

---

### Task 3 — The System Agent

**Purpose:**

Connect the agent to the live system with `query_api`, then iterate against the evaluation benchmark until it passes ≥75%.

**Summary:**

Students add a `query_api` tool (HTTP requests to deployed backend, authenticated with `LMS_API_KEY`). The agent can now answer static system facts (framework, ports, ORM) and data-dependent queries (item count, scores). Students run `uv run run_eval.py` to test locally, then submit to the autochecker bot which tests additional hidden questions. Hidden questions include multi-step challenges requiring tool chaining. Students iterate until the benchmark passes ≥75%.

**Acceptance criteria:**

- `query_api` authenticates with the backend.
- Agent answers static system and data-dependent questions correctly.
- `uv run run_eval.py` passes all local questions.
- Autochecker bot benchmark ≥75% (clone_and_run with Groq on Hetzner).
- AGENT.md documents final architecture and lessons learned.
- 2 more tests. PR merged closing the linked issue.

---

## Optional task

### Task 1 — Advanced Agent Features

**Purpose:**

Extend the agent with advanced capabilities that improve reliability, expand coverage, or demonstrate deeper understanding of agent design.

**Summary:**

Students choose one or more extensions: retry logic with exponential backoff for rate-limited LLM APIs, a caching layer that avoids re-calling tools for repeated arguments, a `query_db` tool that runs read-only SQL queries against PostgreSQL directly, or multi-step reasoning where the agent plans before executing tools.

Students document their chosen extension in a plan, implement it, and write tests that demonstrate the improvement. The extension should measurably improve the agent.

**Acceptance criteria:**

- At least one extension is implemented and documented.
- Tests demonstrate the extension works correctly.
- AGENT.md is updated to describe the extension.
- PR is approved and merged, closing the linked issue.

---

## Infrastructure constraints

See [`autochecker/docs/infrastructure.md`](../../../autochecker/docs/infrastructure.md) for course-wide constraints (dev server, relay, university VMs, LLM API availability).

### Lab 6 implications

**No VM deployment.** Students run everything locally. Autochecker clones their repo on Hetzner, spins up their Docker Compose (backend + DB), and runs the agent with our Groq key. The `query_api` tool hits `localhost:42002` on Hetzner where we started their backend. No relay needed for eval.

**LLM key strategy:**

| Who | Key | Provider | Where it runs |
|-----|-----|----------|--------------|
| Student (local dev) | Their own OpenRouter key (free tier, 50 RPD) | OpenRouter | Student's machine |
| Student (`run_eval.py`) | Same OpenRouter key | OpenRouter | Student's machine |
| Autochecker (grading) | Our Groq key | Groq (`llama-3.1-8b-instant`) | Hetzner (clone_and_run) |

The student's `agent.py` must read `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL` from **environment variables** (not hardcoded). The `.env.agent.secret` file is a local convenience. The autochecker injects its own Groq credentials when running the agent.

**clone_and_run eval flow (task 3):**

```
Hetzner (autochecker):
  1. git clone student repo (shallow)
  2. Create .env.docker.secret with known credentials
  3. docker compose up --build -d (backend + postgres)
  4. Wait for healthy, POST /pipeline/sync (populate DB)
  5. For each eval question:
     LLM_API_KEY=groq_key \
     LLM_API_BASE=https://api.groq.com/openai/v1 \
     LLM_MODEL=llama-3.1-8b-instant \
     LMS_API_KEY=known_key \
     AGENT_API_BASE_URL=http://localhost:42002 \
     python agent.py "question"
  6. Check answers against expected (matching, LLM judge)
  7. docker compose down -v
  8. Clean up cloned repo
```

**What we check without running code (tasks 1-2):**

For tasks 1-2, we only do repo-level checks (no execution). This avoids burning student's LLM API quota and running untrusted code unnecessarily.

| Check type | What it verifies | Examples |
|-----------|-----------------|---------|
| `file_nonempty` | Deliverable files exist | `plans/task-1.md`, `agent.py`, `AGENT.md` |
| `regex_in_file` | Code structure | `read_file` appears 2+ times in agent.py |
| `glob_exists` | Test files exist | `test_*.py` or `tests/test_*.py` |
| `issue_exists` | Git workflow | Issue with correct title |
| `issue_has_linked_pr` | Git workflow | PR closes the issue, is merged |
| `issue_pr_approved` | Code review | PR has ≥1 approval |
| `commit_message_regex` | Commit conventions | Starts with `feat:` |

Task 3 execution checks (clone_and_run) implicitly validate that tasks 1-2 work correctly — if `agent.py` doesn't output valid JSON or tools don't work, eval questions fail.

## Architecture

```
Student's machine (local development):
  agent.py (CLI) ←→ OpenRouter API (free LLM)
       │
       ├── read_file(path)   → wiki/, source code, config
       ├── list_files(dir)   → wiki/, directories
       └── query_api(path)   → localhost:42002 (local Docker Compose)

Autochecker (Hetzner, clone_and_run for task 3):
  1. Clone student repo
  2. docker compose up (backend + DB on Hetzner)
  3. Populate DB (POST /pipeline/sync)
  4. For each question: inject Groq env vars → python agent.py "question"
  5. Check answers → docker compose down → clean up
```

## LLM access

**Provider:** OpenRouter (free tier, zero cost).

- OpenAI-compatible API (`POST /v1/chat/completions`).
- Students create an account at openrouter.ai, get an API key (no credit card).
- LLM setup is part of the Setup task — students verify tool calling works before starting graded tasks.

**Recommended models** (free, reliable tool calling):

| Model | Context | Tool calling | Notes |
|-------|---------|-------------|-------|
| `meta-llama/llama-4-scout:free` | 512k | Strong | Best free option |
| `meta-llama/llama-3.3-70b-instruct:free` | 128k | Strong | Reliable fallback |
| `qwen/qwen-2.5-72b-instruct:free` | 128k | Good | Alternative |

**Configuration:** `.env.agent.secret` (gitignored), with `.env.agent.example` committed.

- `LLM_API_KEY` — LLM provider API key.
- `LLM_API_BASE` — OpenAI-compatible endpoint URL.
- `LLM_MODEL` — model name.

> Two distinct keys: `LMS_API_KEY` (in `.env.docker.secret`) protects the backend. `LLM_API_KEY` (in `.env.agent.secret`) authenticates with the LLM provider.

## CLI interface

**Input:**

```bash
uv run agent.py "How do you resolve a merge conflict?"
```

**Output:**

```json
{
  "answer": "Edit the conflicting file, choose which changes to keep, then stage and commit.",
  "source": "wiki/git-workflow.md#resolving-merge-conflicts",
  "tool_calls": [
    {"tool": "list_files", "args": {"path": "wiki"}, "result": "git-workflow.md\n..."},
    {"tool": "read_file", "args": {"path": "wiki/git-workflow.md"}, "result": "..."}
  ]
}
```

**Fields:**

- `answer` (string, required) — the agent's answer.
- `source` (string, optional) — wiki section reference. Absent in Task 1, required in Task 2, optional in Task 3.
- `tool_calls` (array, required) — tool calls made. Empty array if none.

**Rules:**

- Valid JSON, single line, to stdout.
- Debug/progress output to stderr only.
- 60-second timeout per question.
- Exit code 0 on success.
- Maximum 10 tool calls per question.

## Required tools

### `read_file`

- **Parameters:** `path` (string) — relative path from project root.
- **Returns:** file contents as string, or error message.
- **Security:** must restrict to project directory.
- **Used in:** Task 2 (wiki files), Task 3 (source code, config, tracing bugs).

### `list_files`

- **Parameters:** `path` (string) — relative directory path.
- **Returns:** newline-separated listing.
- **Security:** must restrict to project directory.
- **Used in:** Task 2 (discover wiki files), Task 3 (explore code structure).

### `query_api`

- **Parameters:** `method` (string), `path` (string), `body` (string, optional).
- **Returns:** JSON with `status_code` and `body`.
- **Auth:** uses `LMS_API_KEY` from `.env.docker.secret`.
- **Introduced in:** Task 3.

## Question classes

### Class A: Wiki lookup (Task 2)

Questions about course material. The answer lives in a wiki section.

```yaml
- index: 0
  class: A
  task: 2
  question: "How do you resolve a merge conflict?"
  expected_source: {any_of: ["wiki/git-workflow.md#resolving-merge-conflicts",
                              "wiki/git-workflow.md#merge-conflicts"]}
  expected_answer: {any_of: ["edit", "resolve", "choose", "stage"]}
  check_tools: [read_file]
```

**Checking:**

| Field | Check | Required |
|-------|-------|----------|
| `source` | Matches `expected_source` (exact or `any_of`) | Yes |
| `answer` | Contains keywords from `expected_answer` | Optional |
| `tool_calls` | Includes tools from `check_tools` | Yes |

**Why deterministic:** The correct section is a fact. Students verify by reading the section.

**Count:** ~15 in `run_eval.py`, ~5 hidden.

### Class B: Static system facts (Task 3)

Questions where the answer is baked into the code/config and never changes.

```yaml
- index: 16
  class: B
  task: 3
  question: "What HTTP status code does the API return when you request /items/ without authentication?"
  expected: {any_of: ["401", "403"]}
  feedback: "Try making a request without the API key header and check the response status code."
  check_tools: [query_api]
```

**Checking:**

| Field | Check | Required |
|-------|-------|----------|
| `answer` | Matches `expected` (contains, any_of, regex) | Yes |
| `tool_calls` | Includes tools from `check_tools` | Yes |

**On failure:** Show `feedback` (a hint toward the right approach), not the `expected` value.

**Count:** ~8 in `run_eval.py`, ~3 hidden.

### Class C: Data-dependent system queries (Task 3)

Questions about live data. Answer varies per student.

```yaml
- index: 24
  class: C
  task: 3
  question: "How many items are currently in the database?"
  expected: {numeric_gt: 0}
  feedback: "Query the /items/ endpoint with authentication and count the results."
  check_tools: [query_api]
```

**Checking:**

| Field | Check | Required |
|-------|-------|----------|
| `answer` | Matches `expected` (numeric_gt, numeric_range) | Yes |
| `tool_calls` | Includes tools from `check_tools` | Yes |

**On failure:** Show `feedback`.

**Count:** ~3 in `run_eval.py`, ~2 hidden.

### Class D: Bug diagnosis chain (Task 3, hidden only)

Multi-step questions. The agent calls an API endpoint that triggers a planted bug, sees the error response, reads the source code to identify the cause, and explains the fix.

```yaml
- index: 34
  class: D
  task: 3
  bot_only: true
  question: "Query the analytics pass-rates endpoint for a lab that doesn't exist. What error do you get, and what's the bug in the source code?"
  expected: {any_of: ["ZeroDivisionError", "division by zero", "divide by zero"]}
  expected_source: {contains: "analytics.py"}
  feedback: "Try GET /analytics/pass-rates?lab=lab-99 and read the error. Then check the source code."
  check_tools: [query_api, read_file]
```

**Checking:**

| Field | Check | Required |
|-------|-------|----------|
| `answer` | Contains bug identifier (`expected`) | Yes |
| `source` | Contains file path (`expected_source`) | Yes |
| `tool_calls` | Includes ALL tools from `check_tools` (chain) | Yes |

**On failure:** Show `feedback` (points to where to look, not the answer).

**Count:** 2-3 hidden (bot eval only).

### Class E: LLM-judged reasoning (Task 3, hidden only)

Open-ended questions where keyword matching isn't sufficient.

```yaml
- index: 35
  class: E
  task: 3
  bot_only: true
  question: "Compare how the ETL pipeline handles failures vs how the API endpoints handle failures. Which is more robust and why?"
  rubric: "Answer must: (1) describe ETL error handling, (2) describe API error handling, (3) compare them, (4) give a reasoned judgment."
  feedback: "Read both the ETL code and the API router code, then compare their error handling strategies."
  check_tools: [read_file]
```

**Checking:**

| Field | Check | Required |
|-------|-------|----------|
| `answer` | LLM judge evaluates against `rubric` | Yes |
| `tool_calls` | Includes tools from `check_tools` | Yes |

**Budget:** ~5 questions × ~$0.01/judge call = ~$0.05/student. ~$3 for 60 students. Use a cheap fast model (Haiku/Flash) as judge.

**Count:** 3-5 hidden (bot eval only).

### Summary: questions per task

| Class | Task | `run_eval.py` | Bot-only | Checking | On failure |
|-------|------|--------------|----------|----------|------------|
| A: Wiki lookup | 2 | ~15 | ~5 | Source path match + tool use | Show expected source |
| B: Static system facts | 3 | ~8 | ~3 | Keyword match + tool use | Show `feedback` hint |
| C: Data-dependent queries | 3 | ~3 | ~2 | Numeric range + tool use | Show `feedback` hint |
| D: Bug diagnosis chain | 3 | 0 | 3-5 | Bug ID in `answer` + file in `source` + tool chain | Show `feedback` hint |
| E: LLM-judged reasoning | 3 | 0 | 3-5 | LLM judge + tool use | Show `feedback` hint |
| **Total** | | **~26** | **~13-17** | | |

## Evaluation system

### Two paths

| | Local (`run_eval.py`) | Bot (autochecker, clone_and_run) |
|--|----------------------|--------------------------------|
| Triggered by | Student runs locally | `/check` in Telegram |
| Questions | 10 local (from API) | 10 local + 10 hidden |
| Where agent runs | Student's machine | Hetzner (cloned repo + Docker Compose) |
| LLM key | Student's OpenRouter (free tier) | Our Groq key (injected via env vars) |
| Backend | Student's local Docker Compose | Cloned Docker Compose on Hetzner |
| On failure shows | `feedback` hint (not expected value) | Same |
| Purpose | Fast iteration | Grading |

### Anti-gaming

- Task 2 answers are deterministic wiki sections — hardcoding requires the wiki files.
- Failure feedback shows hints, not expected values (Classes B-E).
- Hidden questions include multi-tool chains that can't be hardcoded.
- LLM judge for open-ended hidden questions.
- Tool call verification ensures the agent actually used tools.
- Every API request is logged.

### `run_eval.py`

```bash
uv run run_eval.py           # all questions, stop at first fail
uv run run_eval.py --index 5 # single question (for debugging)
```

## Wiki requirements

Task 2 depends on a comprehensive wiki covering labs 1-6.

| Topic | Lab | Wiki file |
|-------|-----|-----------|
| Git workflow, branching, PRs | 1 | `wiki/git-workflow.md` |
| Backend basics, FastAPI | 2 | `wiki/backend.md` |
| Docker, Compose, volumes | 2 | `wiki/docker.md` |
| REST API, HTTP methods | 3 | `wiki/rest-api.md` |
| Database, SQL, ORM | 3 | `wiki/database.md` |
| Authentication, security | 3 | `wiki/security.md` |
| Testing, pytest | 4 | `wiki/testing.md` |
| Frontend, React | 4 | `wiki/frontend.md` |
| ETL, data pipelines | 5 | `wiki/etl.md` |
| Analytics, SQL aggregation | 5 | `wiki/analytics.md` |
| Agents, tool calling | 6 | `wiki/agents.md` |

**Action needed:** Audit existing wiki, identify gaps, write missing sections.

## Planted bugs (Task 3)

Non-critical bugs in the backend that produce visible error responses when specific endpoints are triggered. The agent discovers them by querying the API, seeing the error, then reading the source code to diagnose the cause.

| # | Bug | File | API behavior | Trigger |
|---|-----|------|-------------|---------|
| 1 | Division by zero in completion rate when no learners exist | `analytics.py` (`get_completion_rate`) | 500 with `ZeroDivisionError` | GET `/analytics/completion-rate?lab=lab-99` |
| 2 | TypeError sorting None scores in top learners | `analytics.py` (`get_top_learners`) | 500 with `TypeError` | GET `/analytics/top-learners?lab=X` when any learner has all-NULL scores |

**Discovery flow (what the agent does):**

```
query_api(GET /analytics/completion-rate?lab=lab-99)
  → 500: {"detail": "division by zero", "type": "ZeroDivisionError", ...}
read_file(backend/app/routers/analytics.py)
  → finds line: rate = (passed_learners / total_learners) * 100
  → no guard for total_learners == 0
answer: "ZeroDivisionError — completion-rate divides by total_learners without checking for zero"
```

**Error visibility:** A custom exception handler in `main.py` returns `{"detail": ..., "type": ..., "traceback": [...]}` so the agent gets actionable error info in the API response.

Requirements:

- Must not break existing lab 5 functionality or autochecker checks.
- Must produce visible error responses the agent can find via `query_api`.
- Must be diagnosable by reading the source code with `read_file`.
- Must have clear fixes the agent can suggest.

### Future: log-based discovery

The current approach uses API error responses — the agent hits a buggy endpoint and sees the error directly. A more realistic version would use application logs:

1. Add Python `logging` to the backend (structured JSON logs to a file or stdout).
2. Expose logs via a `GET /logs` endpoint (authenticated, read-only, returns recent entries) or let the agent `read_file` on a log path.
3. Plant bugs that don't return errors to the caller but silently log warnings/errors (e.g., caught exceptions, data inconsistencies).
4. Class D questions become: "Check the application logs for errors" → agent queries `/logs` → sees traceback → reads source → explains fix.

This is a better model of real-world debugging (errors are often silent to the user but visible in logs). Deferred to a future iteration because it requires adding a logging framework to the backend.

## Decisions

| # | Decision |
|---|----------|
| 1 | No starter `agent.py` skeleton — students build from scratch, plan first. |
| 2 | LLM setup in Task 1 — students get LLM working before adding tools. |
| 3 | Recommend strong free models first (Llama 4 Scout, Llama 3.3 70B, Qwen 2.5 72B). |
| 4 | Task 2 uses wiki lookup — deterministic, verifiable, teaches tools. |
| 5 | Task 2 output: answer + source — source is deterministic, answer shows understanding. |
| 6 | Tool call verification is loose — check tool was used, not exact args. |
| 7 | Max 10 tool calls per question. |
| 8 | Static facts (deterministic) + range checks for data-dependent questions. |
| 9 | Failure feedback shows hints, not expected values (Classes B-E). |
| 10 | Hidden chain-of-tool questions + LLM judge prevent hardcoding. |
| 11 | Plain string input (`uv run agent.py "..."`). |
| 12 | `LMS_API_KEY` (backend) vs `LLM_API_KEY` (LLM provider). |
| 13 | `.env.agent.secret` for LLM config (gitignored). |
| 14 | 2 planted non-critical bugs producing 500 errors for Task 3 Class D questions. |
| 15 | LLM judge budget: ~$3 total for 60 students. |
| 16 | `run_eval.py` supports `--index N` for single-question debugging. |
| 17 | No VM deployment — students develop locally, autochecker evaluates via clone_and_run on Hetzner. |
| 18 | Agent reads LLM config from env vars (`LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL`). `.env.agent.secret` is convenience only. |
| 19 | Autochecker uses Groq (`llama-3.1-8b-instant`) for eval, not student's OpenRouter key. |
| 20 | Tasks 1-2: repo-level checks only (no code execution). Task 3: clone_and_run with full eval. |
| 21 | `AGENT_API_BASE_URL` env var for query_api base URL (defaults to `http://localhost:42002`). |

## Remaining work

**Done:**

- [x] Rewrite Task 1 (`task-1.md`) — call an LLM from code.
- [x] Rewrite Task 2 (`task-2.md`) — documentation agent.
- [x] Rewrite Task 3 (`task-3.md`) — system agent + benchmark (merged from old task 4).
- [x] Update optional task file.
- [x] Update README to match 3-task structure.
- [x] Write Class B questions (static system facts via read_file/list_files, tier 2).
- [x] Write Class C questions (data-dependent queries via query_api, tier 2).
- [x] Add `source_match` checking to `run_eval.py` and engine.
- [x] Update `run_eval.py` with `--index` flag and feedback display.
- [x] Add `feedback` hints to eval questions (tier 2+).
- [x] Update autochecker spec (`lab-06.yaml`).

- [x] Implement planted bugs in backend (`completion-rate`, `top-learners` endpoints).
- [x] Write Class D questions (2 bug diagnosis chains, bot-only).
- [x] Add `check_tools` / tool chain checking to engine.
- [x] Add exception handler in `main.py` for visible error responses.
- [x] Write Class E questions (3 LLM-judged reasoning, bot-only).
- [x] Add `llm_judge` checking to engine (uses OpenRouter, llama-4-scout:free).
- [x] Deploy autochecker with Class D/E questions and LLM judge.

**Remaining:**

- [ ] **Replace tier 1 conceptual questions with Class A wiki-lookup questions.** Current tier 1 (index 0-16) tests LLM knowledge, not wiki tools. Need questions with `expected_source` and `check_tools: [read_file]` that verify the documentation agent actually navigates the wiki. Requires wiki content to exist first.
- [ ] Audit existing wiki content — what's there, what's missing.
- [ ] Write missing wiki sections (labs 1-6 material).
- [ ] **Implement `agent_eval` clone_and_run mode in autochecker engine.** Clone repo, docker compose up, populate DB, run agent with injected Groq env vars, evaluate answers, tear down. Must not break existing SSH-based `agent_eval`.
- [ ] **Update `lab-06.yaml`** — remove SSH/VM checks from setup and tasks 1-2, add clone_and_run eval for task 3.
- [ ] **Update task-3.md** — remove VM deployment section, add env var requirements (`LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL`, `AGENT_API_BASE_URL` from env vars).
- [ ] Add logging framework to backend + `/logs` endpoint (future — see planted bugs section).
