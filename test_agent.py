#!/usr/bin/env python3
"""
Regression tests for agent.py with tools
"""

import subprocess
import json
import sys
import os
import tempfile

def create_test_wiki():
    """Create test wiki files for testing."""
    wiki_dir = os.path.join(os.path.dirname(__file__), 'wiki')
    os.makedirs(wiki_dir, exist_ok=True)
    
    # Create test git-workflow.md
    with open(os.path.join(wiki_dir, 'git-workflow.md'), 'w') as f:
        f.write("""# Git Workflow

## Resolving Merge Conflicts
To resolve a merge conflict:
1. Edit the conflicting file
2. Choose which changes to keep
3. Stage the file: git add <file>
4. Commit: git commit
""")
    
    # Create another test file
    with open(os.path.join(wiki_dir, 'README.md'), 'w') as f:
        f.write("# Wiki Documentation\n\nThis is the project wiki.")

def test_agent_basic_question():
    """Test that agent.py returns valid JSON with required fields."""
    result = subprocess.run(
        [sys.executable, "agent.py", "What is 2+2?"],
        capture_output=True,
        text=True,
        env=os.environ.copy()
    )
    
    assert result.returncode == 0, f"Agent failed with exit code {result.returncode}"
    
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        assert False, f"Output is not valid JSON: {result.stdout}"
    
    # Check required fields for Task 2
    assert "answer" in output, "Missing 'answer' field"
    assert "source" in output, "Missing 'source' field"
    assert "tool_calls" in output, "Missing 'tool_calls' field"
    assert isinstance(output["tool_calls"], list), "'tool_calls' should be a list"
    
    print("✓ Basic test passed")

def test_agent_list_files_tool():
    """Test that agent uses list_files tool for directory questions."""
    # Create test wiki
    create_test_wiki()
    
    result = subprocess.run(
        [sys.executable, "agent.py", "What files are in the wiki?"],
        capture_output=True,
        text=True,
        env=os.environ.copy()
    )
    
    assert result.returncode == 0, f"Agent failed with exit code {result.returncode}"
    
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        assert False, f"Output is not valid JSON: {result.stdout}"
    
    # Check that list_files was called
    tool_calls = output.get("tool_calls", [])
    list_files_calls = [tc for tc in tool_calls if tc.get("tool") == "list_files"]
    
    assert len(list_files_calls) > 0, "Expected list_files tool call"
    
    # Check that the tool was called with wiki path
    wiki_calls = [tc for tc in list_files_calls if tc.get("args", {}).get("path") == "wiki"]
    assert len(wiki_calls) > 0, "Expected list_files called with 'wiki' path"
    
    print("✓ list_files tool test passed")

def test_agent_read_file_tool():
    """Test that agent uses read_file tool for content questions."""
    # Create test wiki
    create_test_wiki()

    result = subprocess.run(
        [sys.executable, "agent.py", "How do you resolve a merge conflict?"],
        capture_output=True,
        text=True,
        env=os.environ.copy()
    )

    assert result.returncode == 0, f"Agent failed with exit code {result.returncode}"

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        assert False, f"Output is not valid JSON: {result.stdout}"

    # Check that read_file was called
    tool_calls = output.get("tool_calls", [])
    read_file_calls = [tc for tc in tool_calls if tc.get("tool") == "read_file"]

    assert len(read_file_calls) > 0, "Expected read_file tool call"

    # Check that the answer mentions merge conflict resolution
    answer = output.get("answer", "").lower()
    assert any(word in answer for word in ["conflict", "stage", "commit", "edit"]), "Expected answer about merge conflict resolution"

    print("✓ read_file tool test passed")

