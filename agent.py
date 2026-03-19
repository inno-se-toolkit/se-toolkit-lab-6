import json
import sys
from typing import Any

import httpx
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_api_key: str
    llm_api_base: str
    llm_model: str

    model_config = SettingsConfigDict(
        env_file=".env.agent.secret",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class AgentOutput(BaseModel):
    answer: str
    tool_calls: list[dict[str, Any]]


def _parse_question(argv: list[str]) -> str:
    if len(argv) < 2:
        print("Usage: uv run agent.py \"<question>\"", file=sys.stderr)
        sys.exit(1)

    question = argv[1].strip()
    if not question:
        print("Question must not be empty.", file=sys.stderr)
        sys.exit(1)

    return question


def _build_url(base_url: str) -> str:
    return base_url.rstrip("/") + "/chat/completions"


def _query_llm(question: str, settings: Settings) -> str:
    payload = {
        "model": settings.llm_model,
        "max_tokens": 64,
        "messages": [
            {
                "role": "system",
                "content": "Answer the user's question in one short sentence.",
            },
            {"role": "user", "content": question},
        ],
    }

    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = httpx.post(
            _build_url(settings.llm_api_base),
            headers=headers,
            json=payload,
            timeout=60.0,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        print(f"LLM API returned {error.response.status_code}: {error.response.text}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as error:
        print(f"Cannot reach LLM API: {error}", file=sys.stderr)
        sys.exit(1)

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, ValueError) as error:
        print(f"Invalid LLM response format: {error}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    question = _parse_question(sys.argv)

    try:
        settings = Settings()
    except Exception as error:
        print(f"Invalid LLM configuration: {error}", file=sys.stderr)
        sys.exit(1)

    answer = _query_llm(question, settings)
    output = AgentOutput(answer=answer, tool_calls=[])
    print(output.model_dump_json())


if __name__ == "__main__":
    main()
