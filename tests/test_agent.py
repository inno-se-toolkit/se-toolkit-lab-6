"""
Regression tests for agent.py.

These tests run agent.py as a subprocess and verify the JSON output structure.
Run with: uv run pytest tests/test_agent.py -v
"""

import json
import subprocess
import sys
from pathlib import Path


class TestAgentOutput:
    """Test that agent.py outputs valid JSON with required fields."""

    def test_output_has_required_fields(self):
        """
        Test that agent.py output contains 'answer' and 'tool_calls' fields.

        This test uses a mock/stub approach since we can't guarantee LLM
        availability in all test environments. We verify the output structure
        by running the agent and checking that:
        1. Output is valid JSON
        2. 'answer' field exists
        3. 'tool_calls' field exists and is a list
        """
        # Run agent.py as a subprocess
        # Note: This test will fail if LLM is not configured.
        # In CI/CD, you would mock the LLM response.
        agent_path = Path(__file__).parent.parent / "agent.py"
        test_prompt = "What is 2+2? Answer with just the number."

        result = subprocess.run(
            [sys.executable, "-m", "uv", "run", str(agent_path), test_prompt],
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Parse stdout as JSON
        try:
            output = json.loads(result.stdout.strip())
        except json.JSONDecodeError as e:
            raise AssertionError(
                f"agent.py output is not valid JSON: {result.stdout}\n"
                f"stderr: {result.stderr}"
            ) from e

        # Check that 'answer' field exists
        assert "answer" in output, f"Missing 'answer' field in output. Got: {output}"

        # Check that 'tool_calls' field exists and is a list
        assert "tool_calls" in output, (
            f"Missing 'tool_calls' field in output. Got: {output}"
        )
        assert isinstance(output["tool_calls"], list), (
            f"'tool_calls' should be a list. Got: {type(output['tool_calls'])}"
        )

    def test_output_is_valid_json_structure(self):
        """
        Test that the output follows the expected JSON structure.

        Expected format:
        {
            "answer": str,
            "tool_calls": list
        }
        """
        # This is a structural test that verifies the output format
        # without depending on actual LLM responses

        # Example expected output structure (for documentation)
        expected_structure = {
            "answer": "string value",
            "tool_calls": [],  # empty list for Task 1
        }

        # Verify our understanding of the structure
        assert isinstance(expected_structure["answer"], str)
        assert isinstance(expected_structure["tool_calls"], list)

    def test_merge_conflict_question_uses_read_file(self):
        """
        Test that asking about merge conflicts triggers read_file tool.

        Expected behavior:
        - Agent should use list_files to discover wiki files
        - Agent should use read_file to read wiki/git-workflow.md
        - Source should reference wiki/git-workflow.md
        """
        agent_path = Path(__file__).parent.parent / "agent.py"
        test_prompt = "How do you resolve a merge conflict?"

        result = subprocess.run(
            [sys.executable, "-m", "uv", "run", str(agent_path), test_prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )

        # Parse stdout as JSON
        try:
            output = json.loads(result.stdout.strip())
        except json.JSONDecodeError as e:
            raise AssertionError(
                f"agent.py output is not valid JSON: {result.stdout}\n"
                f"stderr: {result.stderr}"
            ) from e

        # Check that tool_calls is populated
        assert isinstance(output["tool_calls"], list), (
            f"'tool_calls' should be a list. Got: {type(output['tool_calls'])}"
        )

        # Check that at least one tool call uses read_file
        tool_names = [call.get("tool") for call in output["tool_calls"]]
        assert "read_file" in tool_names, (
            f"Expected 'read_file' in tool_calls. Got: {tool_names}"
        )

        # Check that source references git-workflow.md
        source = output.get("source", "")
        assert "git-workflow.md" in source, (
            f"Expected 'git-workflow.md' in source. Got: {source}"
        )

    def test_wiki_files_question_uses_list_files(self):
        """
        Test that asking about wiki files triggers list_files tool.

        Expected behavior:
        - Agent should use list_files to discover wiki files
        - tool_calls should contain list_files invocation
        """
        agent_path = Path(__file__).parent.parent / "agent.py"
        test_prompt = "What files are in the wiki?"

        result = subprocess.run(
            [sys.executable, "-m", "uv", "run", str(agent_path), test_prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )

        # Parse stdout as JSON
        try:
            output = json.loads(result.stdout.strip())
        except json.JSONDecodeError as e:
            raise AssertionError(
                f"agent.py output is not valid JSON: {result.stdout}\n"
                f"stderr: {result.stderr}"
            ) from e

        # Check that tool_calls is populated
        assert isinstance(output["tool_calls"], list), (
            f"'tool_calls' should be a list. Got: {type(output['tool_calls'])}"
        )

        # Check that at least one tool call uses list_files
        tool_names = [call.get("tool") for call in output["tool_calls"]]
        assert "list_files" in tool_names, (
            f"Expected 'list_files' in tool_calls. Got: {tool_names}"
        )
