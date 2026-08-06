"""RAG сервис — прямой вызов Mistral AI, без llama_index (чтобы избежать конфликтов)."""
import os
from typing import Optional
from pathlib import Path
from sqlalchemy.orm import Session
from httpx import AsyncClient

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_API_URL = os.getenv("MISTRAL_API_URL", "https://api.mistral.ai/v1/chat/completions")


async def ask_mistral(prompt: str, language: str = "ru") -> str:
    """Прямой вызов Mistral AI."""
    lang_instruction = f"Отвечай на {language} языке." if language != "en" else "Answer in English."
    
    async with AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            MISTRAL_API_URL,
            headers={
                "Authorization": f"Bearer {MISTRAL_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistral-small-latest",
                "messages": [
                    {"role": "system", "content": f"{lang_instruction} Ты — полезный AI-ассистент. Отвечай кратко и по делу."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
        )
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def ask_rag(question: str, language: str = "ru",
                  user_id: Optional[int] = None,
                  db: Optional[Session] = None) -> str:
    """Ответ на вопрос через Mistral AI."""
    result = await ask_mistral(question, language)
    return result
