# Task 3 — The System Agent

## `query_api` tool schema

Add a third tool `query_api` with parameters:
- `method` (string) — HTTP method (GET, POST, etc.)
- `path` (string) — API path (e.g., `/items/`)
- `body` (string, optional) — JSON request body

Returns JSON with `status_code` and `body`.

## Authentication

`query_api` reads `LMS_API_KEY` from environment variables (sourced from `.env.docker.secret`) and sends it as `X-API-Key` header. The base URL comes from `AGENT_API_BASE_URL` (default: `http://localhost:42002`).

## System prompt updates

Expand the system prompt to guide the LLM on when to use each tool:
- Wiki/documentation questions → `list_files` + `read_file` on `wiki/`
- Source code questions → `list_files` + `read_file` on `backend/`
- Data or API questions → `query_api`
- Bug diagnosis → `query_api` first to see the error, then `read_file` to find the buggy code

## Iteration strategy

Run `run_eval.py` after implementation, diagnose failures one by one, and tune the system prompt and tool descriptions until all 10 pass.