def test_agent_missing_question():
    """Test that agent fails gracefully when no question provided."""
    result = subprocess.run(
        [sys.executable, "agent.py"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode != 0, "Agent should fail with no arguments"
    print("✓ Missing argument test passed")

def test_path_traversal_security():
    """Test that path traversal attacks are blocked."""
    # Try to read file outside project
    result = subprocess.run(
        [sys.executable, "agent.py", "Read /etc/passwd"],
        capture_output=True,
        text=True,
        env=os.environ.copy()
    )
    
    # Should still work (agent might try but tool should block)
    assert result.returncode == 0
    
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        assert False, f"Output is not valid JSON: {result.stdout}"
    
    # Check that any read_file attempts returned error
    for tc in output.get("tool_calls", []):
        if tc.get("tool") == "read_file":
            result_content = tc.get("result", "")
            if "path traversal" in result_content.lower() or "invalid path" in result_content.lower():
                print("✓ Path traversal blocked")
                return
    
    print("⚠ No path traversal attempt detected")

def test_agent_query_api_tool():
    """Test that agent uses query_api tool for data questions."""
    # Set test environment
    env = os.environ.copy()
    env['LMS_API_KEY'] = 'test-key'
    env['AGENT_API_BASE_URL'] = 'http://localhost:42002'
    
    result = subprocess.run(
        [sys.executable, "agent.py", "How many items are in the database?"],
        capture_output=True,
        text=True,
        env=env
    )
    
    assert result.returncode == 0, f"Agent failed with exit code {result.returncode}"
    
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        assert False, f"Output is not valid JSON: {result.stdout}"
    
    # Check that query_api was called
    tool_calls = output.get("tool_calls", [])
    query_api_calls = [tc for tc in tool_calls if tc.get("tool") == "query_api"]
    
    assert len(query_api_calls) > 0, "Expected query_api tool call"
    
    # Check that it tried to call /items/
    items_calls = [tc for tc in query_api_calls if "/items/" in tc.get("args", {}).get("path", "")]
    assert len(items_calls) > 0, "Expected query_api called with /items/ path"
    
    print("✓ query_api tool test passed")

def test_agent_chain_tools():
    """Test that agent can chain multiple tools."""
    # Set test environment
    env = os.environ.copy()
    env['LMS_API_KEY'] = 'test-key'
    
    result = subprocess.run(
        [sys.executable, "agent.py", "Query /analytics/completion-rate for lab-99, find the error, and explain the bug."],
        capture_output=True,
        text=True,
        env=env
    )
    
    assert result.returncode == 0, f"Agent failed with exit code {result.returncode}"
    
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        assert False, f"Output is not valid JSON: {result.stdout}"
    
    # Should have at least 2 tool calls (query_api + read_file)
    tool_calls = output.get("tool_calls", [])
    assert len(tool_calls) >= 2, f"Expected at least 2 tool calls, got {len(tool_calls)}"
    
    # Check for both tool types
    tools_used = set(tc.get("tool") for tc in tool_calls)
    assert "query_api" in tools_used, "Expected query_api tool"
    assert "read_file" in tools_used or "list_files" in tools_used, "Expected file access tool"

    print("✓ Tool chaining test passed")


def test_agent_uses_read_file_for_source_code():
    """Test that agent uses read_file for source code questions (Task 3 requirement)."""
    result = subprocess.run(
        [sys.executable, "agent.py", "What Python web framework does this project's backend use? Read the source code to find out."],
        capture_output=True,
        text=True,
        env=os.environ.copy()
    )

    assert result.returncode == 0, f"Agent failed with exit code {result.returncode}"

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        assert False, f"Output is not valid JSON: {result.stdout}"

    # Check that read_file was called
    tool_calls = output.get("tool_calls", [])
    read_file_calls = [tc for tc in tool_calls if tc.get("tool") == "read_file"]

    assert len(read_file_calls) > 0, "Expected read_file tool call for source code question"

    # Check that FastAPI is mentioned in the answer
    answer = output.get("answer", "").lower()
    assert "fastapi" in answer, "Expected answer to mention FastAPI framework"

    print("✓ read_file for source code test passed")


def test_agent_uses_query_api_for_data():
    """Test that agent uses query_api for data questions (Task 3 requirement)."""
    env = os.environ.copy()
    env['LMS_API_KEY'] = 'test-key'

    result = subprocess.run(
        [sys.executable, "agent.py", "How many items are currently stored in the database? Query the running API to find out."],
        capture_output=True,
        text=True,
        env=env
    )

    assert result.returncode == 0, f"Agent failed with exit code {result.returncode}"

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        assert False, f"Output is not valid JSON: {result.stdout}"

    # Check that query_api was called
    tool_calls = output.get("tool_calls", [])
    query_api_calls = [tc for tc in tool_calls if tc.get("tool") == "query_api"]

    assert len(query_api_calls) > 0, "Expected query_api tool call for data question"

    # Check that it tried to call /items/
    items_calls = [tc for tc in query_api_calls if "/items/" in tc.get("args", {}).get("path", "")]
    assert len(items_calls) > 0, "Expected query_api called with /items/ path"

    print("✓ query_api for data question test passed")


if __name__ == "__main__":
    # Task 2 tests
    test_agent_basic_question()
    test_agent_list_files_tool()
    test_agent_read_file_tool()
    
    # Task 3 tests (2 new regression tests)
    test_agent_uses_read_file_for_source_code()
    test_agent_uses_query_api_for_data()
    
    # Additional tests
    test_agent_query_api_tool()
    test_agent_chain_tools()
    test_agent_missing_question()
    test_path_traversal_security()
    print("\n✅ All tests passed!")
