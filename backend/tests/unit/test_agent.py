import json
import subprocess
import sys
from pathlib import Path


def test_agent_outputs_valid_json_with_required_fields() -> None:
    project_root = Path(__file__).parent.parent.parent.parent
    agent_path = project_root / "agent.py"

    result = subprocess.run(
        [sys.executable, str(agent_path), "What is 2+2?"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, f"agent.py failed with: {result.stderr}"

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"agent.py output is not valid JSON: {result.stdout}") from e

    assert "answer" in output, "Missing 'answer' field in output"
    assert "tool_calls" in output, "Missing 'tool_calls' field in output"
    assert isinstance(output["tool_calls"], list), "'tool_calls' must be an array"
    assert output["answer"], "'answer' field should not be empty"
