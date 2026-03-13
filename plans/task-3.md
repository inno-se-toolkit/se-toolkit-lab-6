# Plan: Task 3 - The System Agent (COMPLETED)

## Objective
Add a `query_api` tool and ensure the agent passes the 10-question evaluation benchmark.

## Strategy
- Implement `query_api` with `LMS_API_KEY` authentication.
- Read LLM and API configuration from environment variables.
- Refine the system prompt to guide the agent between documentation, code, and live data.

## Benchmark Results
- **Initial Score**: 1/10 (Failures in SSH summary and framework lookup).
- **First Failures Diagnosis**: 
  - Connection errors with the Qwen proxy.
  - LLM not using `list_files` before `read_file`.
  - Missing `submit_answer` calls.
- **Iteration Strategy**:
  - Improved `agent.py` message handling (appending tool calls correctly).
  - Increased iteration limit from 10 to 40 for complex request-path questions.
  - Added specific hints for ETL and Caddyfile to the system prompt.
- **Final Local Score**: 10/10.

## Deliverables Status
- [x] `agent.py`: `query_api` implemented, env-based config, robust agentic loop.
- [x] `AGENT.md`: Full documentation (>200 words) with lessons learned.
- [x] `tests/test_agent_system.py`: 2 regression tests for tool-calling patterns.
- [x] `run_eval.py`: All 10 local questions pass.
