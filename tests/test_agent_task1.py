"""
Regression tests for Task 1: Call an LLM from Code

Tests that agent.py:
1. Runs successfully with a question argument
2. Outputs valid JSON to stdout
3. Has required 'answer' and 'tool_calls' fields
"""

import json
import subprocess
import sys
from pathlib import Path


def test_agent_outputs_valid_json():
    """
    Test that agent.py outputs valid JSON with required fields.

    This test:
    1. Runs agent.py with a simple question
    2. Parses stdout as JSON
    3. Verifies 'answer' and 'tool_calls' fields exist
    4. Verifies exit code is 0
    """
    # Path to agent.py in the project root
    agent_path = Path(__file__).parent.parent / "agent.py"

    # Run the agent with a simple question
    result = subprocess.run(
        ["uv", "run", str(agent_path), "What is 2 + 2?"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    # Check exit code
    assert result.returncode == 0, f"Agent exited with code {result.returncode}: {result.stderr}"

    # Parse stdout as JSON
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Agent output is not valid JSON: {e}\nStdout: {result.stdout}")

    # Check required fields exist
    assert "answer" in response, "Response missing 'answer' field"
    assert "tool_calls" in response, "Response missing 'tool_calls' field"

    # Check field types
    assert isinstance(response["answer"], str), "'answer' must be a string"
    assert isinstance(response["tool_calls"], list), "'tool_calls' must be a list"

    # Check answer is non-empty
    assert len(response["answer"]) > 0, "'answer' must not be empty"

    # For Task 1, tool_calls should be empty
    assert response["tool_calls"] == [], "tool_calls should be empty for Task 1"

    print(f"✓ Agent response: {response}", file=sys.stderr)


def test_agent_missing_argument():
    """
    Test that agent.py exits with error when no question is provided.
    """
    agent_path = Path(__file__).parent.parent / "agent.py"

    result = subprocess.run(
        ["uv", "run", str(agent_path)],
        capture_output=True,
        text=True,
        timeout=10,
    )

    # Should exit with non-zero code
    assert result.returncode != 0, "Agent should exit with error when no argument provided"

    # Error should be in stderr
    assert "Error" in result.stderr or "Usage" in result.stderr, \
        "Agent should print error message to stderr"
