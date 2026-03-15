#!/usr/bin/env python3
"""
Regression tests for agent.py
"""

import subprocess
import json
import sys
import os

def test_agent_basic_question():
    """Test that agent.py returns valid JSON with answer and tool_calls."""
    # Run the agent with a simple question
    result = subprocess.run(
        [sys.executable, "agent.py", "What is 2+2?"],
        capture_output=True,
        text=True,
        env=os.environ.copy()
    )
    
    # Check exit code
    assert result.returncode == 0, f"Agent failed with exit code {result.returncode}"
    
    # Parse stdout as JSON
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        assert False, f"Output is not valid JSON: {result.stdout}"
    
    # Check required fields
    assert "answer" in output, "Missing 'answer' field in output"
    assert "tool_calls" in output, "Missing 'tool_calls' field in output"
    assert isinstance(output["tool_calls"], list), "'tool_calls' should be a list"
    
    # Check that answer is not empty
    assert output["answer"], "Answer should not be empty"
    
    print("✓ Basic test passed")

def test_agent_missing_question():
    """Test that agent fails gracefully when no question provided."""
    result = subprocess.run(
        [sys.executable, "agent.py"],
        capture_output=True,
        text=True
    )
    
    # Should exit with non-zero code
    assert result.returncode != 0, "Agent should fail with no arguments"

if __name__ == "__main__":
    test_agent_basic_question()
    test_agent_missing_question()
    print("All tests passed!")
