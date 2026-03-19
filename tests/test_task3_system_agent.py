"""
Task 3: Regression tests for system agent tools (read_file and query_api).

Tests that the agent correctly uses each tool for the appropriate question type:
- read_file for documentation lookups
- query_api for live data queries
"""

import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


class _StubLLMHandler(BaseHTTPRequestHandler):
    """Stub LLM server that responds with tool calls or final answers for Task 3."""

    def log_message(self, format, *args):
        """Suppress HTTP server logs."""
        pass

    def do_POST(self) -> None:
        if self.path != "/v1/chat/completions":
            self.send_response(404)
            self.end_headers()
            return

        # Read request body to inspect what the client is sending
        length = int(self.headers.get("Content-Length", "0"))
        body = b""
        if length:
            body = self.rfile.read(length)

        # Parse request to determine response type
        try:
            request_data = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            request_data = {}

        messages = request_data.get("messages", [])
        user_message = ""
        if messages:
            # Get the last user message (most recent question)
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break

        user_message_lower = user_message.lower()

        # Test 1: Framework question → should use read_file
        if "framework" in user_message_lower and "backend" in user_message_lower:
            response = {
                "id": "chatcmpl-test-1",
                "object": "chat.completion",
                "model": "qwen3-coder-plus",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Let me check the backend documentation.",
                            "tool_calls": [
                                {
                                    "id": "call_1",
                                    "type": "function",
                                    "function": {
                                        "name": "read_file",
                                        "arguments": '{"path": "backend/app/main.py"}',
                                    },
                                }
                            ],
                        },
                        "finish_reason": "tool_calls",
                    }
                ],
            }
        # Test 2: Item count question → should use query_api
        elif "items" in user_message_lower and ("count" in user_message_lower or "how many" in user_message_lower):
            response = {
                "id": "chatcmpl-test-2",
                "object": "chat.completion",
                "model": "qwen3-coder-plus",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Let me query the API for the item count.",
                            "tool_calls": [
                                {
                                    "id": "call_2",
                                    "type": "function",
                                    "function": {
                                        "name": "query_api",
                                        "arguments": '{"method": "GET", "path": "/items/"}',
                                    },
                                }
                            ],
                        },
                        "finish_reason": "tool_calls",
                    }
                ],
            }
        else:
            # Default: simple text answer
            response = {
                "id": "chatcmpl-test-default",
                "object": "chat.completion",
                "model": "qwen3-coder-plus",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "I can help with that question.",
                        },
                        "finish_reason": "stop",
                    }
                ],
            }

        # Send response
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())


class _StubAPIHandler(BaseHTTPRequestHandler):
    """Stub backend API server that responds to query_api requests."""

    def log_message(self, format, *args):
        """Suppress HTTP server logs."""
        pass

    def do_GET(self) -> None:
        # Check authorization header
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            self.send_response(401)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
            return

        # Route /items/ → return mock data
        if self.path == "/items/":
            response = [
                {"id": 1, "type": "lab", "title": "Lab 1", "parent_id": None},
                {"id": 2, "type": "task", "title": "Task 1", "parent_id": 1},
                {"id": 3, "type": "task", "title": "Task 2", "parent_id": 1},
            ]
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()


def _start_stub_server(handler_class, port: int) -> tuple[HTTPServer, threading.Thread]:
    """Start a stub server in a background thread."""
    server = HTTPServer(("127.0.0.1", port), handler_class)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _run_agent(question: str, timeout: int = 60):
    """Run agent.py with the question. Returns (answer_dict, error_msg)."""
    try:
        result = subprocess.run(
            [sys.executable, "agent.py", question],
            capture_output=True,
            text=True,
            timeout=timeout,
            env={
                **os.environ,
                "LLM_API_BASE": "http://127.0.0.1:9001/v1",
                "LLM_API_KEY": "test-key",
                "LLM_MODEL": "test-model",
                "LMS_API_KEY": "test-api-key",
                "AGENT_API_BASE_URL": "http://127.0.0.1:9002",
            },
        )
    except subprocess.TimeoutExpired:
        return None, "Agent timed out (60s)"
    except FileNotFoundError:
        return None, "agent.py not found"

    if result.returncode != 0:
        stderr_preview = result.stderr.strip()[:500] if result.stderr else ""
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


def test_task3_read_file_for_docs():
    """
    Test 1: Verify agent uses read_file for documentation questions.
    
    Question: "What framework does the backend use?"
    Expected: Tool calls should include "read_file" with backend code path
    """
    # Start stub servers
    llm_server, llm_thread = _start_stub_server(_StubLLMHandler, 9001)
    api_server, api_thread = _start_stub_server(_StubAPIHandler, 9002)

    try:
        # Reset to project root for test
        original_cwd = os.getcwd()
        test_dir = Path(__file__).resolve().parent.parent
        os.chdir(test_dir)

        # Run agent
        answer_dict, error = _run_agent("What framework does the backend use?")

        # Verify result
        assert error is None, f"Agent error: {error}"
        assert answer_dict is not None, "No answer returned"
        assert "answer" in answer_dict, "Missing answer field"
        assert "tool_calls" in answer_dict, "Missing tool_calls field"

        # Verify that read_file was called
        tool_calls = answer_dict.get("tool_calls", [])
        read_file_calls = [tc for tc in tool_calls if tc.get("tool") == "read_file"]
        assert len(read_file_calls) > 0, f"Expected read_file tool call, got: {tool_calls}"

        print("✓ Test 1 PASSED: Agent correctly used read_file for framework question")
        return True

    finally:
        os.chdir(original_cwd)
        llm_server.shutdown()
        api_server.shutdown()


def test_task3_query_api_for_data():
    """
    Test 2: Verify agent uses query_api for data-dependent questions.
    
    Question: "How many items are in the database?"
    Expected: Tool calls should include "query_api" with GET /items/
    """
    # Start stub servers
    llm_server, llm_thread = _start_stub_server(_StubLLMHandler, 9001)
    api_server, api_thread = _start_stub_server(_StubAPIHandler, 9002)

    try:
        # Reset to project root for test
        original_cwd = os.getcwd()
        test_dir = Path(__file__).resolve().parent.parent
        os.chdir(test_dir)

        # Run agent
        answer_dict, error = _run_agent("How many items are in the database?")

        # Verify result
        assert error is None, f"Agent error: {error}"
        assert answer_dict is not None, "No answer returned"
        assert "answer" in answer_dict, "Missing answer field"
        assert "tool_calls" in answer_dict, "Missing tool_calls field"

        # Verify that query_api was called
        tool_calls = answer_dict.get("tool_calls", [])
        query_api_calls = [tc for tc in tool_calls if tc.get("tool") == "query_api"]
        assert len(query_api_calls) > 0, f"Expected query_api tool call, got: {tool_calls}"

        # Verify the query_api call had correct method and path
        api_call = query_api_calls[0]
        assert api_call.get("args", {}).get("method", "").upper() == "GET", "Expected GET method"
        assert "/items/" in api_call.get("args", {}).get("path", ""), "Expected /items/ path"

        print("✓ Test 2 PASSED: Agent correctly used query_api for data question")
        return True

    finally:
        os.chdir(original_cwd)
        llm_server.shutdown()
        api_server.shutdown()


if __name__ == "__main__":
    try:
        result1 = test_task3_read_file_for_docs()
        result2 = test_task3_query_api_for_data()

        if result1 and result2:
            print("\n✓ All Task 3 regression tests PASSED")
            sys.exit(0)
        else:
            print("\n✗ Some tests FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
