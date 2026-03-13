# Task 3 Plan – The System Agent

## Goal

Extend the agent from Task 2 by adding a new tool that allows it to query the backend API.  
The agent should be able to answer system-level questions and data-dependent queries.

## Tool Schema

A new tool `query_api` will be added to the existing tool set.

Parameters:

- method – HTTP method (GET, POST, etc.)
- path – API endpoint path (e.g. /items/)
- body – optional JSON body

The tool returns a JSON string containing:

- status_code
- body

## Authentication

The tool will authenticate using the environment variable:

LMS_API_KEY

The base URL for the backend will be read from:

AGENT_API_BASE_URL (default: <http://localhost:42002>)

## Agent Behavior

The system prompt will guide the LLM:

- use wiki tools for documentation questions
- use read_file for source code questions
- use query_api for runtime system data

## Iteration Strategy

I will test the agent locally using run_eval.py and adjust the system prompt and tool descriptions if the agent fails to choose the correct tool.

The goal is to ensure that the agent correctly answers system questions and uses the appropriate tools.
