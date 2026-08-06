"""Telegram-бот с AI ядром и поддержкой Tor SOCKS5."""
import asyncio
import logging
import os
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

from app.core.config import TELEGRAM_BOT_TOKEN, ADMIN_IDS
from app.core.database import Base, engine
from app.services.rag import ask_mistral

log = logging.getLogger("bot")

# Создаём таблицы
Base.metadata.create_all(bind=engine)

# SOCKS5 прокси через Tor (для обхода блокировок Telegram в РФ)
PROXY = os.getenv("TG_PROXY", "socks5h://127.0.0.1:9050")
_socks_proxy = PROXY.replace("socks5h://", "socks5://") if PROXY.startswith("socks5h://") else PROXY
session = AiohttpSession(proxy=_socks_proxy)
bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    session=session,
)
dp = Dispatcher(storage=MemoryStorage())


# ── Кнопки ─────────────────────────────────────────────────────────────

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Постоянное меню внизу чата."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Возможности"), KeyboardButton(text="💎 Тарифы")],
            [KeyboardButton(text="ℹ️ О боте"), KeyboardButton(text="❓ Помощь")],
            [KeyboardButton(text="🎲 Пример вопроса")],
        ],
        resize_keyboard=True,
    )


def bot_links_keyboard() -> InlineKeyboardMarkup:
    """Инлайн-кнопки: бот, API, разработчик."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✈️ Открыть бота", url="https://t.me/TgBotAiQ_bot"),
                InlineKeyboardButton(text="📖 API (Swagger)", url="https://t.me/TgBotAiQ_bot"),
            ],
            [
                InlineKeyboardButton(text="👨‍💻 Разработчик", url="https://t.me/mrpkk"),
            ],
        ]
    )


# Примеры вопросов для кнопки «🎲 Пример вопроса»
EXAMPLE_QUESTIONS = [
    "Что такое RAG и как он работает?",
    "Напиши краткий план запуска стартапа",
    "Как настроить корпоративный Telegram-бот?",
    "Объясни простыми словами, что такое блокчейн",
    "Составь шаблон договора оказания услуг",
]


# Шпаргалка для владельца: типичные вопросы заказчика и ответы на демо
DEMO_CHEATSHEET = """🎭 <b>ПАСХАЛОЧКА · демо-шпаргалка</b>

❓ <b>«Это точно работает без вашего присутствия?»</b>
✅ Сервер работает 24/7 (systemd-сервис), бот и API подняты. Панель мониторинга показывает живые метрики.

❓ <b>«Какая модель ИИ?»</b>
✅ Mistral AI (французская, GDPR-friendly). Бесплатный тариф — 500k запросов/мин, поэтому нет затрат на демо. При росте — платные модели.

❓ <b>«А если упадёт?»</b>
✅ Автоперезапуск (systemd Restart=on-failure) + резервные копии БД каждые 2 часа + ежедневно.

❓ <b>«Где данные?»</b>
✅ Своя БД (SQLite) + документы хранятся у нас. Внешние сервисы не получают ваши документы.

❓ <b>«Как масштабировать?»</b>
✅ API готов: подключается к любому сайту/CRM. Бот в Telegram бесплатен и не требует приложения.

❓ <b>«Почему в демо нет платежей?»</b>
✅ Модуль готов (Stripe), но для продакшена нужны ключи платёжной системы. Показываю на тестовых данных — интеграция за 1 день.

❓ <b>«Excel-отчёты?»</b>
✅ Экспорт CSV/Excel готов — показываю прямо сейчас.

❓ <b>«Операторский колл-центр?»</b>
✅ В текущей версии — журнал обращений с оценкой качества. Полноценная очередь тикетов — доработка 2-3 дня.

❓ <b>«Сколько стоит доработка?»</b>
✅ Зависит от объёма — назовите задачу, дам оценку в течение дня.

