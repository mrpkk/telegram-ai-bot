"""Telegram-бот с RAG."""

import logging
import time
from pathlib import Path

from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)

from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_IDS, COMPANY_NAME,
    SUPPORT_EMAIL, SUPPORT_PHONE, DEFAULT_SYSTEM_PROMPT
)
from models import get_db, UserCreate, LogCreate
from rag import RAGSystem, MistralLLM
from config import MISTRAL_API_KEY, DEFAULT_MODEL

log = logging.getLogger("bot")

# ── Глобальные объекты ────────────────────────────────────────────────

rag_system: RAGSystem = None
llm: MistralLLM = None


def init_bot():
    """Инициализация бота и RAG."""
    global rag_system, llm
    rag_system = RAGSystem()
    llm = MistralLLM(api_key=MISTRAL_API_KEY, model=DEFAULT_MODEL)
    log.info("Бот инициализирован")


# ── Клавиатуры ────────────────────────────────────────────────────────

def main_keyboard():
    """Основная клавиатура."""
    return ReplyKeyboardMarkup([
        [KeyboardButton("📝 Задать вопрос"), KeyboardButton("📚 База знаний")],
        [KeyboardButton("📞 Контакты"), KeyboardButton("ℹ️ Помощь")],
    ], resize_keyboard=True)


def helpful_keyboard(log_id: int):
    """Кнопки обратной связи."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👍 Полезно", callback_data=f"helpful_{log_id}_1"),
            InlineKeyboardButton("👎 Не полезно", callback_data=f"helpful_{log_id}_0"),
        ]
    ])


# ── Обработчики команд ────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start."""
    user = update.effective_user

    # Сохраняем пользователя
    db = get_db()
    try:
        db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, username, first_name) VALUES (?, ?, ?)",
            (user.id, user.username, user.first_name)
        )
        db.execute(
            "UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE telegram_id = ?",
            (user.id,)
        )
        db.commit()
    finally:
        db.close()

    welcome = f"""👋 Добро пожаловать в {COMPANY_NAME}!

Я — AI-ассистент, который знает всё о наших продуктах и услугах.

📌 Что я умею:
• Отвечать на вопросы 24/7
• Помогать с выбором товаров
• Консультировать по доставке и оплате
• Решать типовые проблемы

📝 Просто напиши свой вопрос — я постараюсь помочь!

⚠️ Если я не знаю ответа — передам ваш запрос менеджеру."""

    await update.message.reply_text(welcome, reply_markup=main_keyboard())


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help."""
    help_text = """ℹ️ Доступные команды:

📝 Задать вопрос — задайте любой вопрос
📚 База знаний — информация о документах
📞 Контакты — свяжитесь с нами
/feedback — форма обратной связи
/stats — статистика (только для админов)

Просто напишите вопрос текстом — я найду ответ!"""
    await update.message.reply_text(help_text, reply_markup=main_keyboard())


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stats (только для админов)."""
    if update.effective_user.id not in TELEGRAM_ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return

    db = get_db()
    try:
        users_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        questions_today = db.execute(
            "SELECT COUNT(*) FROM logs WHERE date(created_at) = date('now')"
        ).fetchone()[0]
        docs_count = db.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        faq_count = db.execute("SELECT COUNT(*) FROM faq WHERE is_active = 1").fetchone()[0]

        helpful = db.execute(
            "SELECT is_helpful, COUNT(*) FROM logs WHERE is_helpful IS NOT NULL GROUP BY is_helpful"
        ).fetchall()
        helpful_dict = {row[0]: row[1] for row in helpful}

        stats = f"""📊 Статистика бота:

👥 Пользователей: {users_count}
❓ Вопросов сегодня: {questions_today}
📄 Документов: {docs_count}
💬 FAQ: {faq_count}

👍 Полезных ответов: {helpful_dict.get(1, 0)}
👎 Не полезных: {helpful_dict.get(0, 0)}"""

        await update.message.reply_text(stats)
    finally:
        db.close()


# ── Обработчики сообщений ─────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений."""
    text = update.message.text.strip()
    user = update.effective_user

    if not text:
        return

    # Кнопки меню
    if text == "📚 База знаний":
        await handle_docs_list(update, context)
        return
    if text == "📞 Контакты":
        await handle_contacts(update, context)
        return
    if text in ("ℹ️ Помощь", "/help"):
        await cmd_help(update, context)
        return

    # Показываем "печатает..."
    await update.message.chat.send_action("typing")
    start_time = time.time()

    # Ищем в FAQ
    db = get_db()
    try:
        faq_row = db.execute(
            "SELECT answer FROM faq WHERE question = ? AND is_active = 1",
            (text,)
        ).fetchone()

        if faq_row:
            answer = faq_row["answer"]
            source = "FAQ"
        else:
            # RAG-поиск
            context_text = rag_system.get_context(text, k=4)
            answer = llm.generate(
                system_prompt=DEFAULT_SYSTEM_PROMPT,
                user_message=text,
                context=context_text
            )
            source = "AI + Documents"
    finally:
        db.close()

    response_time = int((time.time() - start_time) * 1000)

    # Сохраняем лог
    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO logs (user_id, question, answer, source, response_time_ms) VALUES (?, ?, ?, ?, ?)",
            (user.id, text, answer, source, response_time)
        )
        log_id = cursor.lastrowid
        db.commit()
    finally:
        db.close()

    # Формируем ответ
    response = f"📌 {answer}\n\n⏱️ Время ответа: {response_time}ms"

    await update.message.reply_text(
        response,
        reply_markup=helpful_keyboard(log_id),
        parse_mode=None
    )


async def handle_docs_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список документов."""
    db = get_db()
    try:
        docs = db.execute("SELECT filename, file_type, chunks_count, created_at FROM documents ORDER BY created_at DESC").fetchall()
        if not docs:
            await update.message.reply_text("📚 База знаний пуста. Добавьте документы через админ-панель.")
            return

        msg = "📚 Документы в базе знаний:\n\n"
        for doc in docs:
            msg += f"📄 {doc['filename']} ({doc['file_type']}) — {doc['chunks_count']} фрагментов\n"
        await update.message.reply_text(msg)
    finally:
        db.close()


async def handle_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Контакты."""
    contacts = f"""📞 Контакты {COMPANY_NAME}:

📧 Email: {SUPPORT_EMAIL}
📱 Телефон: {SUPPORT_PHONE}
💬 Telegram: @{COMPANY_NAME.lower().replace(' ', '_')}

⏰ Время работы: Пн-Пт, 9:00-18:00"""
    await update.message.reply_text(contacts)


# ── Обработка callback (кнопки) ────────────────────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на inline-кнопки."""
    query = update.callback_query
    data = query.data

    if data.startswith("helpful_"):
        parts = data.split("_")
        log_id = int(parts[1])
        is_helpful = int(parts[2])

        db = get_db()
        try:
            db.execute("UPDATE logs SET is_helpful = ? WHERE id = ?", (is_helpful, log_id))
            db.commit()
        finally:
            db.close()

        text = "✅ Спасибо за обратную связь!" if is_helpful else "😔 Жаль, что ответ не помог. Мы постараемся улучшить базу знаний."
        await query.answer(text)


# ── Запуск бота ────────────────────────────────────────────────────────

def run_bot():
    """Запуск Telegram-бота."""
    if not TELEGRAM_BOT_TOKEN:
        log.error("TELEGRAM_BOT_TOKEN не задан!")
        return

    init_bot()

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    log.info("Telegram-бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
