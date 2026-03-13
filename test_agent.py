"""Unit tests for agent.py CLI.

These tests verify that the agent outputs valid JSON with required fields.
Run with: uv run pytest backend/tests/unit/test_agent.py -v
"""

import json
import subprocess
import sys
from pathlib import Path


def test_agent_outputs_valid_json():
    """Test that agent.py outputs valid JSON with answer and tool_calls fields."""
    # Get the project root directory (parent of test_agent.py)
    project_root = Path(__file__).parent

    # Run agent.py with a simple question
    result = subprocess.run(
        ["uv", "run", "agent.py", "What is 2+2?"],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    # Check exit code
    assert result.returncode == 0, f"Agent failed with: {result.stderr}"
    
    # Parse stdout as JSON
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Agent output is not valid JSON: {result.stdout}") from e
    
    # Check required fields exist
    assert "answer" in output, "Missing 'answer' field in output"
    assert "tool_calls" in output, "Missing 'tool_calls' field in output"
    
    # Check field types
    assert isinstance(output["answer"], str), "'answer' should be a string"
    assert isinstance(output["tool_calls"], list), "'tool_calls' should be an array"
    
    # Check answer is not empty
    assert len(output["answer"].strip()) > 0, "'answer' should not be empty"


def test_read_file_tool_is_called():
    """Test that read_file tool is called when asking about wiki content.
    
    When asking about merge conflicts, the agent should use read_file
    to find the answer in wiki/git-workflow.md.
    """
    project_root = Path(__file__).parent

    result = subprocess.run(
        ["uv", "run", "agent.py", "How do you resolve a merge conflict?"],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, f"Agent failed with: {result.stderr}"

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Agent output is not valid JSON: {result.stdout}") from e

    # Check required fields
    assert "answer" in output, "Missing 'answer' field"
    assert "tool_calls" in output, "Missing 'tool_calls' field"
    assert "source" in output, "Missing 'source' field"

    # Verify read_file was called
    tool_calls = output["tool_calls"]
    assert len(tool_calls) > 0, "No tool calls were made"
    
    read_file_called = any(
        call.get("tool") == "read_file" for call in tool_calls
    )
    assert read_file_called, "read_file tool was not called"

    # Verify source contains wiki path
    source = output["source"]
    assert "wiki/" in source, f"Source should contain wiki path, got: {source}"


def test_list_files_tool_is_called():
    """Test that list_files tool is called when asking about directory contents.
    
    When asking about files in wiki, the agent should use list_files
    to discover what files exist.
    """
    project_root = Path(__file__).parent

    result = subprocess.run(
        ["uv", "run", "agent.py", "What files are in the wiki?"],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, f"Agent failed with: {result.stderr}"

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Agent output is not valid JSON: {result.stdout}") from e

    # Check required fields
    assert "answer" in output, "Missing 'answer' field"
    assert "tool_calls" in output, "Missing 'tool_calls' field"

    # Verify list_files was called
    tool_calls = output["tool_calls"]
    assert len(tool_calls) > 0, "No tool calls were made"
    
    list_files_called = any(
        call.get("tool") == "list_files" for call in tool_calls
    )
    assert list_files_called, "list_files tool was not called"
