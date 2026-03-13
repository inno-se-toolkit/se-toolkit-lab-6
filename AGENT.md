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