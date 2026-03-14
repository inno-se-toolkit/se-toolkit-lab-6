# AGENT.md

## Overview
This agent is a simple CLI program that sends a user question to an LLM and prints a JSON response.

## LLM provider
Qwen Code API running on a VM.

## Model
qwen3-coder-plus

## Input
The first command-line argument is treated as the user question.

Example:
`bash
uv run agent.py "What does REST stand for?"