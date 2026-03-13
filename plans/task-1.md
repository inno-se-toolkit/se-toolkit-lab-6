# Task 1 Plan – Call an LLM from Code

## Goal

Build a CLI agent that sends a question to an LLM and returns JSON.

## LLM Provider

OpenRouter

## Model

meta-llama/llama-3.3-70b-instruct:free

## Architecture

User question → agent.py → LLM API → JSON response

Steps:

1. Read question from CLI
2. Load API config from `.env.agent.secret`
3. Send request to OpenRouter
4. Extract answer
5. Output JSON:

{
  "answer": "...",
  "tool_calls": []
}
