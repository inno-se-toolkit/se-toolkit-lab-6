import json, subprocess, sys, os

def test_agent():
    r = subprocess.run(
        [sys.executable, "agent.py", "2+2=?"],
        capture_output=True, text=True, timeout=60,
        env=os.environ  
    )
    assert r.returncode == 0, f"Agent failed: {r.stderr}"
    out = json.loads(r.stdout.strip())
    assert "answer" in out, "Missing 'answer'"
    assert "tool_calls" in out, "Missing 'tool_calls'"
    assert isinstance(out["tool_calls"], list), "'tool_calls' must be list"

if __name__ == "__main__":
    test_agent()
    print("✓ Test passed", file=sys.stderr)
