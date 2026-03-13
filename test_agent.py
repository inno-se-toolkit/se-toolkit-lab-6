import subprocess
import json

def test_json_format():
   
    result = subprocess.run(
        ["uv", "run", "agent.py", "What is REST?"],
        capture_output=True,
        text=True
    )
    
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        assert False, "Output is not valid JSON"

    assert "answer" in data, "Missing 'answer' field"
    assert "tool_calls" in data, "Missing 'tool_calls' field"
    assert isinstance(data["tool_calls"], list), "'tool_calls' must be a list"

if __name__ == "__main__":
    test_json_format()
    print("Regression test passed!")