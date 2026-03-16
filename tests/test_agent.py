"""Проверка базовой работы агента: валидность JSON и обязательные поля."""

import json
import subprocess
import sys
from pathlib import Path


def locate_agent() -> Path:
    """Возвращает путь к исполняемому файлу агента."""
    root = Path(__file__).parent.parent
    return root / "agent.py"


class TestAgentBasics:

    def test_output_is_valid_json_with_required_fields(self):
        """Убеждаемся, что агент возвращает корректный JSON и содержит answer / tool_calls."""
        agent_path = locate_agent()
        proc = subprocess.run(
            [sys.executable, str(agent_path), "Сколько будет 2+2?"],
            capture_output=True,
            text=True,
            timeout=90
        )
        assert proc.returncode == 0, f"Агент завершился с ошибкой: {proc.stderr}"

        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError as e:
            raise AssertionError(f"Невалидный JSON: {e}\nstdout: {proc.stdout}")

        assert "answer" in data, "Отсутствует поле 'answer'"
        assert "tool_calls" in data, "Отсутствует поле 'tool_calls'"
        assert isinstance(data["answer"], str), "Поле answer должно быть строкой"
        assert isinstance(data["tool_calls"], list), "Поле tool_calls должно быть списком"
        assert len(data["answer"]) > 0, "Ответ не должен быть пустым"
