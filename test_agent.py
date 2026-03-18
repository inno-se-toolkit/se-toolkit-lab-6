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

def test_read_file_tool():
    """Test that the agent uses read_file_content tool to answer questions about git merge conflicts."""

    result = subprocess.run(
        ["uv", "run", "agent.py", "How do you resolve a merge conflict?"],
        capture_output=True,
        text=True,
        timeout=120
    )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        assert False, "Output is not valid JSON"

    assert "answer" in data, "Missing 'answer' field"
    assert "tool_calls" in data, "Missing 'tool_calls' field"
    assert "source" in data, "Missing 'source' field"
    assert isinstance(data["tool_calls"], list), "'tool_calls' must be a list"
    assert len(data["tool_calls"]) > 0, "Expected at least one tool call"

    # Check that read_file_content was used
    tool_names = [call["tool"] for call in data["tool_calls"]]
    assert "read_file_content" in tool_names, "Expected read_file_content tool to be called"

    # Check that git-workflow.md was accessed
    file_paths = [call["args"].get("file_path", "") for call in data["tool_calls"] if call["tool"] == "read_file_content"]
    assert any("git-workflow.md" in path for path in file_paths), "Expected git-workflow.md to be read"

    # Check source field contains git-workflow.md
    assert "git-workflow.md" in data["source"], "Expected source to reference git-workflow.md"

def test_list_files_tool():
    """Test that the agent uses list_files tool to discover wiki files."""

    result = subprocess.run(
        ["uv", "run", "agent.py", "What files are in the wiki directory?"],
        capture_output=True,
        text=True,
        timeout=120
    )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        assert False, "Output is not valid JSON"

    assert "answer" in data, "Missing 'answer' field"
    assert "tool_calls" in data, "Missing 'tool_calls' field"
    assert isinstance(data["tool_calls"], list), "'tool_calls' must be a list"
    assert len(data["tool_calls"]) > 0, "Expected at least one tool call"

    # Check that list_files was used
    tool_names = [call["tool"] for call in data["tool_calls"]]
    assert "list_files" in tool_names, "Expected list_files tool to be called"

    # Check that wiki directory was listed
    dir_paths = [call["args"].get("directory_path", "") for call in data["tool_calls"] if call["tool"] == "list_files"]
    assert any("wiki" in path for path in dir_paths), "Expected wiki directory to be listed"

if __name__ == "__main__":
    test_json_format()
    print("Test 1: JSON format - PASSED")

    test_read_file_tool()
    print("Test 2: read_file_content tool - PASSED")

    test_list_files_tool()
    print("Test 3: list_files tool - PASSED")

    print("\nAll regression tests passed!")