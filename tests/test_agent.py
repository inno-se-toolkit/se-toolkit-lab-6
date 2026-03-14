"""Regression tests for agent.py."""

import json
import subprocess
import sys


def _run_agent(question: str) -> dict:
    result = subprocess.run(
        [sys.executable, "agent.py", question],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"agent.py exited with code {result.returncode}: {result.stderr}"
    return json.loads(result.stdout)


# --- Task 1: basic output structure ---

def test_agent_returns_valid_json_with_required_fields():
    data = _run_agent("What is 2+2?")
    assert "answer" in data, "Missing 'answer' field in output"
    assert "tool_calls" in data, "Missing 'tool_calls' field in output"
    assert isinstance(data["answer"], str), "'answer' must be a string"
    assert len(data["answer"]) > 0, "'answer' must not be empty"
    assert isinstance(data["tool_calls"], list), "'tool_calls' must be a list"


# --- Task 2: documentation agent tools ---

def test_agent_reads_wiki_for_merge_conflict_question():
    data = _run_agent("How do you resolve a merge conflict?")
    assert "source" in data, "Missing 'source' field in output"
    assert "tool_calls" in data
    tool_names = [tc["tool"] for tc in data["tool_calls"]]
    assert "read_file" in tool_names, "Expected read_file to be called"
    assert "wiki/git-workflow.md" in data["source"], "Expected source to reference wiki/git-workflow.md"


def test_agent_lists_wiki_files():
    data = _run_agent("What files are in the wiki?")
    assert "tool_calls" in data
    tool_names = [tc["tool"] for tc in data["tool_calls"]]
    assert "list_files" in tool_names, "Expected list_files to be called"


# --- Task 3: system agent tools ---

def test_agent_reads_source_for_framework_question():
    data = _run_agent("What Python web framework does this project's backend use?")
    assert "tool_calls" in data
    tool_names = [tc["tool"] for tc in data["tool_calls"]]
    assert "read_file" in tool_names, "Expected read_file to be called for source code question"
    assert "fastapi" in data["answer"].lower(), "Expected answer to mention FastAPI"


def test_agent_queries_api_for_item_count():
    data = _run_agent("How many items are currently stored in the database?")
    assert "tool_calls" in data
    tool_names = [tc["tool"] for tc in data["tool_calls"]]
    assert "query_api" in tool_names, "Expected query_api to be called for data question"
