"""Regression tests for agent.py (Task 1)."""

import json
import os
import subprocess
import sys


def test_agent_returns_valid_json():
    """Test that agent.py outputs valid JSON with required fields.
    
    This test runs the agent as a subprocess and verifies:
    - Exit code is 0
    - Output is valid JSON
    - 'answer' field exists and is non-empty string
    - 'tool_calls' field exists and is an array
    """
    # Ensure environment variables are set
    required_vars = ["LLM_API_KEY", "LLM_API_BASE", "LLM_MODEL"]
    missing = [var for var in required_vars if not os.environ.get(var)]
    
    if missing:
        print(
            f"Skipping test: Missing environment variables: {', '.join(missing)}",
            file=sys.stderr,
        )
        print(
            "Set LLM_API_KEY, LLM_API_BASE, LLM_MODEL to run this test.",
            file=sys.stderr,
        )
        return
    
    # Run agent with a simple question
    result = subprocess.run(
        [sys.executable, "-m", "uv", "run", "agent.py", "What is 2+2?"],
        capture_output=True,
        text=True,
        timeout=120,  # Give extra time for LLM response
    )
    
    # Check exit code
    assert result.returncode == 0, f"Agent failed: {result.stderr}"
    
    # Parse JSON output
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON output: {e}\nStdout: {result.stdout}")
    
    # Validate 'answer' field
    assert "answer" in output, "Missing 'answer' field in output"
    assert isinstance(output["answer"], str), "'answer' must be a string"
    assert len(output["answer"]) > 0, "'answer' must be non-empty"
    
    # Validate 'tool_calls' field
    assert "tool_calls" in output, "Missing 'tool_calls' field in output"
    assert isinstance(output["tool_calls"], list), "'tool_calls' must be an array"
