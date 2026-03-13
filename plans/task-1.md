# Task 1: Call an LLM from Code - Implementation Plan

## LLM Provider Choice
I will use **Qwen Code API** because:
- 1000 free requests per day
- Works without VPN
- No credit card required
- Strong tool-calling support (will be needed in later tasks)

## Model Selection
- **Model**: qwen3-coder-plus (recommended in .env.agent.example)
- **Reason**: Best balance of performance and cost, good for coding tasks

## Agent Structure
The agent will:
1. Load environment variables from `.env.agent.secret`
2. Read question from command-line argument
3. Make API call to Qwen Code endpoint using OpenAI-compatible interface
4. Parse response and extract the answer
5. Output JSON with format: `{"answer": "...", "tool_calls": []}`
6. Send all debug/progress output to stderr, only JSON to stdout

## Implementation Steps
1. Create `.env.agent.secret` from `.env.agent.example`
2. Install required dependencies: `openai`, `python-dotenv`
3. Implement `agent.py` with:
   - Argument parsing
   - Environment variable loading
   - API client setup
   - LLM call with timeout (60 seconds)
   - JSON output formatting
4. Create `AGENT.md` documentation
5. Write regression test

## Error Handling
- Missing API key → exit with error message to stderr
- API timeout/error → exit with error message to stderr
- Invalid input → exit with error message to stderr