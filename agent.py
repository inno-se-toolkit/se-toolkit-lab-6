#!/usr/bin/env python3
"""
Интерфейс командной строки для взаимодействия с LLM и выполнения действий.
Использование: python agent.py "Ваш вопрос"
"""

import json
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

import httpx
from dotenv import load_dotenv


class ApplicationContext:
    """Контекст приложения, хранящий настройки и состояние."""

    def __init__(self):
        self._load_secrets()
        self.project_home = Path(__file__).parent.resolve()
        self.conversation_history: List[Dict[str, Any]] = []
        self.action_records: List[Dict[str, Any]] = []
        self.max_action_rounds = 10

    def _load_secrets(self):
        """Загружает переменные окружения из файлов .env.agent.secret и .env.docker.secret."""
        secret_path = Path(__file__).parent / ".env.agent.secret"
        if secret_path.exists():
            load_dotenv(secret_path)
        docker_secret = Path(__file__).parent / ".env.docker.secret"
        if docker_secret.exists():
            load_dotenv(docker_secret)

        self.llm_token = os.getenv("LLM_API_KEY")
        self.llm_endpoint = os.getenv("LLM_API_BASE")
        self.llm_model_name = os.getenv("LLM_MODEL")
        self.service_token = os.getenv("LMS_API_KEY")
        self.backend_base = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")

        if not all([self.llm_token, self.llm_endpoint, self.llm_model_name]):
            sys.stderr.write("Ошибка: не заданы ключи LLM в окружении.\n")
            sys.exit(1)


class ActionRegistry:
    """Реестр доступных действий, которые может выполнять агент."""

    def __init__(self, context: ApplicationContext):
        self.ctx = context
        self._actions: Dict[str, Dict[str, Any]] = {}
        self._register_core_actions()

    def _register_core_actions(self):
        """Регистрирует встроенные действия."""

        self.register(
            name="read_file",
            description="Прочитать содержимое файла внутри проекта",
            parameters={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Относительный путь к файлу (например, 'wiki/git-workflow.md')"
                    }
                },
                "required": ["target"]
            },
            handler=self._handle_read_file
        )

        self.register(
            name="list_dir",
            description="Показать содержимое папки проекта",
            parameters={
                "type": "object",
                "properties": {
                    "folder": {
                        "type": "string",
                        "description": "Относительный путь к папке (например, 'wiki')"
                    }
                },
                "required": ["folder"]
            },
            handler=self._handle_list_dir
        )

        self.register(
            name="call_api",
            description="Вызвать развёрнутое API бэкенда",
            parameters={
                "type": "object",
                "properties": {
                    "verb": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                        "description": "HTTP метод"
                    },
                    "route": {
                        "type": "string",
                        "description": "Путь эндпоинта (например, '/items/')"
                    },
                    "payload": {
                        "type": "string",
                        "description": "Тело запроса в JSON (для POST/PUT)"
                    },
                    "use_auth": {
                        "type": "boolean",
                        "description": "Включать ли заголовок авторизации (по умолчанию true)"
                    }
                },
                "required": ["verb", "route"]
            },
            handler=self._handle_call_api
        )

    def register(self, name: str, description: str, parameters: dict, handler: Callable):
        """Добавляет новое действие в реестр."""
        self._actions[name] = {
            "schema": {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters
                }
            },
            "handler": handler
        }

    def get_schemas(self) -> List[dict]:
        """Возвращает список схем для передачи LLM."""
        return [item["schema"] for item in self._actions.values()]

    def execute(self, name: str, arguments: dict) -> str:
        """Выполняет действие по имени с заданными аргументами."""
        if name not in self._actions:
            return f"Ошибка: неизвестное действие '{name}'"
        try:
            return self._actions[name]["handler"](arguments)
        except Exception as e:
            return f"Ошибка при выполнении {name}: {e}"

    # ----- Обработчики действий -----

    def _safe_resolve(self, user_path: str) -> Path:
        """Проверяет, что путь не выходит за пределы проекта."""
        if ".." in user_path or user_path.startswith("/"):
            raise ValueError("Недопустимый путь")
        return (self.ctx.project_home / user_path).resolve()

    def _handle_read_file(self, args: dict) -> str:
        target = args.get("target", "")
        try:
            full = self._safe_resolve(target)
            if not full.is_file():
                return f"Файл не найден: {target}"
            return full.read_text(encoding="utf-8")
        except Exception as e:
            return f"Ошибка чтения файла: {e}"

    def _handle_list_dir(self, args: dict) -> str:
        folder = args.get("folder", "")
        try:
            full = self._safe_resolve(folder)
            if not full.is_dir():
                return f"Папка не найдена: {folder}"
            items = [p.name for p in full.iterdir() if not p.name.startswith(".") and p.name != "__pycache__"]
            return "\n".join(sorted(items))
        except Exception as e:
            return f"Ошибка при просмотре папки: {e}"

    def _handle_call_api(self, args: dict) -> str:
        verb = args.get("verb", "GET").upper()
        route = args.get("route", "")
        payload = args.get("payload")
        use_auth = args.get("use_auth", True)

        url = self.ctx.backend_base.rstrip("/") + route
        headers = {"Content-Type": "application/json"}

        if use_auth:
            if not self.ctx.service_token:
                return "Ошибка: LMS_API_KEY не задан"
            headers["Authorization"] = f"Bearer {self.ctx.service_token}"

        try:
            with httpx.Client(timeout=30.0) as client:
                if verb == "GET":
                    resp = client.get(url, headers=headers)
                elif verb == "POST":
                    body = json.loads(payload) if payload else {}
                    resp = client.post(url, headers=headers, json=body)
                elif verb == "PUT":
                    body = json.loads(payload) if payload else {}
                    resp = client.put(url, headers=headers, json=body)
                elif verb == "DELETE":
                    resp = client.delete(url, headers=headers)
                elif verb == "PATCH":
                    body = json.loads(payload) if payload else {}
                    resp = client.patch(url, headers=headers, json=body)
                else:
                    return f"Ошибка: неподдерживаемый метод {verb}"
                return json.dumps({"status_code": resp.status_code, "body": resp.text})
        except Exception as e:
            return f"Ошибка вызова API: {e}"


