"""
Regression test for Task 1: Call an LLM from Code
Tests that agent.py outputs valid JSON with required fields.
"""

import subprocess
import json
import sys
import os
import pytest


@pytest.fixture
def agent_script():
    """Get the path to the agent.py script."""
    return os.path.join(os.path.dirname(__file__), "..", "agent.py")


@pytest.fixture
def env_file_exists():
    """Check if .env.agent.secret exists."""
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env.agent.secret")
    if not os.path.exists(env_path):
        pytest.skip(".env.agent.secret not found - skipping integration test")
    return True


def test_task1_agent_output_structure(agent_script, env_file_exists):
    """
    Test that agent.py outputs valid JSON with required fields:
    - answer (string)
    - tool_calls (array, empty for Task 1)
    """
    # Run the agent with a simple question
    result = subprocess.run(
        [sys.executable, agent_script, "What is 2+2?"],
        capture_output=True,
        text=True,
        timeout=60
    )

    # Check exit code
    assert result.returncode == 0, f"Agent failed with error: {result.stderr}"

    # Parse stdout as JSON
    stdout = result.stdout.strip()
    try:
        response = json.loads(stdout)
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON output: {e}\nStdout: {stdout}\nStderr: {result.stderr}")

    # Validate required fields
    assert "answer" in response, "Missing 'answer' field in output"
    assert "tool_calls" in response, "Missing 'tool_calls' field in output"
    assert isinstance(response["answer"], str), "'answer' should be a string"
    assert isinstance(response["tool_calls"], list), "'tool_calls' should be an array"
    assert len(response["tool_calls"]) == 0, "'tool_calls' should be empty for Task 1"

    # Verify answer is not empty
    assert len(response["answer"]) > 0, "'answer' should not be empty"


def test_task1_debug_output_to_stderr(agent_script, env_file_exists):
    """
    Test that debug/progress output goes to stderr, not stdout.
    stdout should contain ONLY valid JSON.
    """
    result = subprocess.run(
        [sys.executable, agent_script, "Test question"],
        capture_output=True,
        text=True,
        timeout=60
    )

    # stdout should be parseable as JSON without any extra text
    stdout = result.stdout.strip()
    if stdout:
        try:
            json.loads(stdout)
        except json.JSONDecodeError:
            pytest.fail(f"stdout contains non-JSON output: {stdout}")

    # stderr may have debug messages, but we don't validate them


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
