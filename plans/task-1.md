# Task 1 Plan: Call an LLM from Code

## Overview

Build a CLI program (`agent.py`) that:
1. Takes a question as a command-line argument
2. Sends it to an LLM via OpenAI-compatible API
3. Returns a structured JSON response with `answer` and `tool_calls` fields

## LLM Provider and Model

### Chosen Provider: Qwen Code API

**Why Qwen Code:**
- 1000 free requests per day
- Works from Russia (no VPN needed)
- No credit card required
- OpenAI-compatible API format
- Strong tool calling support (for future tasks)

### Model Configuration

| Setting | Value |
|---------|-------|
| Model | `qwen3-coder-plus` |
| API Base | `http://10.93.26.121:8080/v1` (VM) |
| API Key | Stored in `.env.agent.secret` |

### Environment Variables

The agent reads from `.env.agent.secret`:

```bash
LLM_API_KEY=<your-qwen-api-key>
LLM_API_BASE=http://10.93.26.121:8080/v1
LLM_MODEL=qwen3-coder-plus
```

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                     agent.py (CLI)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  1. Parse command-line argument (question)           │   │
│  │  2. Load LLM config from .env.agent.secret           │   │
│  │  3. Build system prompt                              │   │
│  │  4. Call LLM API (chat completions)                  │   │
│  │  5. Parse response                                   │   │
│  │  6. Output JSON to stdout                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP POST /v1/chat/completions
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Qwen Code API (on VM)                          │
│         http://10.93.26.121:8080/v1                         │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input:** `uv run agent.py "What does REST stand for?"`
2. **Parse:** Extract question from `sys.argv[1]`
3. **Load config:** Read `.env.agent.secret` using `python-dotenv`
4. **Build request:**
   ```python
   {
       "model": "qwen3-coder-plus",
       "messages": [
           {"role": "system", "content": "You are a helpful assistant."},
           {"role": "user", "content": "What does REST stand for?"}
       ]
   }
   ```
5. **Call API:** HTTP POST to `LLM_API_BASE/chat/completions`
6. **Parse response:** Extract `choices[0].message.content`
7. **Output JSON:**
   ```json
   {"answer": "Representational State Transfer.", "tool_calls": []}
   ```

## Output Format

### Success Response (stdout)

```json
{"answer": "Representational State Transfer.", "tool_calls": []}
```

### Error Response (stderr, exit code 1)

```
Error: Missing question argument
Usage: uv run agent.py "your question"
```

## Implementation Details

### Dependencies

- `python-dotenv` — load environment variables from `.env.agent.secret`
- `requests` or `httpx` — make HTTP requests to LLM API
- Standard library: `sys`, `json`, `os`

### Key Functions

```python
def load_llm_config() -> dict:
    """Load LLM_API_KEY, LLM_API_BASE, LLM_MODEL from .env.agent.secret"""

def call_llm(question: str, config: dict) -> str:
    """Send question to LLM and return the answer"""

def format_response(answer: str, tool_calls: list) -> dict:
    """Build the JSON response structure"""

def main():
    """Parse args, call LLM, output JSON"""
```

### Error Handling

| Error | Handling |
|-------|----------|
| No question argument | Print usage to stderr, exit 1 |
| Missing API key | Print error to stderr, exit 1 |
| API timeout (>60s) | Print error to stderr, exit 1 |
| Invalid API response | Print error to stderr, exit 1 |

## Testing Strategy

### Regression Test

**File:** `tests/test_agent_task1.py`

**Test case:**
1. Run `agent.py` with a known question as subprocess
2. Parse stdout as JSON
3. Assert `answer` field exists and is non-empty string
4. Assert `tool_calls` field exists and is a list
5. Assert exit code is 0

**Example question:** "What is 2 + 2?"

## Acceptance Criteria Checklist

- [ ] `plans/task-1.md` exists with implementation plan ✅
- [ ] `agent.py` exists in project root
- [ ] `uv run agent.py "..."` outputs valid JSON
- [ ] JSON has `answer` and `tool_calls` fields
- [ ] API key stored in `.env.agent.secret` (not hardcoded)
- [ ] `AGENT.md` documents the solution
- [ ] 1 regression test exists and passes
- [ ] Git workflow: issue, branch, PR, approval, merge

## Timeline

| Step | Task | Estimated Time |
|------|------|----------------|
| 1 | Create this plan | 10 min |
| 2 | Implement `agent.py` | 20 min |
| 3 | Create `AGENT.md` | 10 min |
| 4 | Write regression test | 15 min |
| 5 | Git workflow (issue, branch, PR) | 10 min |
| **Total** | | **~65 min** |
