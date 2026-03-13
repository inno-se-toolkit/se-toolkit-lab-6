# Agent

## Overview

This project implements a CLI agent that connects to an LLM and answers questions.

The agent receives a question from the command line, sends it to an LLM using an OpenAI-compatible API, and prints a JSON response.

## Architecture

User question → agent.py → LLM API → JSON output

## Configuration

The agent reads configuration from `.env.agent.secret`:

- LLM_API_KEY
- LLM_API_BASE
- LLM_MODEL

## Running the agent

Example:

uv run agent.py "What does REST stand for?"

Output format:

{"answer": "...", "tool_calls": []}

## Tools

### list_files

Lists files in a directory.

### read_file

Reads file contents.

## Agentic loop

1. Send question + tools to LLM.
2. If tool_calls returned:
   execute tools and send results back.
3. Repeat until answer produced.

## System Agent (Task 3)

In Task 3 the agent was extended with a new capability: interacting with the running backend system. While the documentation agent from Task 2 could read wiki files and source code, it could not access live system data. To solve this limitation, a new tool called `query_api` was introduced.

The `query_api` tool allows the agent to send HTTP requests to the backend API. The tool accepts three parameters: `method`, `path`, and an optional `body`. The method represents the HTTP method such as GET or POST, the path specifies the endpoint (for example `/items/`), and the body can contain a JSON payload if required. The tool returns a JSON string that includes both the HTTP status code and the response body.

Authentication for backend requests is handled through the `LMS_API_KEY` environment variable. This ensures that sensitive credentials are not hardcoded in the source code. The base URL of the backend service is also configurable through the `AGENT_API_BASE_URL` environment variable, with a default value of `http://localhost:42002`.

The system prompt was updated to help the LLM choose the correct tool depending on the question. Documentation questions should use the wiki tools (`list_files` and `read_file`), source code questions should use `read_file`, and runtime system data questions should use `query_api`.

This design allows the agent to combine multiple information sources: documentation, source code, and live system data. As a result, the agent can answer both static system questions (for example, the framework used by the backend) and dynamic questions that require querying the running system.
