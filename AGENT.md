# Agent — Task 1: Call an LLM from Code

## Overview

This agent is a simple CLI program that connects to an LLM and answers questions. It's the foundation for the more advanced agents you'll build in Tasks 2–3 (with tools and agentic loop).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     agent.py (CLI)                          │
│                                                             │
│  Input:  uv run agent.py "What does REST stand for?"        │
│                                                             │
│  1. Parse command-line argument                             │
│  2. Load LLM config from .env.agent.secret                  │
│  3. Call LLM API (HTTP POST)                                │
│  4. Parse response                                          │
│  5. Output JSON to stdout                                   │
│                                                             │
│  Output: {"answer": "...", "tool_calls": []}                │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP POST /v1/chat/completions
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Qwen Code API (on VM)                          │
│         http://10.93.26.121:8080/v1                         │
└─────────────────────────────────────────────────────────────┘
```

## LLM Provider

### Chosen Provider: Qwen Code API

**Why Qwen Code:**
- ✅ 1000 free requests per day
- ✅ Works from Russia (no VPN needed)
- ✅ No credit card required
- ✅ OpenAI-compatible API format
- ✅ Strong tool calling support (for future tasks)

### Model Configuration

| Setting | Value |
|---------|-------|
| **Model** | `qwen3-coder-plus` |
| **API Base** | `http://10.93.26.121:8080/v1` (deployed on VM) |
| **API Key** | Stored in `.env.agent.secret` |

### Alternative Providers

You can use any LLM provider that supports the OpenAI-compatible chat completions API:

- **OpenRouter**: Multiple models, some free tiers
- **Groq**: Fast inference, free tier available
- **OpenAI**: Industry standard, requires credit card

To switch providers, update `.env.agent.secret`:

```bash
LLM_API_KEY=<your-api-key>
LLM_API_BASE=https://api.openai.com/v1  # or other provider
LLM_MODEL=gpt-4o-mini  # or other model
```

## Configuration

### Environment File: `.env.agent.secret`

The agent reads configuration from `.env.agent.secret` in the project root:

```bash
# LLM provider API key
LLM_API_KEY=your-api-key-here

# API base URL (OpenAI-compatible endpoint)
LLM_API_BASE=http://10.93.26.121:8080/v1

# Model name
LLM_MODEL=qwen3-coder-plus
```

> **Note:** This is **NOT** the same as `LMS_API_KEY` in `.env.docker.secret`. That key protects your backend LMS endpoints. `LLM_API_KEY` authenticates with your LLM provider.

## Usage

### Basic Usage

```bash
# Run with a question
uv run agent.py "What does REST stand for?"
```

### Example Output

```json
{"answer": "REST stands for Representational State Transfer. It is an architectural style for designing networked applications, typically using HTTP.", "tool_calls": []}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success — valid JSON output |
| `1` | Error — missing argument, API failure, timeout |

### Error Cases

```bash
# No argument provided
uv run agent.py
# Error: Missing question argument
# Usage: uv run agent.py "your question"

# API timeout (>60 seconds)
uv run agent.py "very complex question..."
# Error: LLM API timeout after 60 seconds
```

## Implementation Details

### File Structure

```
se-toolkit-lab-6/
├── agent.py                 # Main CLI agent
├── .env.agent.secret        # LLM configuration (gitignored)
├── .env.agent.example       # Example configuration
├── plans/
│   └── task-1.md           # Implementation plan
├── tests/
│   └── test_agent_task1.py # Regression tests
└── AGENT.md                # This documentation
```

### Key Functions

**`load_llm_config()`**
- Loads environment variables from `.env.agent.secret`
- Validates required fields are present
- Returns dict with `api_key`, `api_base`, `model`

**`call_llm(question, config)`**
- Builds HTTP POST request to LLM API
- Sends request with 60-second timeout
- Parses JSON response
- Returns the answer string

**`format_response(answer, tool_calls)`**
- Builds the structured output dict
- Ensures required fields are present

**`main()`**
- Entry point
- Parses command-line arguments
- Orchestrates the flow
- Outputs JSON to stdout
- Errors go to stderr

### Output Format

**Success (stdout):**
```json
{"answer": "Representational State Transfer.", "tool_calls": []}
```

**Error (stderr, exit code 1):**
```
Error: Missing question argument
Usage: uv run agent.py "your question"
```

## Testing

### Run Tests

```bash
# Run all tests
uv run pytest tests/test_agent_task1.py -v

# Run with output capture
uv run pytest tests/test_agent_task1.py -v -s
```

### Test Coverage

| Test | Description |
|------|-------------|
| `test_agent_outputs_valid_json` | Runs agent, checks JSON structure |
| `test_agent_missing_argument` | Checks error handling for missing args |

### Test Assertions

1. Exit code is 0
2. Output is valid JSON
3. `answer` field exists and is a non-empty string
4. `tool_calls` field exists and is a list
5. `tool_calls` is empty (for Task 1)

## Troubleshooting

### "LLM_API_KEY not found"

**Problem:** `.env.agent.secret` is missing or incomplete

**Fix:**
```bash
cp .env.agent.example .env.agent.secret
nano .env.agent.secret  # Add your API key
```

### "Failed to connect to LLM API"

**Problem:** Can't reach the VM or Qwen API is not running

**Fix:**
1. Check you're on university network/VPN
2. Verify VM is accessible: `ssh root@10.93.26.121`
3. Check Qwen API is running: `docker compose -f ~/qwen-code-oai-proxy/docker-compose.yml ps`

### "LLM API timeout"

**Problem:** LLM took more than 60 seconds to respond

**Fix:**
- Try a simpler question
- Check VM has internet access
- Verify Qwen API has remaining quota (1000 requests/day)

### "Invalid response format"

**Problem:** LLM API returned unexpected JSON structure

**Fix:**
- Check the API response in debug mode
- Verify the model name is correct in `.env.agent.secret`

## Next Steps (Tasks 2–3)

In the next tasks, you'll extend this agent with:

**Task 2: The Documentation Agent**
- Add tools: `read_file`, `list_files`, `query_api`
- Implement function calling with the LLM
- Add agentic loop (think → act → observe → repeat)

**Task 3: The System Agent**
- Add domain knowledge (backend API, database schema)
- Implement more complex reasoning
- Handle multi-step questions

## License

This agent is part of the Software Engineering Toolkit course at Innopolis University.
