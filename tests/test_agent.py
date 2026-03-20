"""Regression tests for agent.py.

Note: Tests that require LLM access need authentication.
To run full tests, ensure:
1. Qwen Code API is authenticated on your VM, OR
2. OpenRouter API key is set in .env.agent.secret
"""

import json
import subprocess
import sys
from pathlib import Path


def test_agent_returns_valid_json_structure():
    """Test that agent.py returns valid JSON structure (even on API error)."""
    project_root = Path(__file__).parent.parent

    result = subprocess.run(
        [sys.executable, str(project_root / "agent.py"), "What is 2+2?"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(project_root),
    )

    # Parse stdout as JSON (should always be valid JSON)
    output = result.stdout.strip()
    data = json.loads(output)

    # Check required fields exist (even in error case)
    assert "answer" in data, "Missing 'answer' field"
    assert "tool_calls" in data, "Missing 'tool_calls' field"
    assert "source" in data, "Missing 'source' field"
    assert isinstance(data["tool_calls"], list), "'tool_calls' must be a list"

    print(f"✓ Test passed: JSON structure valid")


def test_agent_tools_integration():
    """Test that agent tools work correctly (without LLM)."""
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    from agent import read_file, list_files
    
    # Test read_file
    content = read_file("wiki/git.md")
    assert not content.startswith("Error:"), f"read_file failed: {content}"
    assert len(content) > 0, "read_file returned empty content"
    
    # Test list_files
    files = list_files("wiki")
    assert not files.startswith("Error:"), f"list_files failed: {files}"
    assert "git.md" in files or "git-workflow.md" in files, f"Expected git files in: {files}"
    
    # Test security
    result = read_file("../secret.txt")
    assert "Error:" in result, f"Security check failed: {result}"
    
    print(f"✓ Tool integration test passed")


def test_agent_read_file_for_merge_conflict():
    """Test that agent can use read_file for git workflow questions.
    
    This test verifies the tool is available and can read the relevant file.
    Full LLM integration test requires authentication.
    """
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    from agent import read_file
    
    # Verify the git-workflow.md file exists and can be read
    content = read_file("wiki/git-workflow.md")
    assert not content.startswith("Error:"), f"Cannot read git-workflow.md: {content}"
    assert "merge" in content.lower() or "conflict" in content.lower() or "Git" in content, \
        "git-workflow.md should contain relevant content"
    
    print(f"✓ read_file for merge conflict question: file accessible")


if __name__ == "__main__":
    test_agent_returns_valid_json_structure()
    test_agent_tools_integration()
    test_agent_read_file_for_merge_conflict()
    print("\nAll tests passed!")
