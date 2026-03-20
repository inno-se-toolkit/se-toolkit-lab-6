"""Unit tests for agent tools."""

import sys
from pathlib import Path

# Import tools from agent.py
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent import read_file, list_files, PROJECT_ROOT


def test_read_file_exists():
    """Test that read_file can read an existing file."""
    result = read_file("wiki/git.md")
    assert not result.startswith("Error:"), f"Failed to read existing file: {result}"
    assert len(result) > 0, "File content is empty"
    print(f"✓ read_file exists: read {len(result)} bytes")


def test_read_file_not_exists():
    """Test that read_file returns error for non-existent file."""
    result = read_file("wiki/nonexistent.md")
    assert result.startswith("Error:"), f"Should return error for non-existent file: {result}"
    print(f"✓ read_file not exists: {result}")


def test_read_file_security():
    """Test that read_file blocks path traversal."""
    result = read_file("../secret.txt")
    assert "Error:" in result, f"Should block path traversal: {result}"
    print(f"✓ read_file security: {result}")


def test_list_files_exists():
    """Test that list_files can list an existing directory."""
    result = list_files("wiki")
    assert not result.startswith("Error:"), f"Failed to list existing directory: {result}"
    assert "git.md" in result or "git-workflow.md" in result, f"Should contain git files: {result}"
    print(f"✓ list_files exists: found {len(result.splitlines())} files")


def test_list_files_security():
    """Test that list_files blocks path traversal."""
    result = list_files("../secret")
    assert "Error:" in result, f"Should block path traversal: {result}"
    print(f"✓ list_files security: {result}")


if __name__ == "__main__":
    test_read_file_exists()
    test_read_file_not_exists()
    test_read_file_security()
    test_list_files_exists()
    test_list_files_security()
    print("\nAll tool tests passed!")