❓ <b>«Кто это написал?»</b>
✅ Я архитектор и владелец. Код пишу с использованием AI-инструментов — это ускоряет разработку. Отвечаю за каждую часть системы."""


@dp.message(Command("demo"))
async def cmd_demo(message: types.Message):
    """Секретная шпаргалка для владельца (только для админов)."""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Команда доступна только владельцу.")
        return
    await message.answer(DEMO_CHEATSHEET)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Приветствие."""
    text = (
        "🤖 <b>AI Business Assistant</b>\n\n"
        "Привет! Я корпоративный AI-ассистент на базе <b>Mistral AI</b>.\n\n"
        "🧠 <b>Мои возможности:</b>\n"
        "• Отвечаю на вопросы по вашим документам (RAG)\n"
        "• Анализирую договоры, статьи, отчёты\n"
        "• Помогаю с кодом, переводами, текстами\n"
        "• Работаю 24/7 без выходных\n\n"
        "📌 <b>Попробуй:</b>\n"
        "/ask <i>твой вопрос</i> — задать вопрос\n"
        "/features — все возможности\n"
        "/pricing — тарифы\n\n"
        "<i>Или просто напиши мне что-нибудь!</i>"
    )
    await message.answer(text, reply_markup=main_menu_keyboard())


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Помощь."""
    text = (
        "📋 <b>Помощь</b>\n\n"
        "<b>/start</b> — запустить\n"
        "<b>/ask</b> <i>вопрос</i> — задать вопрос\n"
        "<b>/features</b> — все возможности\n"
        "<b>/pricing</b> — тарифы\n"
        "<b>/about</b> — о боте\n\n"
        "<b>💡 Совет:</b>\n"
        "Просто напиши мне в чат — я отвечу как AI-ассистент.\n"
        "Если вопрос сложный — используй /ask\n\n"
        "Пример: <i>/ask Что такое RAG и как он работает?</i>"
    )
    await message.answer(text, reply_markup=main_menu_keyboard())


@dp.message(Command("features"))
async def cmd_features(message: types.Message):
    """Все возможности."""
    text = (
        "🚀 <b>AI Business Assistant — Возможности</b>\n\n"
        "🧠 <b>1. Умный AI-чат</b>\n"
        "Отвечаю на любые вопросы: бизнес, IT, маркетинг, право.\n"
        "База: Mistral AI (одна из мощнейших моделей).\n\n"
        "📚 <b>2. RAG — поиск по вашим документам</b>\n"
        "Загрузите PDF, DOCX, XLSX — и я отвечу ТОЛЬКО по ним.\n"
        "🔹 Юрист: загрузил договоры → спроси «какие штрафы?»\n"
        "🔹 Врач: загрузил протоколы → отвечаю по ним\n"
        "🔹 Бухгалтер: загрузил НК → консультирую\n\n"
        "🔗 <b>3. REST API</b>\n"
        "Можно подключить к вашему сайту, CRM или приложению.\n"
        "Swagger-документация: /api/docs\n\n"
        "🔒 <b>4. Приватность</b>\n"
        "Ваши документы не уходят третьим лицам.\n"
        "Всё обрабатывается локально.\n\n"
        "⚡ <b>5. 24/7 Доступность</b>\n"
        "Работаю без перерывов и выходных."
    )
    await message.answer(text, reply_markup=bot_links_keyboard())


@dp.message(Command("pricing"))
async def cmd_pricing(message: types.Message):
    """Тарифы."""
    text = (
        "💎 <b>Тарифы AI Business Assistant</b>\n\n"
        "🌱 <b>Базовый — Бесплатно</b>\n"
        "• AI-чат без ограничений\n"
        "• До 10 вопросов/день по документам\n"
        "• 1 загруженный документ\n\n"
        "🚀 <b>Бизнес — 500 ⭐ / мес</b>  (~500 RUB)\n"
        "• Всё из Базового\n"
        "• Безлимит вопросов по документам\n"
        "• До 50 документов в базе знаний\n"
        "• API доступ\n\n"
        "🏢 <b>Корпоративный — 1500 ⭐ / мес</b>\n"
        "• Всё из Бизнес\n"
        "• Неограничено документов\n"
        "• Выделенный AI (тонкая настройка)\n"
        "• Интеграция с вашей CRM\n"
        "• Приоритетная поддержка\n\n"
        "💳 Оплата через Telegram Stars (без комиссий)\n"
        "👨‍💻 По всем вопросам: @mrpkk"
    )
    await message.answer(text, disable_web_page_preview=True, reply_markup=bot_links_keyboard())


@dp.message(Command("about"))
async def cmd_about(message: types.Message):
    """О боте."""
    text = (
        "🤖 <b>AI Business Assistant</b>\n\n"
        "Версия: 2.0.0\n"
        "AI: Mistral AI (mistral-small-latest)\n"
        "Технологии: FastAPI + RAG (гибридный поиск)\n"
        "RAG: BM25 + Векторный поиск + AI\n"
        "Документы: PDF, DOCX, XLSX, TXT\n\n"
        "⚡ <b>Стек:</b>\n"
        "• Python 3.14 / FastAPI / aiogram 3.x\n"
        "• SQLite + SQLAlchemy\n"
        "• Mistral AI (500k req/min free)\n"
        "• SOCKS5 через Tor (безопасность)\n\n"
        "📅 Запущен: июль 2026\n\n"
        "👨‍💻 Разработчик: <a href='https://t.me/mrpkk'>@mrpkk</a>"
    )
    await message.answer(text, reply_markup=bot_links_keyboard())


@dp.message(Command("ask"))
async def cmd_ask(message: types.Message):
    """Ответ на вопрос через AI."""
    question = message.text.replace("/ask", "", 1).strip()
    if not question:
        text = (
            "❓ <b>Задай вопрос</b>\n\n"
            "Используй: <code>/ask твой вопрос</code>\n\n"
            "Примеры:\n"
            "• <code>/ask Что такое RAG?</code>\n"
            "• <code>/ask Напиши шаблон договора</code>\n"
            "• <code>/ask Как работает блокчейн?</code>"
        )
        await message.answer(text)
        return
    
    await message.answer("⏳ Анализирую ваш вопрос...")
    try:
        answer = await ask_mistral(question, "ru")
        await message.answer(f"🤖 <b>Ответ:</b>\n\n{answer}")
    except Exception as e:
        await message.answer(
            "❌ <b>Произошла ошибка</b>\n\n"
            f"<code>{str(e)}</code>\n\n"
            "Попробуй ещё раз или обратись к @mrpkk"
        )


@dp.message()
async def handle_message(message: types.Message):
    """Ответ на любое текстовое сообщение."""
    if not message.text or message.text.startswith("/"):
        return

    # Обработка нажатий кнопок главного меню
    menu_actions = {
        "🚀 Возможности": cmd_features,
        "💎 Тарифы": cmd_pricing,
        "ℹ️ О боте": cmd_about,
        "❓ Помощь": cmd_help,
    }
    if message.text in menu_actions:
        await menu_actions[message.text](message)
        return

    # Кнопка «🎲 Пример вопроса» — случайный вопрос из списка
    if message.text == "🎲 Пример вопроса":
        question = random.choice(EXAMPLE_QUESTIONS)
        await message.answer(f"🤖 <b>Вопрос:</b> {question}\n\n⏳ Думаю...")
        try:
            answer = await ask_mistral(question, "ru")
            await message.answer(f"🤖 {answer}")
        except Exception as e:
            await message.answer(
                "❌ <b>Ошибка обработки</b>\n\n"
                f"<code>{str(e)}</code>\n\n"
                "Попробуй написать /ask с твоим вопросом"
            )
        return

    # Маленькая "фишка" — приветствие по-разному
    greeting_words = ["привет", "здравствуй", "hello", "hi", "дарова", "сап", "ку"]
    is_greeting = any(message.text.lower().startswith(w) for w in greeting_words)
    
    if is_greeting:
        await message.answer(
            "👋 Привет! Я AI Business Assistant.\n"
            "Спрашивай что угодно — я онлайн!\n"
            "Или напиши /features чтобы узнать мои возможности."
        )
        return
    
    await message.answer("⏳ Думаю...")
    try:
        answer = await ask_mistral(message.text, "ru")
        # Telegram ограничение — 4096 символов
        if len(answer) > 4000:
            answer = answer[:4000] + "\n\n<i>...продолжение в /ask</i>"
        await message.answer(f"🤖 {answer}")
    except Exception as e:
        await message.answer(
            "❌ <b>Ошибка обработки</b>\n\n"
            f"<code>{str(e)}</code>\n\n"
            "Попробуй написать /ask с твоим вопросом"
        )


async def run_bot():
    """Запуск бота (неблокирующий)."""
    log.info("Telegram-бот запускается через SOCKS5 (Tor)...")
    retries = 3
    for attempt in range(retries):
        try:
            me = await bot.get_me()
            log.info(f"✅ Бот @{me.username} авторизован")
            break
        except Exception as e:
            log.warning(f"Попытка {attempt+1}/{retries} не удалась: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(10)
    else:
        log.error("❌ Не удалось подключиться к Telegram после 3 попыток")
        log.info("Бот будет работать в офлайн-режиме (только API)")
        return
    await dp.start_polling(bot)
