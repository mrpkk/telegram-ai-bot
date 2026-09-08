"""Конфигурация приложения.

Приоритет цепочки LLM-провайдеров:
  1. GigaChat (Сбер) — GigaChat-Max, freemium, работает из РФ напрямую
  2. Mistral AI — mistral-small-latest (бесплатно), fallback

GigaChat-ключи (GIGACHAT_AUTH_KEY, GIGACHAT_SCOPE) лежат в ~/.env (мастер-файл),
остальной конфиг — в локальном .env проекта.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Сначала ~/.env (мастер-файл ключей) — с override, чтобы перекрыть устаревшие
load_dotenv(os.path.expanduser("~/.env"), override=True)
# Затем локальный .env проекта — только недостающие переменные
load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ADMIN_IDS = [int(x) for x in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",") if x.strip()]

# AI Models — цепочка: GigaChat (Сбер) → Mistral AI (fallback)
# GigaChat (первичный провайдер, ключ из ~/.env)
GIGACHAT_AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY", "")
GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
GIGACHAT_BASE_URL = os.getenv("GIGACHAT_BASE_URL", "https://gigachat.devices.sberbank.ru/api/v1/chat/completions")
GIGACHAT_OAUTH_URL = os.getenv("GIGACHAT_OAUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
GIGACHAT_MODEL = os.getenv("GIGACHAT_MODEL", "GigaChat-Max")
# Mistral AI (fallback)
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_API_URL = os.getenv("MISTRAL_API_URL", "https://api.mistral.ai/v1/chat/completions")
MISTRAL_EMBED_URL = os.getenv("MISTRAL_EMBED_URL", "https://api.mistral.ai/v1/embeddings")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "mistral-small-latest")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "mistral-embed")

# Database
DB_PATH = Path(os.getenv("DB_PATH", "./data/bot.db"))
CHROMA_PATH = Path(os.getenv("CHROMA_PATH", "./chroma_db"))
DOCUMENTS_PATH = Path(os.getenv("DOCUMENTS_PATH", "./data/documents"))

# Admin Panel
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")

# Support
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@company.com")
SUPPORT_PHONE = os.getenv("SUPPORT_PHONE", "+79001234567")
COMPANY_NAME = os.getenv("COMPANY_NAME", "Моя Компания")

# System Prompt
DEFAULT_SYSTEM_PROMPT = f"""Ты — AI-ассистент компании "{COMPANY_NAME}". Ты помогаешь клиентам с вопросами о продуктах и услугах.

Правила:
1. Отвечай ТОЛЬКО на основе предоставленных документов
2. Если информации нет — скажи: "Я не нашёл ответ в базе знаний. Напишите нам на {SUPPORT_EMAIL}"
3. Всегда указывай источник документа
4. Тон: дружелюбный, профессиональный, краткий (не более 3 абзацев)
5. Не выдумывай факты, не используй стороннюю информацию
6. Если пользователь просит контакты — давай их сразу"""

# Paths
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
CHROMA_PATH.mkdir(parents=True, exist_ok=True)
DOCUMENTS_PATH.mkdir(parents=True, exist_ok=True)
