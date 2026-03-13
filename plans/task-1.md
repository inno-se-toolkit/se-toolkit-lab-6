# Task 1 plan

Provider: Qwen Code API (recommended) or OpenRouter.
Config in .env.agent.secret: LLM_API_KEY, LLM_API_BASE, LLM_MODEL.

agent.py:
- read question from argv
- load .env.agent.secret
- call OpenAI-compatible /chat/completions via HTTP
- print single-line JSON: {"answer": "...", "tool_calls": []}
- debug only to stderr

Tests:
- run agent.py as subprocess
- parse stdout JSON
- check keys answer/tool_calls exist
