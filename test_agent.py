"""
Regression tests for agent.py.

These tests verify that the agent:
1. Outputs valid JSON
2. Contains required 'answer' and 'tool_calls' fields
3. Runs successfully with a test question
"""

import json
import os
import subprocess
import sys

import pytest


def get_agent_env() -> dict[str, str]:
    """
    Get the environment variables for running the agent.

    Loads from .env.agent.secret if it exists, otherwise uses
    environment variables already set.
    """
    env = os.environ.copy()

    # Try to load from .env.agent.secret
    env_file = os.path.join(os.path.dirname(__file__), "..", ".env.agent.secret")
    env_file = os.path.normpath(env_file)

    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # Remove quotes if present
                    value = value.strip("\"'")
                    env[key] = value

    # Set defaults for Google AI Studio if not specified
    if "LLM_API_BASE" not in env:
        env["LLM_API_BASE"] = "https://generativelanguage.googleapis.com/v1beta"
    if "LLM_MODEL" not in env:
        env["LLM_MODEL"] = "gemini-2.5-flash"

    return env


@pytest.mark.skipif(
    not os.environ.get("LLM_API_KEY"),
    reason="LLM_API_KEY not set, skipping integration test",
)
def test_agent_outputs_valid_json() -> None:
    """Test that agent.py outputs valid JSON with required fields."""
    # Run the agent with a simple question
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "uv",
            "run",
            "agent.py",
            "What is 2 + 2? Answer with just the number.",
        ],
        capture_output=True,
        text=True,
        env=get_agent_env(),
        timeout=60,
    )

    # Print stderr for debugging
    if result.stderr:
        print(f"Agent stderr: {result.stderr}", file=sys.stderr)

    # Check exit code
    assert result.returncode == 0, (
        f"Agent exited with code {result.returncode}: {result.stderr}"
    )

    # Parse stdout as JSON
    stdout = result.stdout.strip()
    assert stdout, "Agent produced no output"

    try:
        response = json.loads(stdout)
    except json.JSONDecodeError as e:
        pytest.fail(f"Agent output is not valid JSON: {e}\nOutput: {stdout}")

    # Verify required fields exist
    assert "answer" in response, "Missing 'answer' field in response"
    assert "tool_calls" in response, "Missing 'tool_calls' field in response"

    # Verify field types
    assert isinstance(response["answer"], str), "'answer' should be a string"
    assert isinstance(response["tool_calls"], list), "'tool_calls' should be an array"

    # Verify answer is non-empty
    assert response["answer"].strip(), "'answer' field is empty"


def test_agent_missing_env_var() -> None:
    """Test that agent exits with error when env vars are missing."""
    # Run with minimal environment (no LLM config)
    minimal_env = os.environ.copy()
    for var in ["LLM_API_KEY", "LLM_API_BASE", "LLM_MODEL"]:
        minimal_env.pop(var, None)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "uv",
            "run",
            "agent.py",
            "Test question",
        ],
        capture_output=True,
        text=True,
        env=minimal_env,
        timeout=30,
    )

    # Should exit with non-zero code
    assert result.returncode != 0, "Agent should exit with error when env vars missing"

    # Error should go to stderr
    assert "Error" in result.stderr or "missing" in result.stderr.lower(), (
        f"Expected error message in stderr, got: {result.stderr}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
