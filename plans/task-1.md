# Task 1 Plan

## LLM provider
I will use Qwen Code API deployed on my VM.

## Model
I will use qwen3-coder-plus.

## Agent structure
The agent will:
1. Read the user question from the first CLI argument.
2. Load LLM settings from .env.agent.secret.
3. Send a chat completion request to the OpenAI-compatible API.
4. Extract the assistant answer.
5. Print a JSON object with:
   - answer
   - tool_calls (empty list for this task)

## Output rules
- Only JSON to stdout
- Debug info to stderr
- Exit code 0 on success