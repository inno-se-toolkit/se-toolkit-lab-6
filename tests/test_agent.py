import subprocess
import json
import sys
from pathlib import Path

# Добавляем корневую директорию в путь, чтобы импортировать agent.py если нужно
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

def test_agent_returns_valid_json():
    """
    Тест проверяет, что agent.py:
    1. Запускается без ошибок
    2. Выводит валидный JSON в stdout
    3. JSON содержит поля 'answer' и 'tool_calls'
    """
    # Команда для запуска агента с тестовым вопросом
    # Используем sys.executable для вызова того же интерпретатора, что и в pytest
    cmd = ["uv", "run", "agent.py", "What is Python?"]
    
    # Запускаем процесс
    result = subprocess.run(
        cmd,
        capture_output=True,  # Захватываем stdout и stderr
        text=True,            # Как текст, а не байты
        timeout=30            # Таймаут на всякий случай
    )
    
    # Проверяем, что процесс завершился успешно (код 0)
    assert result.returncode == 0, f"Agent failed with code {result.returncode}. Stderr: {result.stderr}"
    
    # Парсим stdout как JSON
    try:
        output_json = json.loads(result.stdout.strip())
    except json.JSONDecodeError as e:
        assert False, f"Output is not valid JSON: {result.stdout}. Error: {e}"
    
    # Проверяем наличие обязательных полей
    assert "answer" in output_json, "JSON missing 'answer' field"
    assert "tool_calls" in output_json, "JSON missing 'tool_calls' field"
    
    # Проверяем, что tool_calls - это список (в задании 1 он пустой)
    assert isinstance(output_json["tool_calls"], list), "'tool_calls' should be a list"
    
    # Проверяем, что answer - это строка
    assert isinstance(output_json["answer"], str), "'answer' should be a string"
    
    # Дополнительно: проверяем, что в stderr что-то есть (для отладки) 
    # но это не обязательно
    if result.stderr:
        print(f"Debug output from agent: {result.stderr}", file=sys.stderr)


def test_agent_handles_empty_input():
    """
    Тест на граничный случай: пустой вопрос
    """
    cmd = ["uv", "run", "agent.py", ""]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Даже с пустым вопросом программа должна завершиться успешно
    assert result.returncode == 0
    
    # И выдать валидный JSON
    output_json = json.loads(result.stdout.strip())
    assert "answer" in output_json
    assert "tool_calls" in output_json