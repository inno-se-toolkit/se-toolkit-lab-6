# Plan: Task 1 - Call an LLM from Code

## Objective
Build a basic `agent.py` CLI that takes a question as a command-line argument, sends it to an LLM, and returns a JSON response containing the answer and an empty list of tool calls.

## Strategy
- Use `pydantic` or simple `json` for output formatting to ensure strict compliance with the required JSON schema: `{"answer": "...", "tool_calls": []}`.
- Use `openai` Python library to interact with the LLM API.
- Load configuration from `.env.agent.secret` using `python-dotenv`.
- All logs and debug info will be directed to `stderr`.

## Components
1. **Environment Setup**: Ensure `.env.agent.secret` is properly configured with:
   - `LLM_API_KEY`
   - `LLM_API_BASE` (pointing to the VM: `http://10.93.26.56:42005/v1`)
   - `LLM_MODEL` (`qwen3-coder-plus`)
2. **`agent.py`**:
   - Parse command line arguments using `sys.argv`.
   - Initialize the OpenAI client.
   - Send a chat completion request.
   - Print the JSON response to `stdout`.
3. **`AGENT.md`**: Document the setup and how to run the agent.
4. **Tests**: Create `tests/test_agent_basic.py` using `pytest` to verify the subprocess output.

## LLM Provider
- **Provider**: Qwen Code API (self-hosted proxy on VM).
- **Model**: `qwen3-coder-plus`.
