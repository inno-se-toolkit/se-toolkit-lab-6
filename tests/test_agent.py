#!/usr/bin/env python3
"""
Agent that calls LLM and returns JSON response.
"""
import os
import sys
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

# Настройка логирования в stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

def load_config() -> Dict[str, str]:
    """Load configuration from environment variables
    
    Returns:
        Dict[str, str]: Configuration dictionary with api_key, api_base, model
    """
    # Читаем напрямую из переменных окружения (как требует авточекер)
    config: Dict[str, Optional[str]] = {
        'api_key': os.environ.get('LLM_API_KEY'),
        'api_base': os.environ.get('LLM_API_BASE'),
        'model': os.environ.get('LLM_MODEL', 'qwen3-coder-plus')  # Значение по умолчанию допустимо
    }
    
    # Проверка наличия всех необходимых переменных
    missing = [k for k, v in config.items() if k != 'model' and not v]  # model может иметь дефолт
    if missing:
        logger.error(f"Missing required environment variables: {missing}")
        logger.error("Please set LLM_API_KEY, LLM_API_BASE, and optionally LLM_MODEL")
        sys.exit(1)
    
    # Преобразуем Optional[str] в str (после проверки на None)
    return {k: v for k, v in config.items() if v is not None}  # type: ignore

def call_llm(question: str, config: Dict[str, str]) -> str:
    """Call LLM with the question
    
    Args:
        question (str): User's question
        config (Dict[str, str]): Configuration with api_key, api_base, model
    
    Returns:
        str: LLM's answer
    """
    try:
        client = OpenAI(
            api_key=config['api_key'],
            base_url=config['api_base']
        )
        
        logger.info(f"Sending question to {config['model']}: {question[:50]}...")
        
        response = client.chat.completions.create(
            model=config['model'],
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Provide clear and concise answers."},
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        answer: str = response.choices[0].message.content
        logger.info(f"Received response ({len(answer)} chars)")
        return answer
        
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        sys.exit(1)

def format_response(answer: str) -> str:
    """Format response as JSON
    
    Args:
        answer (str): LLM's answer
    
    Returns:
        str: JSON string with answer and empty tool_calls
    """
    response_dict: Dict[str, Any] = {
        "answer": answer,
        "tool_calls": []
    }
    return json.dumps(response_dict, ensure_ascii=False)

def main() -> None:
    """Main entry point"""
    # Проверка аргументов
    if len(sys.argv) < 2:
        logger.error("Usage: uv run agent.py 'your question here'")
        sys.exit(1)
    
    question: str = sys.argv[1]
    
    # Загрузка конфигурации из переменных окружения
    config: Dict[str, str] = load_config()
    
    # Вызов LLM
    answer: str = call_llm(question, config)
    
    # Вывод результата в stdout (только JSON!)
    print(format_response(answer))
    
    logger.info("Done")

if __name__ == "__main__":
    main()