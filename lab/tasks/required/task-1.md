# Call an LLM from Code

Build a CLI that connects to an LLM and answers questions. This is the foundation for the agent you will build in the next tasks.

## What you will build

A `Python` CLI program (`agent.py`) that takes a question, sends it to an LLM, and returns a structured JSON answer. No tools or agentic loop yet — just the basic plumbing: parse input, call the LLM, format output. You will add tools and the agentic loop in Tasks 2–3.

```
User question → agent.py → LLM API → JSON answer
```

**Input** — a question as the first command-line argument:

```bash
uv run agent.py "What does REST stand for?"
```

**Output** — a single JSON line to stdout:

```json
{"answer": "Representational State Transfer.", "tool_calls": []}
```

**Rules:**

- `answer` and `tool_calls` fields are required in the output.
- `tool_calls` is an empty array for this task (you will populate it in Task 2).
- Only valid JSON goes to stdout. All debug/progress output goes to **stderr**.
- The agent must respond within 60 seconds.
- Exit code 0 on success.

## How to get access to an LLM?

Your agent needs an LLM that supports the OpenAI-compatible chat completions API. You are free to use any provider.

[OpenRouter](https://openrouter.ai) offers free models with no credit card required. Look for models that support **tool calling** — you will need this in later tasks.

**Recommended models** (free, reliable tool calling):

| Model | Tool calling | Notes |
|-------|-------------|-------|
| `meta-llama/llama-4-scout:free` | Strong | Best free option |
| `meta-llama/llama-3.3-70b-instruct:free` | Strong | Reliable fallback |
| `qwen/qwen-2.5-72b-instruct:free` | Good | Alternative |

Register in OpenRouter and get an API key from them. This will be your LLM_API_KEY in `.env.agent.secret` (gitignored by the `*.secret` pattern). An example file is provided:

```bash
cp .env.agent.example .env.agent.secret
```

Edit `.env.agent.secret` and fill in `LLM_API_KEY`, `LLM_API_BASE`, and `LLM_MODEL`. Your agent reads from this file.

> **Note:** This is **not** the same as `LMS_API_KEY` in `.env.docker.secret`. That one protects your backend LMS endpoints. `LLM_API_KEY` authenticates with your LLM provider.

> [!WARNING]
> Free-tier models on OpenRouter have a **50 requests per day** limit per account. Plan your testing carefully:
> - Use short, focused test runs instead of running the full eval repeatedly.
> - Consider creating multiple OpenRouter accounts if you hit the limit.
> - Implement retry logic with backoff for `429` errors (see [Optional Task 1](../optional/task-1.md#advanced-agent-features)).

## Deliverables

### 1. Plan (`plans/task-1.md`)

Before writing code, create `plans/task-1.md`. Describe which LLM provider and model you will use, and how you will structure the agent.

### 2. Agent (`agent.py`)

Create `agent.py` in the project root. The system prompt can be minimal for now — you will expand it in later tasks when you add tools and domain knowledge.

### 3. Documentation (`AGENT.md`)

Create `AGENT.md` in the project root documenting how the agent works, which LLM provider you chose, and how to run it.

### 4. Tests (1 test)

Create 1 regression test that runs `agent.py` as a subprocess, parses the stdout JSON, and checks that `answer` and `tool_calls` are present.

## Acceptance criteria

- [ ] `plans/task-1.md` exists with the implementation plan (committed before code).
- [ ] `agent.py` exists in the project root.
- [ ] `uv run agent.py "..."` outputs valid JSON with `answer` and `tool_calls`.
- [ ] The API key is stored in `.env.agent.secret` (not hardcoded).
- [ ] `AGENT.md` documents the solution architecture.
- [ ] 1 regression test exists and passes.
- [ ] [Git workflow](../../../wiki/git-workflow.md): issue `[Task] Call an LLM from Code`, branch, PR with `Closes #...`, partner approval, merge.
