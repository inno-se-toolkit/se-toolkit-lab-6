import subprocess
import json
import pytest

def run_agent(question):
    """Helper to run agent.py with a question and return parsed output."""
    result = subprocess.run(
        ["python3", "agent.py", question],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Agent failed with stderr: {result.stderr}"
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"stdout is not valid JSON: {result.stdout}")
    return output, result.stderr

def test_merge_conflict():
    """Test question about resolving merge conflict should use read_file."""
    output, stderr = run_agent("How do you resolve a merge conflict?")
    
    # Check required fields
    assert "answer" in output
    assert "source" in output
    assert "tool_calls" in output
    
    # Verify that read_file was called
    tool_names = [call["tool"] for call in output["tool_calls"]]
    assert "read_file" in tool_names, f"Expected read_file in tool_calls, got {tool_names}"
    
    # Source should contain wiki/git-workflow.md (or similar)
    assert "wiki/" in output["source"], f"Expected wiki source, got {output['source']}"

def test_list_files_in_wiki():
    """Test question about wiki contents should use list_files."""
    output, stderr = run_agent("What files are in the wiki?")
    
    assert "answer" in output
    assert "source" in output
    assert "tool_calls" in output
    
    tool_names = [call["tool"] for call in output["tool_calls"]]
    assert "list_files" in tool_names, f"Expected list_files in tool_calls, got {tool_names}"
