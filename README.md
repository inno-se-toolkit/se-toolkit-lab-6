# Lab 6 — Build Your Own Agent

The lab gets updated regularly, so do [sync your fork with the upstream](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork#syncing-a-fork-branch-from-the-command-line) from time to time.

<h2>Table of contents</h2>

- [Lab story](#lab-story)
- [Learning advice](#learning-advice)
- [Learning outcomes](#learning-outcomes)
- [Tasks](#tasks)
  - [Prerequisites](#prerequisites)
  - [Required](#required)
  - [Optional (recommended)](#optional-recommended)

## Lab story

> "Everybody should implement an agent loop at some point. It's the hello-world of agentic engineering."

You've used AI agents throughout the course — now you'll build one from scratch.

You have a running Learning Management Service — a backend, a database, and a frontend dashboard. You'll build a **CLI agent** that answers questions about the course and about your own system, and then evaluate the agent against a benchmark.

## Learning advice

This lab is different from previous ones. You are not following step-by-step instructions — you are building something and iterating until it works. Use your coding agent to help you understand and plan:

> Read task X. What exactly do we need to deliver? Explain, I want to understand.

> Why does an agent need a loop? Walk me through the flow.

> My agent failed this question: "...". Diagnose why and suggest a fix.

The agent you build is simple (~100-200 lines). The learning comes from debugging it against the benchmark — each failure teaches you something about agents or course material.

You need a coding agent that has access to the whole repo to work effectively.

## Learning outcomes

By the end of this lab, you should be able to:

- Explain how an agentic loop works: user input → LLM → tool call → execute → feed result → repeat until final answer.
- Integrate with an LLM API using the OpenAI-compatible chat completions format with tool/function calling.
- Implement tools that read files, list directories, and query HTTP APIs, then register them as function-calling schemas.
- Build a CLI that accepts structured input and produces structured output (JSON).
- Debug agent behavior by examining tool call traces, identifying prompt issues, and fixing tool implementations.
- Assess agent quality against a benchmark, iterating on prompts and tools to improve pass rate.

In simple words, you should be able to say:
>
> 1. I built an agent that calls an LLM and answers questions!
> 2. I gave it tools to read files and query my API!
> 3. I iterated until it passed the evaluation benchmark!

## Tasks

### Prerequisites

1. Complete the [lab setup](./lab/tasks/setup-simple.md#lab-setup)

> **Note**: If this is the first lab you are attempting in this course, you need to do the [full version of the setup](./lab/tasks/setup.md#lab-setup)

### Required

1. [Basic agent loop](./lab/tasks/required/task-1.md#basic-agent-loop)
2. [Add tools](./lab/tasks/required/task-2.md#add-tools)
3. [Pass the benchmark](./lab/tasks/required/task-3.md#pass-the-benchmark)

### Optional (recommended)

1. [Advanced agent features](./lab/tasks/optional/task-1.md#advanced-agent-features)
