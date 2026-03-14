import subprocess
import json

def test_list_files_tool():
    result = subprocess.run(
        ["uv", "run", "agent.py", "What files are in the wiki?"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "tool_calls" in output
    assert any(t["tool"] == "list_files" for t in output["tool_calls"])

def test_read_file_tool():
    result = subprocess.run(
        ["uv", "run", "agent.py", "How do you resolve a merge conflict?"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "tool_calls" in output
    assert any(t["tool"] == "read_file" for t in output["tool_calls"])
    assert output["source"].startswith("wiki/")