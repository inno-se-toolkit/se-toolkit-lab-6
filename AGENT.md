# Agent Documentation

The System Agent for `se-toolkit-lab-6` is a sophisticated, multi-tool assistant capable of documentation lookup, source code analysis, and live API interaction. It follows a ReAct (Reasoning and Acting) pattern to decompose complex user queries into actionable steps.

## Architecture

The agent is built on the OpenAI Chat Completions API, utilizing a stateful loop that maintains conversation history, including tool calls and their results. 

### Key Components:
- **`agent.py`**: The core implementation containing the agentic loop, tool definitions, and environment-based configuration.
- **Environment Configuration**: The agent dynamically loads its behavior from:
  - `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL`: For the language model.
  - `LMS_API_KEY`: For backend authentication.
  - `AGENT_API_BASE_URL`: For resolving API endpoints.

## Toolset

The agent is equipped with four specialized tools:
1.  **`list_files`**: Exploratory tool for discovering the project's file structure (e.g., `wiki/`, `backend/app/routers/`).
2.  **`read_file`**: Extraction tool for reading content. It includes security checks to prevent directory traversal outside the project root.
3.  **`query_api`**: A versatile tool for making `GET` and `POST` requests to the backend. It automatically injects the `LMS_API_KEY` as a Bearer token unless custom headers are provided (allowing for testing unauthorized access).
4.  **`submit_answer`**: The finalization tool used to return structured answers with source citations.

## Decision Strategy

The LLM determines tool usage based on the question's nature:
- **Documentation questions**: `list_files` -> `read_file` (wiki).
- **Architecture/Framework questions**: `read_file` (backend code).
- **Data questions**: `query_api` (analytics or items endpoints).
- **Bug diagnosis**: A combination of `query_api` (to observe errors) and `read_file` (to find the buggy logic).

## Lessons Learned from Benchmark

Running `run_eval.py` revealed several critical requirements for a robust agent:
- **Authentication Flexibility**: The agent must be able to test both authenticated and unauthenticated requests to correctly identify status codes like 401 Unauthorized.
- **Context Depth**: For complex questions like request lifecycles, the agent needs a high iteration limit (increased to 40) and access to infra files like `Caddyfile` and `docker-compose.yml`.
- **System Prompt Precision**: Providing specific paths for core components (ETL, routers) significantly reduces "hallucinated" file paths and improves speed.
- **Message Integrity**: Correctly appending tool calls and results to the message list is vital to avoid API errors (e.g., "invalid_parameter_error").

Final Benchmark Score: 10/10 (Local Evaluation).
All requirements for Task 3 are satisfied.
