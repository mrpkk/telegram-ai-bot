"""RAG сервис — вызов LLM через цепочку провайдеров с авто-fallback.

Приоритет цепочки:
  1. GigaChat (Сбер) — GigaChat-Max, freemium, работает из РФ напрямую
  2. Mistral AI — mistral-small-latest (бесплатно), fallback

GigaChat-ключи (GIGACHAT_AUTH_KEY, GIGACHAT_SCOPE) читаются из ~/.env (мастер-файл),
access_token кэшируется до expires_in.
"""
import os
import time
import logging
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# ~/.env — мастер-файл ключей (GigaChat и др.) — с override; локальный .env — только дополняет
load_dotenv(os.path.expanduser("~/.env"), override=True)
load_dotenv()

log = logging.getLogger("app.services.rag")

# ── Mistral AI (fallback №2) ──────────────────────────────────────────
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_API_URL = os.getenv("MISTRAL_API_URL", "https://api.mistral.ai/v1/chat/completions")
MISTRAL_MODEL = os.getenv("DEFAULT_MODEL", "mistral-small-latest")

# ── GigaChat (Сбер, первичный провайдер) ──────────────────────────────
GIGACHAT_AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY", "")
GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
GIGACHAT_BASE_URL = os.getenv("GIGACHAT_BASE_URL", "https://gigachat.devices.sberbank.ru/api/v1/chat/completions")
GIGACHAT_OAUTH_URL = os.getenv("GIGACHAT_OAUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
GIGACHAT_MODEL = os.getenv("GIGACHAT_MODEL", "GigaChat-Max")

# Диагностика: какой провайдер/модель ответили последним
last_provider: Optional[str] = None
last_model: Optional[str] = None
last_error: Optional[str] = None

# Кэш access_token GigaChat (expires_in ~ 30 мин; запас 60с на десинхронизацию часов)
_giga_token_cache = {"token": None, "expires_at": 0.0}


async def _giga_access_token() -> Optional[str]:
    """OAuth-токен GigaChat (Authorization: Basic <ключ>, данные scope, заголовок RqUID)."""
    now = time.time()
    if _giga_token_cache["token"] and _giga_token_cache["expires_at"] > now + 60:
        return _giga_token_cache["token"]
    try:
        async with httpx.AsyncClient(timeout=20, verify=False) as client:
            resp = await client.post(
                GIGACHAT_OAUTH_URL,
                data={"scope": GIGACHAT_SCOPE},
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "RqUID": "6f0b1291-c7f3-43c6-bb2e-9f3efb2dc98e",
                    "Authorization": f"Basic {GIGACHAT_AUTH_KEY}",
                },
            )
        if resp.status_code >= 400:
            log.warning("gigachat/auth: %s — %s", resp.status_code, resp.text[:200])
            return None
        data = resp.json()
        token = data.get("access_token")
        expires_in = data.get("expires_in", 1800)
        if token:
            _giga_token_cache["token"] = token
            _giga_token_cache["expires_at"] = now + expires_in - 60
            return token
    except Exception as e:
        log.warning("gigachat/auth error: %s", e)
    return None


async def _ask_giga(system_prompt: str, prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
    """Запрос к GigaChat (self-signed сертификаты → verify=False)."""
    token = await _giga_access_token()
    if not token:
        return ""
    async with httpx.AsyncClient(timeout=60, verify=False) as client:
        resp = await client.post(
            GIGACHAT_BASE_URL,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "model": GIGACHAT_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
    if resp.status_code != 200:
        log.warning("gigachat: %s — %s", resp.status_code, resp.text[:200])
        return ""
    return resp.json()["choices"][0]["message"]["content"]


async def ask_llm(prompt: str, language: str = "ru", max_tokens: int = 4000, temperature: float = 0.7) -> str:
    """Вызов LLM по цепочке: GigaChat → Mistral. Возвращает текст ответа.

    Провайдер последнего успешного вызова виден через модульные
    переменные last_provider / last_model (для диагностики).
    """
    global last_provider, last_model, last_error
    lang_instruction = f"Отвечай на {language} языке." if language != "en" else "Answer in English."
    system_prompt = f"{lang_instruction} Ты — полезный AI-ассистент. Отвечай кратко и по делу."

    # ── 1. GigaChat (Сбер) — первичный провайдер ──
    if GIGACHAT_AUTH_KEY:
        try:
            text = await _ask_giga(system_prompt, prompt, max_tokens, temperature)
            if text:
                last_provider, last_model = "gigachat", GIGACHAT_MODEL
                return text
            log.warning("GigaChat вернул пустой ответ — переключаюсь на Mistral")
        except Exception as e:
            last_error = f"gigachat: {e}"
            log.warning("GigaChat failed: %s — fallback Mistral", e)
    else:
        log.warning("GIGACHAT_AUTH_KEY не задан — пропускаю GigaChat")

    # ── 2. Mistral AI — fallback ──
    if not MISTRAL_API_KEY:
        raise RuntimeError("Нет API-ключа Mistral (MISTRAL_API_KEY)")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                MISTRAL_API_URL,
                headers={
                    "Authorization": f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": MISTRAL_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        last_provider, last_model = "mistral", MISTRAL_MODEL
        return text
    except Exception as e:
        last_error = f"mistral: {e}"
        raise RuntimeError(f"Все LLM-провайдеры недоступны: {last_error}") from e


async def ask_mistral(prompt: str, language: str = "ru") -> str:
    """Прямой вызов LLM (GigaChat первичен, Mistral — fallback). Совместимость с bot/main.py."""
    return await ask_llm(prompt, language)


async def ask_rag(question: str, language: str = "ru",
                  user_id: Optional[int] = None,
                  db: Optional[Session] = None) -> str:
    """Ответ на вопрос через LLM (GigaChat → Mistral)."""
    return await ask_llm(question, language)