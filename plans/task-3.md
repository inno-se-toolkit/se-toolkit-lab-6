# Task 3 Plan — System Agent

## Tool

query_api

Allows the agent to query the backend API.

Parameters:
- method (string)
- path (string)
- body (optional JSON string)

Authentication:
Use LMS_API_KEY from environment variables.

Base URL:
AGENT_API_BASE_URL (default http://localhost:42002)

## Agent strategy

The agent decides which tool to use:

- list_files → discover wiki files
- read_file → read documentation or source code
- query_api → get live system data

## Benchmark strategy

Run run_eval.py and iteratively fix failing cases.

Typical workflow:
1. Check which tool should be used.
2. Improve system prompt.
3. Fix tool implementation.

Initial score: TBD