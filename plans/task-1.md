LLM provider used: Qwen Code API
Model of LLM provider: coder-model
Agent Structure:
A Python CLI program (agent.py) that takes a question, sends it to an LLM, and returns a structured JSON answer.
User question → agent.py → LLM API → JSON answer
Input — a question as the first command-line argument:
uv run agent.py "What does REST stand for?"
Output — a single JSON line to stdout:
{"answer": "Representational State Transfer.", "tool_calls": []}
answer and tool_calls fields are required in the output.
Only valid JSON goes to stdout. All debug/progress output goes to stderr.
The agent must respond within 60 seconds.
Exit code 0 on success.
