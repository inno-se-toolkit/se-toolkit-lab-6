import json, subprocess, sys

def test_merge_conflict():
    r = subprocess.run(
        [sys.executable, "agent.py", "How do you resolve a merge conflict?"],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout.strip())
    assert "answer" in out
    assert "source" in out
    assert "tool_calls" in out
    assert len(out["tool_calls"]) > 0

def test_list_wiki():
    r = subprocess.run(
        [sys.executable, "agent.py", "What files are in the wiki?"],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout.strip())
    assert "answer" in out
    assert "tool_calls" in out
    tools_used = [t["tool"] for t in out["tool_calls"]]
    assert "list_files" in tools_used

if __name__ == "__main__":
    test_merge_conflict()
    test_list_wiki()
    print("✓ Task 2 tests passed", file=sys.stderr)