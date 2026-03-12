# Lab plan — Build Your Own Agent

**Topic:** Agent loop, LLM tool calling, CLI development, course review
**Date:** 2026-03-11

## Main goals

- Demystify the agent loop by building one from scratch.
- Reinforce understanding of all course material (labs 1-6) through an evaluation benchmark.
- Teach LLM API integration and tool calling as a transferable skill.

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

You have a running Learning Management Service from the previous lab — a backend, a database full of analytics data, and a frontend dashboard. The course is ending and you need to review everything you have learned. Instead of reviewing manually, you will build a CLI agent that answers questions about the course and about your own system, evaluated against a hidden benchmark — like building an algorithm against a test suite.

A senior engineer explains the assignment:

> 1. Build a CLI that takes a question, calls an LLM, and returns a JSON answer — the basic agent loop.
> 2. Give the agent tools to read your codebase and query your API — so it can answer questions about your actual system.
> 3. Iterate until the agent passes the evaluation benchmark — each failure teaches you something about agents or course material.

## Required tasks

### Task 1 — Call an LLM from Code

**Purpose:**

Build the foundation — a working CLI that calls an LLM and returns structured answers.

**Summary:**

Students create `agent.py` in the project root. The CLI accepts a plain string question as a command-line argument and outputs a JSON object with `answer` and `tool_calls` fields to stdout. All debug output goes to stderr.

Students choose an LLM provider (OpenRouter recommended for zero-cost access) and write a system prompt with course knowledge. The system prompt is the primary way the agent answers tier 1 questions that require no tools. Students write a plan before coding, document their architecture in AGENT.md, and create five regression tests.

The agent must work on the VM via SSH. At this stage, `tool_calls` is always an empty array because no tools are implemented yet.

**Acceptance criteria:**

- `agent.py` runs on the VM and exits with code 0.
- Output is valid JSON with `answer` and `tool_calls` fields.
- Plan and documentation files are committed before the agent code.
- At least five regression tests pass.
- PR is approved and merged, closing the linked issue.

---

### Task 2 — Add Tools

**Purpose:**

Implement the agentic loop with tools that let the agent inspect its own codebase and query the running API.

**Summary:**

Students implement three tools: `read_file` (reads a file from the project directory), `list_files` (lists directory contents), and `query_api` (makes HTTP requests to the deployed backend). Each tool is defined as a JSON schema in the `tools` parameter of the LLM API request.

Students build the agentic loop: call the LLM, check if it requests a tool call, execute the tool, send the result back as a `tool` role message, and repeat until the LLM produces a final text answer. A maximum of 10 iterations prevents infinite loops. File tools are restricted to the project directory for security. The `query_api` tool authenticates using `LMS_API_KEY` from the environment.

Students update their plan, documentation, and tests. The agent must handle tool-based evaluation questions.

**Acceptance criteria:**

- All three tools are implemented and appear in the agent's tool schemas.
- The agentic loop executes tool calls and feeds results back to the LLM.
- Tool-based evaluation questions return correct answers.
- At least five new regression tests verify tool usage.
- PR is approved and merged, closing the linked issue.

---

### Task 3 — Pass the Benchmark

**Purpose:**

Iterate on the agent until it passes the full evaluation benchmark, learning course material and agent debugging along the way.

**Summary:**

Students run `python run_eval.py` to test their agent against 25 questions fetched from the autochecker API. The script stops at the first failure, showing the question, the agent's answer, and the expected match criteria. Students diagnose each failure (wrong knowledge, missing tool call, broken tool, bad prompt phrasing) and fix it.

Common fixes include expanding the system prompt, improving tool descriptions so the LLM calls the right tool, fixing tool implementations, and handling edge cases. Students document their initial score, diagnosis of failures, and iteration strategy in a plan file. After passing all 25 local questions, they deploy and run the autochecker bot which tests 34 questions total (25 shared plus 9 never-seen extras).

Students update AGENT.md with the final architecture, lessons learned, and evaluation score.

**Acceptance criteria:**

- `run_eval.py` passes all 25 questions locally.
- The autochecker bot benchmark passes at least 75% (26 out of 34 questions).
- AGENT.md documents final architecture and lessons learned.
- Regression tests are updated with benchmark edge cases.
- PR is approved and merged, closing the linked issue.

---

## Optional task

### Task 1 — Advanced Agent Features

**Purpose:**

Extend the agent with advanced capabilities that improve reliability or expand what it can answer.

**Summary:**

Students choose one or more extensions to implement: retry logic with exponential backoff for rate-limited LLM APIs, a caching layer that avoids re-calling tools for repeated questions, a `query_db` tool that runs read-only SQL queries against the PostgreSQL database directly, or multi-step reasoning where the agent plans its approach before executing tools.

Students document their chosen extension in a plan, implement it, and write tests that demonstrate the improvement. The extension should measurably improve the agent — either by increasing the pass rate on edge cases, reducing latency, or handling failure modes gracefully.

**Acceptance criteria:**

- At least one extension is implemented and documented.
- Tests demonstrate the extension works correctly.
- AGENT.md is updated to describe the extension.
- PR is approved and merged, closing the linked issue.
