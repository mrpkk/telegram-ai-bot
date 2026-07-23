"""FastAPI приложение — основной сервер."""

import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import DB_PATH
from app.models import init_db
from app.admin import router as admin_router

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения."""
    # Startup
    log.info("Инициализация БД...")
    from models import DB_PATH as db_path
    import models
    models.DB_PATH = DB_PATH
    init_db()
    log.info("БД готова")

    # Запускаем Telegram-бота в отдельном потоке
    from bot.main import run_bot
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    log.info("Telegram-бот запущен в фоне")

    yield

    # Shutdown
    log.info("Остановка сервера...")


app = FastAPI(
    title="Telegram AI Bot API",
    description="RAG-система для Telegram-бота с Mistral AI",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем админ API
app.include_router(admin_router)


@app.get("/health")
async def health():
    """Проверка статуса."""
    return {"status": "ok", "service": "telegram-ai-bot"}


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {
        "name": "Telegram AI Bot",
        "version": "1.0.0",
        "docs": "/docs",
        "admin": "/admin",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
