import subprocess
import json
import sys

def test_agent_output():
    result = subprocess.run(
        ["uv", "run", "agent.py", "What does REST stand for?"],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0
    output = json.loads(result.stdout.strip())
    assert "answer" in output
    assert "tool_calls" in output
    assert isinstance(output["tool_calls"], list)
