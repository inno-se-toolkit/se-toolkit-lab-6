"""
Regression tests for agent.py

Tests verify that the agent:
1. Outputs valid JSON
2. Has required fields (answer, tool_calls)
3. Responds within timeout
"""

import json
import subprocess
import sys
from pathlib import Path


def test_agent_output():
    """Test that agent.py outputs valid JSON with required fields."""
    agent_path = Path(__file__).parent.parent / "agent.py"
    
    result = subprocess.run(
        [sys.executable, str(agent_path), "What is 2+2?"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    # Check exit code
    assert result.returncode == 0, f"Agent exited with code {result.returncode}: {result.stderr}"
    
    # Parse JSON output
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON output: {e}\nStdout: {result.stdout}\nStderr: {result.stderr}")
    
    # Check required fields
    assert "answer" in output, "Missing 'answer' field in output"
    assert "tool_calls" in output, "Missing 'tool_calls' field in output"
    
    # Check field types
    assert isinstance(output["answer"], str), "'answer' should be a string"
    assert isinstance(output["tool_calls"], list), "'tool_calls' should be a list"
    
    # Check that answer is not empty
    assert len(output["answer"]) > 0, "'answer' should not be empty"


def test_agent_missing_argument():
    """Test that agent.py shows usage when no argument provided."""
    agent_path = Path(__file__).parent.parent / "agent.py"
    
    result = subprocess.run(
        [sys.executable, str(agent_path)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    # Should exit with non-zero code
    assert result.returncode != 0, "Agent should exit with non-zero code when no argument"
    
    # Should show usage message in stderr
    assert "Usage" in result.stderr or "usage" in result.stderr, "Should show usage message"
