"""Конфигурация приложения."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ADMIN_IDS = [int(x) for x in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",") if x.strip()]

# AI Models (Mistral AI — бесплатно)
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
