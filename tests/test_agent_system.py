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

def test_agent_uses_read_file_for_framework():
    """
    Test that the agent uses 'read_file' when asked about the backend framework.
    """
    question = "What Python web framework does this project's backend use? Read the source code to find out."
    output = run_agent(question)
    
    assert "answer" in output
    assert "tool_calls" in output
    
    # Check if read_file was used
    tools_used = [tc["tool"] for tc in output["tool_calls"]]
    assert "read_file" in tools_used, f"Agent should use 'read_file' to check framework, but used: {tools_used}"
    assert "fastapi" in output["answer"].lower()

def test_agent_uses_query_api_for_items():
    """
    Test that the agent uses 'query_api' for questions about items in the database.
    """
    question = "How many items are currently stored in the database? Query the running API to find out."
    output = run_agent(question)
    
    assert "answer" in output
    assert "tool_calls" in output
    
    # Check if query_api was used
    tools_used = [tc["tool"] for tc in output["tool_calls"]]
    assert "query_api" in tools_used, f"Agent should use 'query_api' to check item count, but used: {tools_used}"
    # The answer should contain a number (the count)
    import re
    assert re.search(r"\d+", output["answer"]), f"Answer should contain a number, but got: {output['answer']}"
