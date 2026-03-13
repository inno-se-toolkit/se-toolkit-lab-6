"""Unit tests for agent.py CLI.

These tests verify that the agent outputs valid JSON with required fields.
Run with: uv run pytest backend/tests/unit/test_agent.py -v
"""

import json
import subprocess
import sys
from pathlib import Path


def test_agent_outputs_valid_json():
    """Test that agent.py outputs valid JSON with answer and tool_calls fields."""
    # Get the project root directory (parent of backend/tests/unit)
    project_root = Path(__file__).parent.parent.parent.parent
    
    # Run agent.py with a simple question
    result = subprocess.run(
        ["uv", "run", "agent.py", "What is 2+2?"],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    # Check exit code
    assert result.returncode == 0, f"Agent failed with: {result.stderr}"
    
    # Parse stdout as JSON
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Agent output is not valid JSON: {result.stdout}") from e
    
    # Check required fields exist
    assert "answer" in output, "Missing 'answer' field in output"
    assert "tool_calls" in output, "Missing 'tool_calls' field in output"
    
    # Check field types
    assert isinstance(output["answer"], str), "'answer' should be a string"
    assert isinstance(output["tool_calls"], list), "'tool_calls' should be an array"
    
    # Check answer is not empty
    assert len(output["answer"].strip()) > 0, "'answer' should not be empty"
