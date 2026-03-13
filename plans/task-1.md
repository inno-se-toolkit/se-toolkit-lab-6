# Task 1 Plan: Call an LLM from Code

## LLM Provider

**Provider:** Qwen Code API (через qwen-code-oai-proxy на VM)

**Model:** `qwen3-coder-plus`

**Почему этот выбор:**
- 1000 бесплатных запросов в день
- Доступно из России
- Не требует кредитную карту
- OpenAI-совместимый API (можно использовать тот же клиент)

## Конфигурация

Агент будет читать настройки из `.env.agent.secret`:
- `LLM_API_KEY` — API ключ от Qwen Code
- `LLM_API_BASE` — URL endpoint (например, `http://<vm-ip>:<port>/v1`)
- `LLM_MODEL` — имя модели (`qwen3-coder-plus`)

## Структура агента

### Входные данные
- Вопрос передаётся как первый аргумент командной строки: `uv run agent.py "Вопрос"`

### Обработка
1. Парсинг аргументов командной строки (argparse или sys.argv)
2. Чтение конфигурации из `.env.agent.secret` (библиотека `python-dotenv` или вручную)
3. Вызов LLM через HTTP запрос к OpenAI-совместимому API (библиотека `httpx`)
4. Форматирование ответа в JSON

### Выходные данные
JSON в stdout:
```json
{"answer": "Текст ответа", "tool_calls": []}
```

### Обработка ошибок
- Timeout 60 секунд на запрос к LLM
- Валидация JSON ответа
- Exit code 0 при успехе, non-zero при ошибке
- Все debug сообщения в stderr (не в stdout)

## Зависимости

- `httpx` — HTTP клиент для запросов к API (уже есть в pyproject.toml)
- `pydantic-settings` — для чтения .env файла (уже есть в pyproject.toml)
- Стандартные: `sys`, `json`, `os`

## Тестирование

Один regression test (`test_agent.py`):
- Запускает `agent.py` как subprocess
- Проверяет exit code = 0
- Проверяет валидность JSON в stdout
- Проверяет наличие полей `answer` и `tool_calls`
