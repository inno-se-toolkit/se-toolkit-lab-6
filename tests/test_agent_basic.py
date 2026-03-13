import json
import subprocess
import pytest

def test_agent_basic_response():
    """
    Test that the agent.py script returns a valid JSON response with 'answer' and 'tool_calls'.
    """
    question = "What is 2+2?"
    
    # Run agent.py as a subprocess
    result = subprocess.run(
        ["uv", "run", "agent.py", question],
        capture_output=True,
        text=True,
        check=True
    )
    
    # Parse stdout as JSON
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"Stdout is not a valid JSON: {result.stdout}")
    
    # Verify the structure
    assert "answer" in output, "Response missing 'answer' field"
    assert "tool_calls" in output, "Response missing 'tool_calls' field"
    assert isinstance(output["tool_calls"], list), "'tool_calls' should be a list"
    assert len(output["tool_calls"]) == 0, "For Task 1, 'tool_calls' should be empty"
    
    # Basic check for answer content (the LLM should be able to answer what is 2+2)
    assert "4" in output["answer"], f"Expected '4' in answer, but got: {output['answer']}"
