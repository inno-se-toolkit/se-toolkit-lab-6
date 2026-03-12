#!/usr/bin/env python3
"""Local evaluation runner for the agent benchmark.

Fetches questions one at a time from the autochecker API,
runs your agent, and checks the answer locally.
Stops at the first failure.

Usage:
    uv run run_eval.py           # all questions, stop at first fail
    uv run run_eval.py --index 5 # single question (for debugging)

Reads from .env (same credentials as the autochecker):
    AUTOCHECKER_API_URL  — e.g. https://auche.namaz.live
    AUTOCHECKER_EMAIL    — your university email
    AUTOCHECKER_PASSWORD — your GitHub username + Telegram alias

Note:
    This runner tests your agent against the LOCAL question set only.
    The autochecker bot tests ADDITIONAL hidden questions not shown here.
    Some questions use LLM-based judging on the bot side for more accurate
    scoring (locally they fall back to simple keyword matching).
    You need >=75% overall (local + hidden) to pass.
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def _load_env():
    """Load variables from .env file (simple key=value parser)."""
    for env_file in [".env", ".env.docker.secret"]:
        path = Path(env_file)
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def _get_credentials():
    """Return (api_url, email, password) from environment."""
    api_url = os.environ.get("AUTOCHECKER_API_URL", "")
    email = os.environ.get("AUTOCHECKER_EMAIL", "")
    password = os.environ.get("AUTOCHECKER_PASSWORD", "")
    if not all([api_url, email, password]):
        print(
            "Missing credentials. Set AUTOCHECKER_API_URL, AUTOCHECKER_EMAIL, "
            "and AUTOCHECKER_PASSWORD in your .env file.",
            file=sys.stderr,
        )
        sys.exit(1)
    return api_url.rstrip("/"), email, password


def _basic_auth_header(email: str, password: str) -> str:
    """Build HTTP Basic Auth header value."""
    encoded = base64.b64encode(f"{email}:{password}".encode()).decode()
    return f"Basic {encoded}"


def _fetch_question(api_url: str, auth: str, lab: str, index: int):
    """Fetch a question from the autochecker API. Returns dict or None on 404."""
    import urllib.request
    import urllib.error

    url = f"{api_url}/api/eval/question?lab={lab}&index={index}"
    req = urllib.request.Request(url, headers={"Authorization": auth})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        body = e.read().decode() if e.fp else ""
        print(f"API error {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Cannot reach API: {e.reason}", file=sys.stderr)
        sys.exit(1)


def _run_agent(question: str, timeout: int = 60):
    """Run agent.py with the question. Returns (answer_dict, error_msg)."""
    try:
        result = subprocess.run(
            [sys.executable, "agent.py", question],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return None, "Agent timed out (60s)"
    except FileNotFoundError:
        return None, "agent.py not found"

    if result.returncode != 0:
        stderr_preview = result.stderr.strip()[:200] if result.stderr else ""
        return None, f"Agent exited with code {result.returncode}: {stderr_preview}"

    stdout = result.stdout.strip()
    if not stdout:
        return None, "Agent produced no output"

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return None, f"Agent output is not valid JSON: {stdout[:200]}"

    if "answer" not in data:
        return None, f"Missing 'answer' field in output: {stdout[:200]}"

    return data, None


# ---------------------------------------------------------------------------
# Matching logic (mirrors autochecker evaluation)
# ---------------------------------------------------------------------------

def _match(text: str, rule: dict) -> bool:
    """Check if text satisfies the matching rule."""
    text_lower = text.lower()

    if "contains" in rule:
        return rule["contains"].lower() in text_lower

    if "contains_all" in rule:
        return all(kw.lower() in text_lower for kw in rule["contains_all"])

    if "any_of" in rule:
        return any(kw.lower() in text_lower for kw in rule["any_of"])

    if "regex" in rule:
        return bool(re.search(rule["regex"], text, re.IGNORECASE))

    if "numeric_gt" in rule:
        numbers = re.findall(r"[\d.]+", text)
        return any(float(n) > rule["numeric_gt"] for n in numbers if n)

    if "numeric_range" in rule:
        lo, hi = rule["numeric_range"]
        numbers = re.findall(r"[\d.]+", text)
        return any(lo <= float(n) <= hi for n in numbers if n)

    return False


def _format_expected(expected: dict) -> str:
    """Human-readable description of the expected match."""
    if "contains" in expected:
        return f"answer should contain: \"{expected['contains']}\""
    if "contains_all" in expected:
        return f"answer should contain all of: {expected['contains_all']}"
    if "any_of" in expected:
        return f"answer should contain any of: {expected['any_of']}"
    if "regex" in expected:
        return f"answer should match pattern: {expected['regex']}"
    if "numeric_gt" in expected:
        return f"answer should contain a number > {expected['numeric_gt']}"
    if "numeric_range" in expected:
        return f"answer should contain a number in range {expected['numeric_range']}"
    return str(expected)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

LAB = "lab-06"


def _check_question(q: dict, data: dict) -> tuple[bool, str]:
    """Check agent output against question expectations.

    Returns (passed, failure_reason). failure_reason is empty on pass.
    Checks: (1) answer keywords, (2) source reference, (3) tool usage.
    """
    answer = data.get("answer", "")
    expected = q.get("expected", {})

    # Check answer
    if expected:
        if not _match(answer, expected):
            feedback = q.get("feedback")
            if feedback:
                return False, f"    {YELLOW}hint: {feedback}{RESET}"
            else:
                return False, f"    Expected: {_format_expected(expected)}"
    elif q.get("has_rubric"):
        # Rubric-only question — locally we can only do a basic length check.
        # The autochecker bot uses LLM-based judging for more accurate scoring.
        if len(answer.split()) < 20:
            return False, f"    {YELLOW}Answer too short for a reasoning question (bot uses LLM judge){RESET}"

    # Check source if expected_source is defined
    expected_source = q.get("expected_source")
    if expected_source:
        source = data.get("source", "")
        if not source:
            return False, f"    Missing 'source' field (expected a file reference)"
        if not _match(source, expected_source):
            feedback = q.get("feedback")
            if feedback:
                return False, f"    {YELLOW}hint: {feedback}{RESET}"
            else:
                return False, f"    Source '{source}' doesn't match expected"

    # Check tool usage
    check_tools = q.get("check_tools")
    if check_tools:
        tool_calls = data.get("tool_calls", [])
        tools_used = {tc.get("tool") for tc in tool_calls} if tool_calls else set()
        missing = set(check_tools) - tools_used
        if missing:
            return False, (
                f"    Expected tool calls: {', '.join(check_tools)}\n"
                f"    Missing: {', '.join(missing)}\n"
                f"    Your agent used: {', '.join(tools_used) or '(none)'}"
            )

    return True, ""


def main():
    parser = argparse.ArgumentParser(description="Run agent evaluation benchmark")
    parser.add_argument(
        "--index", type=int, default=None,
        help="Run a single question by index (for debugging)"
    )
    args = parser.parse_args()

    _load_env()
    api_url, email, password = _get_credentials()
    auth = _basic_auth_header(email, password)

    if args.index is not None:
        # Single question mode
        q = _fetch_question(api_url, auth, LAB, args.index)
        if q is None:
            print(f"Question {args.index} not found", file=sys.stderr)
            sys.exit(1)

        question = q["question"]
        print(f"  [{args.index}] {question}")

        data, error = _run_agent(question)
        if error:
            print(f"  {RED}Error: {error}{RESET}")
            sys.exit(1)

        passed, reason = _check_question(q, data)
        answer = data.get("answer", "")
        source = data.get("source", "")
        tool_calls = data.get("tool_calls", [])

        print(f"  Answer: {answer[:200]}")
        if source:
            print(f"  Source: {source}")
        if tool_calls:
            tools_used = [tc.get("tool", "?") for tc in tool_calls]
            print(f"  Tools: {', '.join(tools_used)}")

        if passed:
            print(f"  {GREEN}PASSED{RESET}")
        else:
            print(f"  {RED}FAILED{RESET}")
            print(reason)
            sys.exit(1)
        return

    # Full run mode — stop at first failure
    index = 0
    passed = 0

    while True:
        q = _fetch_question(api_url, auth, LAB, index)
        if q is None:
            # All questions done
            print(f"\n{BOLD}{GREEN}{passed}/{index} PASSED{RESET}")
            print(
                f"\n{YELLOW}Note: The autochecker bot tests {index} additional hidden questions"
                f" and may use LLM-based judging for open-ended answers."
                f" You need >=75% overall to pass.{RESET}"
            )
            break

        total = q["total"]
        question = q["question"]

        # Run the agent
        data, error = _run_agent(question)

        if error:
            print(f"\n  {RED}x [{index + 1}/{total}] {question}{RESET}")
            print(f"    Error: {error}")
            print(f"\n{BOLD}{passed}/{total} passed{RESET}")
            sys.exit(1)

        ok, reason = _check_question(q, data)

        if ok:
            print(f"  {GREEN}+ [{index + 1}/{total}] {question}{RESET}")
            passed += 1
            index += 1
        else:
            answer = data.get("answer", "")
            print(f"\n  {RED}x [{index + 1}/{total}] {question}{RESET}")
            print(f"    Your answer: {answer[:200]}")
            print(reason)
            print(f"\n{BOLD}{passed}/{total} passed{RESET}")
            sys.exit(1)


if __name__ == "__main__":
    main()
