"""FastAPI приложение — основной сервер."""

import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.config import DB_PATH
from app.models import init_db

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")


def _ensure_admin_tables():
    """Создание таблиц админки (documents, faq, logs), если их ещё нет."""
    import sqlite3
    from app.config import DB_PATH
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_path TEXT,
            file_type TEXT,
            file_size INTEGER,
            chunks_count INTEGER DEFAULT 0,
            tags TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS faq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question TEXT,
            answer TEXT,
            response_time_ms REAL DEFAULT 0,
            source TEXT DEFAULT 'ai',
            is_helpful INTEGER,
            command TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        conn.close()
        log.info("Таблицы админки готовы (documents, faq, logs)")
    except Exception as e:
        log.warning(f"Не удалось создать таблицы админки: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения."""
    # Startup
    log.info("Инициализация БД...")
    init_db()
    log.info("БД готова")
    _ensure_admin_tables()

    # Запускаем Telegram-бота фоновой задачей
    from bot.main import run_bot
    bot_task = asyncio.create_task(run_bot())
    log.info("Telegram-бот запущен в фоне")

    try:
        yield
    finally:
        # Shutdown
        if hasattr(bot_task, 'cancel'):
            bot_task.cancel()
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

# API v1
from app.api.v1 import api_router
app.include_router(api_router, prefix="/api/v1")

# Админ-API
from app.admin import router as admin_router
app.include_router(admin_router, prefix="/api/v1")


@app.get("/health")
async def health():
    """Проверка статуса."""
    return {"status": "ok", "service": "telegram-ai-bot"}


HTML_ROOT = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🤖 Telegram AI Bot</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; background:#0a0e14; color:#e6edf3; }
  .hero { text-align:center; padding:80px 24px 50px; background:radial-gradient(ellipse at 50% 0%, rgba(56,139,253,0.12) 0%, transparent 60%); }
  .hero h1 { font-size:2.8rem; font-weight:700; background:linear-gradient(135deg,#f0f6fc,#58a6ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
  .hero p { color:#8b949e; margin-top:10px; font-size:1.1rem; max-width:500px; margin-left:auto; margin-right:auto; }
  .badge { display:inline-block; background:rgba(56,139,253,0.1); color:#58a6ff; padding:4px 16px; border-radius:100px; font-size:0.8rem; border:1px solid rgba(56,139,253,0.15); margin-top:14px; }
  .grid { max-width:900px; margin:0 auto; padding:40px 24px; display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:16px; }
  .card { background:linear-gradient(135deg,#0d1117,#161b22); border:1px solid #21262d; border-radius:16px; padding:24px; transition:all 0.25s; }
  .card:hover { border-color:#58a6ff; transform:translateY(-2px); box-shadow:0 8px 30px rgba(0,0,0,0.4); }
  .card h3 { font-size:1.1rem; margin-bottom:6px; }
  .card p { color:#8b949e; font-size:0.85rem; line-height:1.5; }
  .btn { display:inline-block; margin-top:12px; padding:10px 24px; border-radius:10px; text-decoration:none; font-weight:600; font-size:0.9rem; transition:all 0.2s; }
  .btn-primary { background:linear-gradient(135deg,#238636,#2ea043); color:#fff; }
  .btn-primary:hover { transform:translateY(-2px); box-shadow:0 8px 30px rgba(46,160,67,0.3); }
  .btn-secondary { background:rgba(56,139,253,0.1); color:#58a6ff; border:1px solid rgba(56,139,253,0.2); }
  .btn-secondary:hover { background:rgba(56,139,253,0.2); }
  .btn-bot { background:rgba(45,164,78,0.1); color:#3fb950; border:1px solid rgba(45,164,78,0.2); }
  .btn-bot:hover { background:rgba(45,164,78,0.2); }
  .links { display:flex; flex-wrap:wrap; gap:10px; justify-content:center; margin-top:20px; }
  .how { max-width:900px; margin:0 auto; padding:40px 24px; }
  .how h2 { text-align:center; margin-bottom:24px; color:#f0f6fc; }
  .step { display:flex; gap:16px; margin-bottom:16px; background:#0d1117; border:1px solid #21262d; border-radius:12px; padding:16px 20px; }
  .step-num { width:36px; height:36px; border-radius:50%; background:linear-gradient(135deg,#58a6ff,#a371f7); display:flex; align-items:center; justify-content:center; font-weight:700; font-size:0.9rem; flex-shrink:0; }
  .step-content { flex:1; }
  .step-content h4 { font-size:0.95rem; color:#f0f6fc; }
  .step-content p { color:#8b949e; font-size:0.8rem; margin-top:2px; }
  .step code { color:#58a6ff; font-size:0.75rem; font-family:monospace; }
  .tech { max-width:900px; margin:0 auto; padding:40px 24px; display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:12px; }
  .tech-item { background:#0d1117; border:1px solid #21262d; border-radius:10px; padding:16px; text-align:center; }
  .tech-item h4 { font-size:0.9rem; color:#f0f6fc; }
  .tech-item p { color:#8b949e; font-size:0.78rem; margin-top:4px; }
  .cta { text-align:center; padding:60px 24px; background:radial-gradient(ellipse at center, rgba(56,139,253,0.06) 0%, transparent 70%); }
  .cta h2 { font-size:1.8rem; margin-bottom:8px; }
  .cta p { color:#8b949e; margin-bottom:20px; }
  footer { text-align:center; padding:30px; color:#484f58; font-size:0.8rem; }
  a { color:#58a6ff; text-decoration:none; }
</style>
</head>
<body>
<div class="hero">
  <h1>🤖 Telegram AI Bot</h1>
  <p>Корпоративный AI-ассистент. Mistral AI + RAG по вашим документам.</p>
  <div class="badge">@TgBotAiQ_bot · v1.0.0 · Работает 24/7</div>
  <div class="links">
    <a href="https://t.me/TgBotAiQ_bot" class="btn btn-bot">✈️ Открыть бота</a>
    <a href="/docs" class="btn btn-secondary">📖 Swagger API</a>
  </div>
</div>

<div class="how">
  <h2>🚀 Как это работает</h2>
  <div class="step">
    <div class="step-num">1</div>
    <div class="step-content">
      <h4>Напиши боту в Telegram</h4>
      <p>Открой <code>@TgBotAiQ_bot</code> и просто напиши вопрос — как в чате.</p>
    </div>
  </div>
  <div class="step">
    <div class="step-num">2</div>
    <div class="step-content">
      <h4>Мозг — Mistral AI</h4>
      <p>Запрос обрабатывает <strong>Mistral AI</strong> (500k req/min free). Мгновенно, качественно, на русском.</p>
    </div>
  </div>
  <div class="step">
    <div class="step-num">3</div>
    <div class="step-content">
      <h4>RAG по документам</h4>
      <p>Загрузи PDF, DOCX, XLSX — бот найдёт ответ прямо в твоих файлах. Гибридный поиск (BM25 + вектора).</p>
    </div>
  </div>
  <div class="step">
    <div class="step-num">4</div>
    <div class="step-content">
      <h4>REST API для интеграции</h4>
      <p>Любая CRM может подключиться через <code>/api/v1/ai/ask</code>. CORS разрешает любые запросы.</p>
    </div>
  </div>
</div>

<div class="tech">
  <div class="tech-item"><h4>🧠 Mistral AI</h4><p>Основная модель — быстрая, умная, бесплатная</p></div>
  <div class="tech-item"><h4>📚 RAG</h4><p>Поиск по документам: BM25 + векторные эмбеддинги</p></div>
  <div class="tech-item"><h4>🔌 REST API</h4><p>FastAPI + Swagger. Любая CRM может подключиться</p></div>
  <div class="tech-item"><h4>🔒 Приватность</h4><p>Всё локально. Данные не уходят на сторонние сервера</p></div>
  <div class="tech-item"><h4>🌐 Tor SOCKS5</h4><p>Telegram API через Tor — обход блокировок в РФ</p></div>
  <div class="tech-item"><h4>⚡ Асинхронно</h4><p>aiogram 3.x + asyncio — ответы без задержек</p></div>
</div>

<div class="cta">
  <h2>⚡ Попробуй прямо сейчас</h2>
  <p>Напиши @TgBotAiQ_bot — открыть без VPN</p>
  <a href="https://t.me/TgBotAiQ_bot" class="btn btn-primary">✈️ Открыть бота</a>
  <a href="/api/v1/ai/ask?query=Что ты умеешь?" class="btn btn-secondary" style="margin-left:10px;">🔍 Тест API</a>
</div>

<footer>Telegram AI Bot · <a href="/docs">Swagger</a> · <a href="https://t.me/mrpkk">@mrpkk</a></footer>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def root():
    """Корневой эндпоинт — красивая HTML-страница."""
    return HTML_ROOT


@app.get("/api/root.json")
async def root_json():
    """JSON-статус для API-клиентов."""
    return {
        "name": "Telegram AI Bot",
        "version": "1.0.0",
        "docs": "/docs",
        "admin": "/admin",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
