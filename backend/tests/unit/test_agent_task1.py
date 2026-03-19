import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


class _FakeLlmHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        body = {
            "id": "test-id",
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Representational State Transfer.",
                    },
                    "finish_reason": "stop",
                }
            ],
        }

        encoded = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: object) -> None:
        return


def test_agent_outputs_answer_and_tool_calls() -> None:
    server = HTTPServer(("127.0.0.1", 0), _FakeLlmHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    env = os.environ.copy()
    env["LLM_API_KEY"] = "test-key"
    env["LLM_API_BASE"] = f"http://127.0.0.1:{server.server_port}/v1"
    env["LLM_MODEL"] = "qwen3-coder-plus"

    try:
        result = subprocess.run(
            [sys.executable, "agent.py", "What does REST stand for?"],
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
            capture_output=True,
            text=True,
            env=env,
            timeout=60,
            check=False,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)

    assert result.returncode == 0, result.stderr

    data = json.loads(result.stdout)
    assert "answer" in data
    assert "tool_calls" in data
    assert isinstance(data["tool_calls"], list)
