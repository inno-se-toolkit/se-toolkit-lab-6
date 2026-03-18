"""
Regression tests for Task 1 and Task 2: Agent with Tools.

Tests verify that agent.py:
- Runs successfully
- Outputs valid JSON
- Contains required fields: answer, source, and tool_calls
- Uses tools correctly (read_file, list_files)
"""

import json
import subprocess
import sys


def get_agent_path():
    """Get the path to agent.py."""
    import os
    project_root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(project_root, "agent.py")


def run_agent(question: str) -> dict:
    """Run agent.py with a question and return parsed output."""
    import os
    
    project_root = os.path.dirname(os.path.dirname(__file__))
    agent_path = get_agent_path()
    
    result = subprocess.run(
        [sys.executable, agent_path, question],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=project_root,
    )
    
    assert result.returncode == 0, f"Agent failed with: {result.stderr}"
    
    output = result.stdout.strip()
    assert output, "No output from agent"
    
    return json.loads(output)


def test_agent_outputs_valid_json():
    """Test that agent.py outputs valid JSON with required fields."""
    # Run agent with a simple question
    data = run_agent("What is 2+2?")

    # Verify required fields exist
    assert "answer" in data, "Missing 'answer' field in output"
    assert "tool_calls" in data, "Missing 'tool_calls' field in output"

    # Verify tool_calls is an array
    assert isinstance(data["tool_calls"], list), "'tool_calls' must be an array"

    # Verify answer is non-empty
    assert data["answer"], "Answer is empty"

    print(f"✓ Test passed. Answer: {data['answer'][:50]}...")


def test_agent_read_file_tool():
    """Test that agent uses read_file tool for documentation questions."""
    # Run agent with a question that should trigger read_file
    data = run_agent("How do you resolve a merge conflict?")

    # Verify required fields
    assert "answer" in data, "Missing 'answer' field"
    assert "source" in data, "Missing 'source' field"
    assert "tool_calls" in data, "Missing 'tool_calls' field"

    # Verify read_file was called
    tool_names = [call.get("tool") for call in data["tool_calls"]]
    assert "read_file" in tool_names, "Expected read_file to be called"

    # Verify source contains wiki path
    assert "wiki/" in data["source"], f"Expected wiki path in source, got: {data['source']}"

    print(f"✓ Test passed. Source: {data['source']}")


def test_agent_list_files_tool():
    """Test that agent uses list_files tool when asked about wiki contents."""
    # Run agent with a question that should trigger list_files
    data = run_agent("What files are in the wiki?")

    # Verify required fields
    assert "answer" in data, "Missing 'answer' field"
    assert "source" in data, "Missing 'source' field"
    assert "tool_calls" in data, "Missing 'tool_calls' field"

    # Verify list_files was called
    tool_names = [call.get("tool") for call in data["tool_calls"]]
    assert "list_files" in tool_names, "Expected list_files to be called"

    print(f"✓ Test passed. Found {len(data['tool_calls'])} tool call(s)")


def test_agent_query_api_for_data_question():
    """Test that agent uses query_api for data-dependent questions."""
    # Run agent with a question that should trigger query_api
    data = run_agent("How many items are in the database?")

    # Verify required fields
    assert "answer" in data, "Missing 'answer' field"
    assert "tool_calls" in data, "Missing 'tool_calls' field"

    # Verify query_api was called
    tool_names = [call.get("tool") for call in data["tool_calls"]]
    assert "query_api" in tool_names, "Expected query_api to be called for data question"

    print(f"✓ Test passed. Agent used query_api for data question")


def test_agent_read_file_for_framework_question():
    """Test that agent uses read_file for system framework questions."""
    # Run agent with a question about the backend framework
    data = run_agent("What Python web framework does this project use?")

    # Verify required fields
    assert "answer" in data, "Missing 'answer' field"
    assert "source" in data, "Missing 'source' field"
    assert "tool_calls" in data, "Missing 'tool_calls' field"

    # Verify read_file was called (framework info should be in documentation)
    tool_names = [call.get("tool") for call in data["tool_calls"]]
    assert "read_file" in tool_names, "Expected read_file to be called for framework question"

    print(f"✓ Test passed. Agent used read_file for framework question")
