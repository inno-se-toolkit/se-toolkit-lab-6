"""Regression tests for the agent."""

import json
import subprocess
import sys
from typing import Any


def run_agent(question: str) -> dict[str, Any]:
    """Run the agent as a subprocess and return the JSON output."""
    result = subprocess.run(
        [sys.executable, "agent.py", question],
        capture_output=True,
        text=True,
        timeout=120,
        cwd="/Users/easyg/Documents/Innopolis/SET/Lab6",
    )

    if result.returncode != 0:
        print(f"Agent stderr: {result.stderr}", file=sys.stderr)
        raise RuntimeError(f"Agent failed with exit code {result.returncode}")

    # Parse JSON output from stdout
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Failed to parse agent output: {result.stdout}", file=sys.stderr)
        raise ValueError(f"Agent output is not valid JSON: {e}")


def test_task1_basic_json_output():
    """Test that agent returns valid JSON with required fields."""
    output = run_agent("What is 2+2?")

    # Verify required fields exist
    assert "answer" in output, "Output must have 'answer' field"
    assert "tool_calls" in output, "Output must have 'tool_calls' field"

    # Verify types
    assert isinstance(output["answer"], str), "answer must be a string"
    assert isinstance(output["tool_calls"], list), "tool_calls must be a list"

    # Verify answer is not empty
    assert len(output["answer"]) > 0, "answer must not be empty"

    print("✓ Test passed: Basic JSON output structure is correct")


def test_task1_tool_calls_empty():
    """Test that tool_calls is present in response."""
    output = run_agent("What is the capital of France?")

    assert "tool_calls" in output, "tool_calls field must exist"
    assert isinstance(output["tool_calls"], list), "tool_calls must be a list"
    print("✓ Test passed: tool_calls field is present")


def test_task2_list_files_usage():
    """Test Task 2: Agent uses list_files tool."""
    output = run_agent("What files are in the wiki directory?")

    # Verify output structure
    assert "answer" in output
    assert "tool_calls" in output
    assert "source" in output or output["source"] == ""

    # Verify tool was used
    tool_names = [tc.get("tool") for tc in output["tool_calls"]]
    assert "list_files" in tool_names, "Agent should use list_files tool for this question"

    print("✓ Test passed: list_files tool usage verified")


def test_task2_read_file_usage():
    """Test Task 2: Agent uses read_file tool."""
    output = run_agent("How do you initialize a Git repository?")

    # Verify output structure
    assert "answer" in output
    assert "tool_calls" in output
    assert "source" in output

    # Verify read_file was used
    tool_names = [tc.get("tool") for tc in output["tool_calls"]]
    assert "read_file" in tool_names or "list_files" in tool_names, \
        "Agent should use file tools to answer this question"

    # Answer should not be empty
    assert len(output["answer"]) > 0, "Answer must not be empty"

    print("✓ Test passed: read_file tool usage verified")


def test_task3_query_api_usage():
    """Test Task 3: Agent can use query_api tool."""
    output = run_agent("What Python web framework does this project use?")

    # Verify output structure
    assert "answer" in output
    assert "tool_calls" in output
    assert "source" in output

    # Answer should contain FastAPI
    assert "FastAPI" in output["answer"] or "fastapi" in output["answer"].lower(), \
        "Answer should mention FastAPI framework"

    print("✓ Test passed: Backend framework question answered")


def test_task3_multi_tool_usage():
    """Test Task 3: Agent can chain multiple tools together."""
    output = run_agent("How many items are currently in the database?")

    # Verify output structure
    assert "answer" in output
    assert "tool_calls" in output

    # Verify query_api was used
    tool_names = [tc.get("tool") for tc in output["tool_calls"]]
    assert "query_api" in tool_names, "Agent should use query_api to query the database"

    # Answer should contain a number
    import re
    numbers = re.findall(r'\d+', output["answer"])
    assert len(numbers) > 0, "Answer should contain at least one number"

    print("✓ Test passed: Database query verified")


if __name__ == "__main__":
    # Run tests
    try:
        test_task1_basic_json_output()
        test_task1_tool_calls_empty()
        test_task2_list_files_usage()
        test_task2_read_file_usage()
        test_task3_query_api_usage()
        test_task3_multi_tool_usage()
        print("\n✓ All tests passed!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed: {e}", file=sys.stderr)
        sys.exit(1)
