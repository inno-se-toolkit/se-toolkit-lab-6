"""Regression tests for agent.py."""

import json
import subprocess


def test_agent_returns_valid_json():
    """Test that agent.py outputs valid JSON with required fields."""
    result = subprocess.run(
        ["uv", "run", "agent.py", "What is 2+2?"],
        capture_output=True,
        text=True,
    )
    
    # Check exit code
    assert result.returncode == 0, f"Agent failed: {result.stderr}"
    
    # Parse stdout as JSON
    output = json.loads(result.stdout)
    
    # Check required fields
    assert "answer" in output, "Missing 'answer' field in output"
    assert "tool_calls" in output, "Missing 'tool_calls' field in output"
    
    # Check field types
    assert isinstance(output["answer"], str), "'answer' should be a string"
    assert isinstance(output["tool_calls"], list), "'tool_calls' should be a list"
    
    # Check that answer is non-empty
    assert len(output["answer"]) > 0, "'answer' should not be empty"
    
    # For Task 1, tool_calls should be empty
    assert output["tool_calls"] == [], "'tool_calls' should be empty for Task 1"


if __name__ == "__main__":
    test_agent_returns_valid_json()
    print("All tests passed!")
