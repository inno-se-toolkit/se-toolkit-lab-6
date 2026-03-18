import subprocess
import json
import pytest

def test_agent_output_contains_answer_and_tool_calls():
    # Run agent.py as a subprocess
    result = subprocess.run(
        ["python", "agent.py"],
        capture_output=True,
        text=True,
        check=True
    )

    # Parse stdout as JSON
    try:
        output_json = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail("agent.py did not output valid JSON")

    # Check that required keys are present
    assert "answer" in output_json, "'answer' key not found in output JSON"
    assert "tool_calls" in output_json, "'tool_calls' key not found in output JSON"