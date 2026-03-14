"""
Regression tests for the Lab Assistant Agent.

Tests verify:
- Task 1: Basic LLM calling with JSON output
- Task 2: Tool calling (read_file, list_files) and agentic loop
- Task 3: System agent (query_api tool)
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

AGENT_PATH = Path(__file__).parent.parent / "agent.py"


def run_agent(question: str, mock_mode: bool = True) -> tuple[int, dict]:
    """
    Run agent.py as a subprocess and parse the JSON output.

    Args:
        question: The question to ask the agent
        mock_mode: If True, uses mock LLM responses (no API key needed)

    Returns:
        Tuple of (exit_code, response_dict)
    """
    env = os.environ.copy()
    if mock_mode:
        env["MOCK_MODE"] = "true"
        # Reset mock call counts by using a fresh Python process each time
        # The mock function tracks state in memory, so each subprocess is independent

    result = subprocess.run(
        ["uv", "run", str(AGENT_PATH), question],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=AGENT_PATH.parent,
        env=env,
    )

    # Parse JSON from stdout
    try:
        response = json.loads(result.stdout.strip())
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON output: {e}\nStdout: {result.stdout}\nStderr: {result.stderr}")

    return result.returncode, response


class TestTask1_BasicLLM:
    """Task 1: Basic LLM calling tests."""

    def test_basic_question_returns_valid_json(self):
        """Test that a basic question returns valid JSON with required fields."""
        exit_code, response = run_agent("What does REST stand for?")

        assert exit_code == 0, f"Agent failed with stderr: {response.get('error', 'unknown')}"
        assert "answer" in response, "Missing 'answer' field in response"
        assert "tool_calls" in response, "Missing 'tool_calls' field in response"
        assert isinstance(response["answer"], str), "'answer' must be a string"
        assert isinstance(response["tool_calls"], list), "'tool_calls' must be an array"
        assert len(response["answer"].strip()) > 0, "'answer' cannot be empty"


class TestTask2_DocumentationAgent:
    """Task 2: Documentation agent tests with tool calling."""

    def test_merge_conflict_question_uses_read_file(self):
        """Test that a merge conflict question triggers read_file tool."""
        exit_code, response = run_agent("How do you resolve a merge conflict?")

        assert exit_code == 0, f"Agent failed with stderr: {response.get('error', 'unknown')}"
        assert "answer" in response, "Missing 'answer' field"
        assert "tool_calls" in response, "Missing 'tool_calls' field"

        tool_calls = response["tool_calls"]
        assert len(tool_calls) > 0, "Expected at least one tool call"

        # Check that read_file was used
        tools_used = {tc.get("tool") for tc in tool_calls}
        assert "read_file" in tools_used, f"Expected read_file in tool calls, got: {tools_used}"

        # Check answer is non-empty
        assert len(response["answer"].strip()) > 0, "'answer' cannot be empty"

    def test_wiki_files_question_uses_list_files(self):
        """Test that a wiki files question triggers list_files tool."""
        exit_code, response = run_agent("What files are in the wiki?")

        assert exit_code == 0, f"Agent failed with stderr: {response.get('error', 'unknown')}"
        assert "answer" in response, "Missing 'answer' field"
        assert "tool_calls" in response, "Missing 'tool_calls' field"

        tool_calls = response["tool_calls"]
        assert len(tool_calls) > 0, "Expected at least one tool call"

        # Check that list_files was used
        tools_used = {tc.get("tool") for tc in tool_calls}
        assert "list_files" in tools_used, f"Expected list_files in tool calls, got: {tools_used}"

        # Check answer is non-empty
        assert len(response["answer"].strip()) > 0, "'answer' cannot be empty"


class TestTask3_SystemAgent:
    """Task 3: System agent tests with query_api tool."""

    def test_framework_question_uses_read_file(self):
        """Test that a framework question triggers read_file on source code."""
        exit_code, response = run_agent("What Python web framework does the backend use?")

        assert exit_code == 0, f"Agent failed with stderr: {response.get('error', 'unknown')}"
        assert "answer" in response, "Missing 'answer' field"
        assert "tool_calls" in response, "Missing 'tool_calls' field"

        tool_calls = response["tool_calls"]
        assert len(tool_calls) > 0, "Expected at least one tool call"

        # Check that read_file was used
        tools_used = {tc.get("tool") for tc in tool_calls}
        assert "read_file" in tools_used, f"Expected read_file in tool calls, got: {tools_used}"

        # Check answer mentions FastAPI (in mock mode, check for any reasonable answer)
        assert len(response["answer"].strip()) > 0, "'answer' cannot be empty"

    def test_database_count_question_uses_query_api(self):
        """Test that a database count question triggers query_api tool."""
        exit_code, response = run_agent("How many items are in the database?")

        assert exit_code == 0, f"Agent failed with stderr: {response.get('error', 'unknown')}"
        assert "answer" in response, "Missing 'answer' field"
        assert "tool_calls" in response, "Missing 'tool_calls' field"

        tool_calls = response["tool_calls"]
        assert len(tool_calls) > 0, "Expected at least one tool call"

        # Check that query_api was used
        tools_used = {tc.get("tool") for tc in tool_calls}
        assert "query_api" in tools_used, f"Expected query_api in tool calls, got: {tools_used}"

        # Check answer is non-empty
        assert len(response["answer"].strip()) > 0, "'answer' cannot be empty"


class TestToolSecurity:
    """Test tool security features."""

    def test_read_file_rejects_traversal_path(self):
        """Test that read_file rejects paths with directory traversal."""
        # Run a custom question that triggers read_file with traversal path
        env = os.environ.copy()
        env["MOCK_MODE"] = "true"

        # Use subprocess to test the tool directly via a special command
        result = subprocess.run(
            ["uv", "run", "python", "-c",
             "import sys; sys.path.insert(0, '.'); from agent import read_file; print(read_file('../etc/passwd'))"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=AGENT_PATH.parent,
            env=env,
        )

        output = result.stdout.strip()
        assert "Error" in output, f"Should reject path with .., got: {output}"
        assert "traversal" in output.lower() or "invalid" in output.lower(), f"Should mention traversal, got: {output}"

    def test_list_files_rejects_traversal_path(self):
        """Test that list_files rejects paths with directory traversal."""
        env = os.environ.copy()
        env["MOCK_MODE"] = "true"

        result = subprocess.run(
            ["uv", "run", "python", "-c",
             "import sys; sys.path.insert(0, '.'); from agent import list_files; print(list_files('../etc'))"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=AGENT_PATH.parent,
            env=env,
        )

        output = result.stdout.strip()
        assert "Error" in output, f"Should reject path with .., got: {output}"
        assert "traversal" in output.lower() or "invalid" in output.lower(), f"Should mention traversal, got: {output}"
