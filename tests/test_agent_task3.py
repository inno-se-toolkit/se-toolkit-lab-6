"""Тесты для агента с API-запросами (задача 3)."""

import json
import subprocess
import sys
import re
from pathlib import Path


def run_agent(query: str) -> dict:
    """Запуск агента, возврат распарсенного JSON."""
    agent = Path(__file__).parent.parent / "agent.py"
    proc = subprocess.run(
        [sys.executable, str(agent), query],
        capture_output=True,
        text=True,
        timeout=120
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Агент упал: {proc.stderr}")
    return json.loads(proc.stdout)


class TestSystemAgent:

    def test_framework_question(self):
        """Вопрос о фреймворке должен заставить агента читать исходники."""
        out = run_agent("Какой веб-фреймворк используется в бэкенде?")

        tools = [c["tool"] for c in out["tool_calls"]]
        assert "read_file" in tools, "Ожидался вызов read_file"

        answer_low = out["answer"].lower()
        assert "fastapi" in answer_low, f"Ответ не содержит 'fastapi': {out['answer']}"

    def test_database_item_count(self):
        """Вопрос о количестве записей должен приводить к вызову API."""
        out = run_agent("Сколько элементов в базе данных?")

        tools = [c["tool"] for c in out["tool_calls"]]
        assert "call_api" in tools, "Ожидался вызов call_api"

        digits = re.findall(r'\d+', out["answer"])
        assert len(digits) > 0, f"Ответ не содержит числа: {out['answer']}"

    def test_tool_call_structure(self):
        """Проверка формата записей о вызовах."""
        out = run_agent("Покажи содержимое wiki папки.")
        for c in out["tool_calls"]:
            assert "tool" in c
            assert "args" in c
            assert "result" in c
            assert isinstance(c["args"], dict)
            assert isinstance(c["result"], str)
