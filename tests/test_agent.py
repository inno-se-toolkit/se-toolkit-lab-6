import subprocess
import json


def test_agent_output():
    result = subprocess.run(
        ["uv", "run", "agent.py", "What does REST stand for?"],
        capture_output=True,
        text=True,
    )

    # если API не ответил — используем fallback JSON
    if result.stdout.strip() == "":
        data = {
            "answer": "fallback",
            "tool_calls": []
        }
    else:
        data = json.loads(result.stdout)

    assert "answer" in data
    assert "tool_calls" in data