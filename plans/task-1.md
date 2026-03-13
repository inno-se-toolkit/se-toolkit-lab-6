# Task 1: Call an LLM from Code - Implementation Plan

## LLM Provider Selection

**Provider:** Google AI Studio (Gemini)  
**Model:** `gemini-2.5-flash`

**Rationale:**

- Free tier available
- Fast response times
- Strong performance on reasoning tasks
- Reliable API with good uptime
- No credit card required

## Architecture

### Components

1. **CLI Entry Point (`agent.py`)**
   - Parse command-line argument (the question)
   - Load LLM configuration from environment variables
   - Call the LLM API
   - Format and output JSON response

2. **Environment Configuration (`.env.agent.secret`)**
   - `LLM_API_KEY` - API key for authentication
   - `LLM_API_BASE` - Base URL for the LLM API endpoint
   - `LLM_MODEL` - Model name to use

3. **Output Format**

   ```json
   {"answer": "<llm response>", "tool_calls": []}
   ```

### Data Flow

```
User question (CLI arg) 
    → agent.py reads question
    → Load env vars (LLM_API_KEY, LLM_API_BASE, LLM_MODEL)
    → Build HTTP request to LLM API
    → Parse LLM response
    → Format JSON output
    → Print to stdout
```

## Error Handling

- Missing environment variables → exit with error to stderr
- API request failure → exit with error to stderr
- Invalid JSON response → exit with error to stderr
- All errors go to stderr, only valid JSON to stdout

## Testing Strategy

Create one regression test that:

1. Runs `agent.py` as a subprocess with a test question
2. Parses the stdout as JSON
3. Verifies `answer` field exists and is non-empty
4. Verifies `tool_calls` field exists and is an array

## Files to Create

1. `plans/task-1.md` - This plan
2. `agent.py` - CLI entry point
3. `AGENT.md` - Architecture documentation
4. `test_agent.py` - Regression test
5. `.env.agent.secret` - LLM configuration (copy from `.env.agent.example`)

## Acceptance Criteria Checklist

- [ ] Plan written before code
- [ ] `agent.py` outputs valid JSON with `answer` and `tool_calls`
- [ ] LLM config read from environment variables (not hardcoded)
- [ ] `AGENT.md` documents the solution
- [ ] At least 1 regression test passes
- [ ] Git workflow: issue → branch → PR → approval → merge
