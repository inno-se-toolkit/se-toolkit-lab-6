I will use qwen3-coder-plus.

Agent structure:
The agent will be implemented as a CLI application in agent.py that uses the qwen3-coder-plus model through an OpenAI-compatible chat completions interface. For this task, the agent will have a minimal system prompt. The CLI will parse the question from the terminal, send it to the LLM, receive the text response, and output a single JSON line with the following structure { “answer”: “<response>”, “tool_calls”: [] }. The LLM API credentials (LLM_API_KEY, LLM_API_BASE, LLM_MODEL) will be read from the .env.agent.secret file.
