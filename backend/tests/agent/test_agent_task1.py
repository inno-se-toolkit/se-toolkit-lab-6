"""
Regression test for Task 1: Call an LLM from Code.

This test runs agent.py as a subprocess, parses the stdout JSON,
and checks that 'answer' and 'tool_calls' fields are present.
"""

import json
import subprocess
import sys
from pathlib import Path


def get_agent_path() -> Path:
    """Get the path to agent.py in the project root."""
    return Path(__file__).parent.parent.parent.parent / "agent.py"


def test_agent_output_format() -> None:
    """
    Test that agent.py outputs valid JSON with required fields.
    
    This test verifies:
    1. agent.py runs successfully (exit code 0)
    2. stdout contains valid JSON
    3. JSON has 'answer' field (string)
    4. JSON has 'tool_calls' field (array)
    """
    agent_path = get_agent_path()
    
    if not agent_path.exists():
        raise AssertionError(f"agent.py not found at {agent_path}")
    
    # Use a simple question that should work even with mocked/stubbed LLM
    question = "What is 2 + 2?"
    
    # Run agent.py directly using the same Python interpreter
    result = subprocess.run(
        [sys.executable, str(agent_path), question],
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    # Check exit code
    assert result.returncode == 0, (
        f"agent.py failed with exit code {result.returncode}\n"
        f"stderr: {result.stderr}"
    )
    
    # Parse JSON from stdout
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(
            f"Invalid JSON in stdout: {result.stdout}\nError: {e}"
        ) from e
    
    # Check required fields
    assert "answer" in output, "Missing 'answer' field in output"
    assert isinstance(output["answer"], str), (
        f"'answer' must be a string, got {type(output['answer'])}"
    )
    
    assert "tool_calls" in output, "Missing 'tool_calls' field in output"
    assert isinstance(output["tool_calls"], list), (
        f"'tool_calls' must be an array, got {type(output['tool_calls'])}"
    )
    
    # Verify answer is not empty
    assert len(output["answer"]) > 0, "'answer' field is empty"


def test_agent_empty_question_error() -> None:
    """Test that agent.py handles empty questions with an error."""
    agent_path = get_agent_path()
    
    result = subprocess.run(
        [sys.executable, str(agent_path), ""],
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    # Should fail with non-zero exit code
    assert result.returncode != 0, "agent.py should fail on empty question"


def test_agent_no_question_error() -> None:
    """Test that agent.py handles missing question with an error."""
    agent_path = get_agent_path()
    
    result = subprocess.run(
        [sys.executable, str(agent_path)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    # Should fail with non-zero exit code
    assert result.returncode != 0, "agent.py should fail without question argument"
