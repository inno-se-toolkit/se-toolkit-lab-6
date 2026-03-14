import subprocess
import json
import sys

def run_agent(question):
    result = subprocess.run(
        ["uv", "run", "agent.py", question],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0
    return json.loads(result.stdout.strip())

def test_merge_conflict():
    output = run_agent("How do you resolve a merge conflict?")
    assert "answer" in output
    assert "tool_calls" in output
    tool_names = [tc["tool"] for tc in output["tool_calls"]]
    assert "read_file" in tool_names
    assert "source" in output
    assert "wiki/" in output["source"]

def test_list_wiki_files():
    output = run_agent("What files are in the wiki?")
    assert "answer" in output
    assert "tool_calls" in output
    tool_names = [tc["tool"] for tc in output["tool_calls"]]
    assert "list_files" in tool_names
