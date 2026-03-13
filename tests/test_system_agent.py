import subprocess


def test_framework_question():
    result = subprocess.run(
        ["uv", "run", "agent.py", "What framework does the backend use?"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "read_file" in result.stdout


def test_items_query():
    result = subprocess.run(
        ["uv", "run", "agent.py", "How many items are in the database?"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "query_api" in result.stdout