#!/usr/bin/env python3
"""Regression tests for agent.py."""

import json
import subprocess
import sys
from pathlib import Path


def test_agent_outputs_valid_json():
    """Test that agent.py outputs valid JSON with required fields.
    
    This test runs agent.py as a subprocess and verifies:
    - The output is valid JSON
    - The 'answer' field exists and is non-empty
    - The 'tool_calls' field exists and is an array
    """
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    agent_path = project_root / "agent.py"
    
    # Run agent.py with a simple test question
    # Using a question that should have a quick, deterministic answer
    result = subprocess.run(
        ["uv", "run", str(agent_path), "What is 2 + 2?"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    # Check that the process succeeded
    if result.returncode != 0:
        print(f"Agent failed with exit code {result.returncode}", file=sys.stderr)
        print(f"Stderr: {result.stderr}", file=sys.stderr)
        assert False, f"Agent exited with code {result.returncode}"
    
    # Parse the JSON output from stdout
    stdout = result.stdout.strip()
    if not stdout:
        assert False, "Agent produced no output"
    
    try:
        output = json.loads(stdout)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON output: {stdout}", file=sys.stderr)
        assert False, f"Output is not valid JSON: {e}"
    
    # Check that 'answer' field exists and is non-empty
    assert "answer" in output, "Missing 'answer' field in output"
    assert output["answer"], "'answer' field is empty"
    assert isinstance(output["answer"], str), "'answer' must be a string"
    
    # Check that 'tool_calls' field exists and is an array
    assert "tool_calls" in output, "Missing 'tool_calls' field in output"
    assert isinstance(output["tool_calls"], list), "'tool_calls' must be an array"
    
    print(f"Test passed! Answer: {output['answer']}", file=sys.stderr)


if __name__ == "__main__":
    test_agent_outputs_valid_json()
    print("All tests passed!", file=sys.stderr)