class DialogueEngine:
    """Управляет диалогом с LLM и выполняет действия."""

    SYSTEM_MESSAGE = """Ты ассистент, который помогает отвечать на вопросы о проекте. У тебя есть три инструмента:

- read_file – читает файл внутри проекта.
- list_dir – показывает содержимое папки.
- call_api – отправляет HTTP-запрос к работающему бэкенду.

Как пользоваться инструментами:
- Для вопросов о документации: сначала list_dir папки 'wiki', потом read_file нужных файлов.
- Для вопросов о коде: list_dir 'backend/app', затем read_file конкретных файлов.
- Для получения живых данных (количество элементов, статусы) используй call_api с нужным путём.
- При диагностике ошибок сначала вызывай API, чтобы увидеть ошибку, потом читай код в месте ошибки.

Всегда указывай источник:
- wiki/имя_файла.md#раздел
- backend/путь/к/файлу.py
- путь API

Не делай более 5 вызовов подряд без прогресса. Будь краток."""

    def __init__(self, context: ApplicationContext, registry: ActionRegistry):
        self.ctx = context
        self.registry = registry

    def _call_llm(self, messages: List[dict]) -> dict:
        """Отправляет запрос к LLM и возвращает ответ."""
        url = f"{self.ctx.llm_endpoint}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.ctx.llm_token}",
            "Content-Type": "application/json"
        }
        body = {
            "model": self.ctx.llm_model_name,
            "messages": messages,
            "tools": self.registry.get_schemas()
        }
        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(url, headers=headers, json=body)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            sys.stderr.write(f"Ошибка связи с LLM: {e}\n")
            sys.exit(1)

    def process_query(self, user_input: str) -> Dict[str, Any]:
        """Запускает цикл обработки вопроса и возвращает итоговый ответ."""
        self.ctx.conversation_history = [
            {"role": "system", "content": self.SYSTEM_MESSAGE},
            {"role": "user", "content": user_input}
        ]
        self.ctx.action_records.clear()
        final_answer = ""
        round_num = 0

        while round_num < self.ctx.max_action_rounds:
            round_num += 1
            sys.stderr.write(f"--- Раунд {round_num} ---\n")

            llm_response = self._call_llm(self.ctx.conversation_history)
            choice = llm_response["choices"][0]
            msg = choice["message"]

            if "tool_calls" in msg and msg["tool_calls"]:
                for call in msg["tool_calls"]:
                    func = call.get("function", {})
                    name = func.get("name")
                    raw_args = func.get("arguments", "{}")
                    try:
                        args = json.loads(raw_args)
                    except json.JSONDecodeError:
                        args = {}
                    sys.stderr.write(f"Вызов действия: {name} с аргументами {args}\n")
                    result = self.registry.execute(name, args)
                    self.ctx.action_records.append({
                        "tool": name,
                        "args": args,
                        "result": result
                    })
                    # Добавляем результат как сообщение от пользователя (Qwen-совместимый формат)
                    self.ctx.conversation_history.append({
                        "role": "user",
                        "content": f"[Результат {name}]: {result}"
                    })
            else:
                final_answer = msg.get("content", "")
                sys.stderr.write("Получен финальный ответ.\n")
                break
        else:
            sys.stderr.write("Достигнут лимит раундов.\n")
            if not final_answer:
                final_answer = "Не удалось получить ответ в отведённое время."

        # Извлекаем источник (wiki/…md) из ответа
        source = ""
        match = re.search(r"wiki/[\w\-]+\.md(?:#[\w\-]+)?", final_answer)
        if match:
            source = match.group()
        else:
            # если не нашли, берём последний прочитанный файл
            for rec in reversed(self.ctx.action_records):
                if rec["tool"] == "read_file" and not rec["result"].startswith("Ошибка"):
                    source = rec["args"].get("target", "")
                    break

        return {
            "answer": final_answer,
            "source": source,
            "tool_calls": self.ctx.action_records
        }


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("Использование: python agent.py \"Ваш вопрос\"\n")
        sys.exit(1)

    question = sys.argv[1]
    sys.stderr.write(f"Вопрос: {question}\n")

    ctx = ApplicationContext()
    registry = ActionRegistry(ctx)
    engine = DialogueEngine(ctx, registry)

    result = engine.process_query(question)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
