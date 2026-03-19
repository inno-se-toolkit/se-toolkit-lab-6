"""Regression tests for agent.py."""

import json
import subprocess
import sys
from pathlib import Path


def test_agent_returns_valid_json():
    """Test that agent.py returns valid JSON with answer and tool_calls."""
    # Get project root directory
    project_root = Path(__file__).parent.parent

    # Run agent.py with a simple question
    result = subprocess.run(
        [sys.executable, str(project_root / "agent.py"), "What is 2+2?"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(project_root),
    )

    # Check exit code
    assert result.returncode == 0, f"Agent failed: {result.stderr}"

    # Parse stdout as JSON
    output = result.stdout.strip()
    data = json.loads(output)

    # Check required fields
    assert "answer" in data, "Missing 'answer' field in output"
    assert "tool_calls" in data, "Missing 'tool_calls' field in output"
    assert isinstance(data["tool_calls"], list), "'tool_calls' must be a list"

    # Check answer is not empty
    assert len(data["answer"]) > 0, "Answer is empty"

    print(f"✓ Test passed: {data['answer'][:50]}...")


if __name__ == "__main__":
    test_agent_returns_valid_json()
    print("All tests passed!")
