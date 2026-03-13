"""
Regression tests for Task 1: Call an LLM from Code.

Tests verify that agent.py:
- Outputs valid JSON with 'answer' and 'tool_calls' fields
- Exits with code 0 on success
"""

import json
import subprocess
import sys


def test_agent_outputs_valid_json():
    """Test that agent.py outputs valid JSON with required fields."""
    # Run agent.py with a simple question
    result = subprocess.run(
        [sys.executable, "agent.py", "What is 2 plus 2?"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    # Check exit code
    assert result.returncode == 0, f"Agent exited with code {result.returncode}: {result.stderr}"

    # Parse stdout as JSON
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON output: {e}\nStdout: {result.stdout}\nStderr: {result.stderr}")

    # Check required fields
    assert "answer" in output, f"Missing 'answer' field in output: {output}"
    assert isinstance(output["answer"], str), f"'answer' should be string, got {type(output['answer'])}"
    assert len(output["answer"]) > 0, "'answer' should not be empty"

    assert "tool_calls" in output, f"Missing 'tool_calls' field in output: {output}"
    assert isinstance(output["tool_calls"], list), f"'tool_calls' should be array, got {type(output['tool_calls'])}"

    print(f"✓ Test passed: answer='{output['answer'][:50]}...'")


if __name__ == "__main__":
    test_agent_outputs_valid_json()
    print("All tests passed!")
