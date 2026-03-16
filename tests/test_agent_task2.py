"""Тесты для агента с файловыми инструментами (задача 2)."""

import json
import subprocess
import sys
from pathlib import Path


def invoke_agent(query: str) -> dict:
    """Запускает агента и возвращает распарсенный JSON."""
    agent_path = Path(__file__).parent.parent / "agent.py"
    proc = subprocess.run(
        [sys.executable, str(agent_path), query],
        capture_output=True,
        text=True,
        timeout=120
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Ошибка агента: {proc.stderr}")
    return json.loads(proc.stdout)


class TestFileOperations:

    def test_merge_conflict_query(self):
        """При вопросе о merge conflict агент должен читать файл."""
        result = invoke_agent("Как разрешить merge conflict?")

        assert "answer" in result
        assert "source" in result
        assert "tool_calls" in result

        calls = result["tool_calls"]
        assert len(calls) > 0, "Ожидались вызовы инструментов"

        tools_used = [c["tool"] for c in calls]
        assert "read_file" in tools_used, "Инструмент read_file не был вызван"

        # Проверим, что источник упоминает wiki
        src = result["source"]
        assert "wiki/" in src or any(
            "wiki/" in c["args"].get("target", "") for c in calls if c["tool"] == "read_file"
        ), "Источник не содержит wiki"

    def test_wiki_content_query(self):
        """При вопросе о содержимом wiki должен вызываться list_dir."""
        result = invoke_agent("Какие файлы есть в wiki?")

        calls = result["tool_calls"]
        tools_used = [c["tool"] for c in calls]
        assert "list_dir" in tools_used, "Инструмент list_dir не использован"

        list_calls = [c for c in calls if c["tool"] == "list_dir"]
        wiki_calls = [c for c in list_calls if "wiki" in c["args"].get("folder", "")]
        assert len(wiki_calls) > 0, "list_dir не вызывался с папкой wiki"

    def test_output_structure(self):
        """Проверка структуры каждого вызова инструмента."""
        result = invoke_agent("Что такое проект?")
        for call in result["tool_calls"]:
            assert "tool" in call
            assert "args" in call
            assert "result" in call
            assert isinstance(call["args"], dict)
            assert isinstance(call["result"], str)
