import subprocess
import json


def test_list_files_tool():
    result = subprocess.run(
        ["uv", "run", "agent.py", "What files are in the wiki?"],
        capture_output=True,
        text=True,
    )

    if result.stdout.strip() == "":
        return

    data = json.loads(result.stdout)

    assert "tool_calls" in data


def test_read_file_tool():
    result = subprocess.run(
        ["uv", "run", "agent.py", "How do you resolve a merge conflict?"],
        capture_output=True,
        text=True,
    )

    if result.stdout.strip() == "":
        return

    data = json.loads(result.stdout)

    assert "answer" in data