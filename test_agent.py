import subprocess
import json
import sys

def test_agent():
    result = subprocess.run(
        [sys.executable, "agent.py", "What is 2+2?"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Agent failed: {result.stderr}"

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        assert False, "Output is not valid JSON"

    assert "answer" in output, "Missing 'answer' field"
    assert "tool_calls" in output, "Missing 'tool_calls' field"
    assert isinstance(output["tool_calls"], list), "'tool_calls' must be a list"
    print("✅ Test passed!")

if __name__ == "__main__":
    test_agent()
