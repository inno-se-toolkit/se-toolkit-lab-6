"""
Regression tests for Task 1: Call an LLM from Code.

Tests verify that agent.py:
- Runs successfully
- Outputs valid JSON
- Contains required fields: answer and tool_calls
"""

import json
import subprocess
import sys


def test_agent_outputs_valid_json():
    """Test that agent.py outputs valid JSON with required fields."""
    import os
    
    # Get project root directory (two levels up from tests/)
    project_root = os.path.dirname(os.path.dirname(__file__))
    agent_path = os.path.join(project_root, "agent.py")
    
    # Run agent with a simple question
    result = subprocess.run(
        [sys.executable, agent_path, "What is 2+2?"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=project_root,
    )

    # Check exit code
    assert result.returncode == 0, f"Agent failed with: {result.stderr}"

    # Parse stdout as JSON
    output = result.stdout.strip()
    assert output, "No output from agent"

    data = json.loads(output)

    # Verify required fields exist
    assert "answer" in data, "Missing 'answer' field in output"
    assert "tool_calls" in data, "Missing 'tool_calls' field in output"

    # Verify tool_calls is an array
    assert isinstance(data["tool_calls"], list), "'tool_calls' must be an array"

    # Verify answer is non-empty
    assert data["answer"], "Answer is empty"

    print(f"✓ Test passed. Answer: {data['answer'][:50]}...")
