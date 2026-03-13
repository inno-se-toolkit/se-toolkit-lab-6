import json
import subprocess
import pytest

def run_agent(question):
    result = subprocess.run(
        ["uv", "run", "agent.py", question],
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(result.stdout)

def test_agent_resolve_merge_conflict():
    """
    Test that the agent can answer about merge conflicts using the wiki.
    """
    question = "How do you resolve a merge conflict?"
    output = run_agent(question)
    
    # Check for expected fields
    assert "answer" in output
    assert "source" in output
    assert "tool_calls" in output
    
    # Check that tools were actually used
    tool_names = [tc["tool"] for tc in output["tool_calls"]]
    assert "read_file" in tool_names
    
    # Check source
    assert any(f in output["source"] for f in ["wiki/git-workflow.md", "wiki/git.md", "wiki/git-vscode.md"])

def test_agent_list_wiki_files():
    """
    Test that the agent can list files in the wiki.
    """
    question = "What files are in the wiki?"
    output = run_agent(question)
    
    # Check for expected fields
    assert "answer" in output
    assert "tool_calls" in output
    
    # Check that list_files was used
    tool_names = [tc["tool"] for tc in output["tool_calls"]]
    assert "list_files" in tool_names
    
    # Check that wiki directory was listed
    wiki_listed = any(tc["args"].get("path") == "wiki" for tc in output["tool_calls"] if tc["tool"] == "list_files")
    assert wiki_listed
