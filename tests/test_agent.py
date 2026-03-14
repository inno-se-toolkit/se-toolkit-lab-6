"""
Regression tests for agent.py CLI.

Tests verify that agent.py:
- Runs successfully with a question argument
- Outputs valid JSON to stdout
- JSON contains required fields: answer, tool_calls
"""

import json
import subprocess
from pathlib import Path


def test_agent_outputs_valid_json():
    """Test that agent.py outputs valid JSON with required fields."""
    # Path to agent.py in project root
    project_root = Path(__file__).parent.parent
    agent_path = project_root / "agent.py"

    # Run agent with a simple question
    result = subprocess.run(
        ["uv", "run", str(agent_path), "What is 2+2?"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(project_root),
    )

    # Check exit code
    assert result.returncode == 0, f"Agent failed: {result.stderr}"

    # Parse stdout as JSON
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Agent output is not valid JSON: {result.stdout}") from e

    # Check required fields
    assert "answer" in output, "Missing 'answer' field in output"
    assert "tool_calls" in output, "Missing 'tool_calls' field in output"

    # Check field types
    assert isinstance(output["answer"], str), "'answer' should be a string"
    assert isinstance(output["tool_calls"], list), "'tool_calls' should be an array"

    # Check answer is not empty
    assert len(output["answer"].strip()) > 0, "'answer' should not be empty"

    print(f"✓ Test passed: answer={output['answer'][:50]}...")
