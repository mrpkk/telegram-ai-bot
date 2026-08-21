"""Telegram-бот с AI ядром и поддержкой Tor SOCKS5."""
import asyncio
from datetime import timedelta, timezone
import logging
import os
import random
import tempfile
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    FSInputFile,
)

from app.core.config import TELEGRAM_BOT_TOKEN, ADMIN_IDS
from app.core.database import Base, engine, SessionLocal
from app.models.billing import Subscription, QuestionLog
from app.services.stars_payments import (
    PLAN_DAYS, PLAN_STARS, PLANS_TEXT_RU, daily_limit_for,
    new_expiry, send_plan_invoice, subscription_active,
)
from app.services.rag import ask_mistral
from app.services.image import extract_text_from_image

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

# Лимит сообщения Telegram (4096) с запасом
MAX_MSG_LEN = 3800


# ── Утилиты ───────────────────────────────────────────────────────────

def split_long_text(text: str, limit: int = MAX_MSG_LEN) -> list[str]:
    """Разбивает длинный текст на части по границам абзацев, не рвёт слова."""
    text = text.strip()
    if len(text) <= limit:
        return [text]

    parts: list[str] = []
    # Сначала пытаемся резать по абзацам
    paragraphs = text.split("\n\n")
    buf = ""
    for p in paragraphs:
        if len(p) > limit:
            # Очень длинный абзац — режем по предложениям/символам
            if buf:
                parts.append(buf.strip())
                buf = ""
            for chunk in _split_by_chars(p, limit):
                parts.append(chunk)
            continue
        if len(buf) + len(p) + 2 > limit:
            parts.append(buf.strip())
            buf = p
        else:
            buf = (buf + "\n\n" + p) if buf else p
    if buf.strip():
        parts.append(buf.strip())
    return parts


def _split_by_chars(text: str, limit: int) -> list[str]:
    """Режет длинный кусок по ~limit символов, стараясь не рвать предложения."""
    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + limit, n)
        if end < n:
            # откатываемся к ближайшей точке/концу предложения/пробелу
            for sep in (". ", "! ", "? ", "\n", " ", ", "):
                idx = text.rfind(sep, start + limit // 2, end)
                if idx != -1:
                    end = idx + len(sep)
                    break
        chunks.append(text[start:end].strip())
        start = end
    return [c for c in chunks if c]


async def send_long(message: types.Message, text: str, reply_markup=None):
    """Отправляет текст, разбивая на несколько сообщений если нужно."""
    parts = split_long_text(text)
    for i, part in enumerate(parts):
        if i == len(parts) - 1:
            await message.answer(part, reply_markup=reply_markup)
        else:
            await message.answer(part)
        # небольшая пауза между сообщениями, чтобы не упереться в rate limit
        if i < len(parts) - 1:
            await asyncio.sleep(0.4)


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
    """Инлайн-кнопки: API, разработчик."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📖 API (документация)", callback_data="api_info"),
                InlineKeyboardButton(text="👨‍💻 Разработчик", callback_data="dev_contact"),
            ],
            [
                InlineKeyboardButton(text="📜 Пример договора", callback_data="contract_sample"),
                InlineKeyboardButton(text="🌐 Балансы сетей", callback_data="chain_balances"),
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


# ── Callback-обработчики (кнопки) ─────────────────────────────────────

@dp.callback_query(F.data == "api_info")
async def cb_api_info(callback: types.CallbackQuery):
    """Информация об API (Swagger доступен только локально — показываем описание)."""
    text = (
        "📖 <b>REST API</b>\n\n"
        "Бот работает на базе полноценного API-сервера. "
        "Подключается к вашему сайту, CRM или приложению.\n\n"
        "🔹 <code>POST /api/v1/ai/ask</code> — AI-ответ на вопрос\n"
        "🔹 <code>POST /api/v1/image/ocr</code> — распознавание текста с фото\n"
        "🔹 <code>GET /api/v1/blockchains/.../balance/&lt;адрес&gt;</code> — балансы 6 сетей\n"
        "🔹 <code>GET /api/v1/agents/risk/var</code> — расчёт риска (VaR)\n"
        "🔹 <code>GET /api/v1/agents/risk/stress-test</code> — стресс-тест\n"
        "🔹 <code>POST /api/v1/agents/yield/optimize</code> — DeFi-доходность\n"
        "🔹 <code>/admin/*</code> — загрузка документов, FAQ, статистика, экспорт\n\n"
        "📘 Swagger-документация доступна по запросу (или на демо покажу на экране)."
    )
    await callback.message.answer(text)
    await callback.answer()


@dp.callback_query(F.data == "dev_contact")
async def cb_dev_contact(callback: types.CallbackQuery):
    """Контакты разработчика."""
    text = (
        "👨‍💻 <b>Разработчик</b>\n\n"
        "Максим — архитектор и владелец проекта.\n\n"
        "📩 Telegram: <a href='https://t.me/mrpkk'>@mrpkk</a>\n"
        "💼 Портфолио: <a href='https://github.com/mrpkk'>github.com/mrpkk</a>\n\n"
        "Напишите мне — отвечаю быстро."
    )
    await callback.message.answer(text, disable_web_page_preview=True)
    await callback.answer()


@dp.callback_query(F.data == "contract_sample")
async def cb_contract_sample(callback: types.CallbackQuery):
    """Генерация шаблона договора (демонстрация длинных ответов)."""
    await callback.message.answer("⏳ Готовлю шаблон договора...")
    try:
        answer = await ask_mistral(
            "Составь полный шаблон договора оказания услуг (исполнитель — разработчик, "
            "заказчик — клиент). Включи все разделы: предмет договора, сроки, стоимость и порядок "
            "оплаты, права и обязанности сторон, ответственность, конфиденциальность, "
            "расторжение, реквизиты. Не сокращай — напиши договор целиком.",
            "ru",
        )
        await send_long(callback.message, f"🤖 <b>Шаблон договора:</b>\n\n{answer}")
    except Exception as e:
        await callback.message.answer(
            "❌ <b>Ошибка обработки</b>\n\n"
            f"<code>{str(e)}</code>\n\n"
            "Попробуй ещё раз."
        )
    await callback.answer()


@dp.callback_query(F.data == "chain_balances")
async def cb_chain_balances(callback: types.CallbackQuery):
    """Подсказка по команде балансов."""
    text = (
        "🌐 <b>Балансы в блокчейн-сетях</b>\n\n"
        "Проверяю балансы в 6 сетях:\n"
        "• Ethereum\n• Solana\n• TON\n• Cosmos\n• Sui\n• Aptos\n\n"
        "Используй команду:\n"
        "<code>/balance 0x1234...abc</code> — баланс Ethereum\n"
        "<code>/balance SOL 9x...xyz</code> — баланс Solana\n"
        "<code>/balance TON UQ...abc</code> — баланс TON\n\n"
        "Сети определяются автоматически по формату адреса."
    )
    await callback.message.answer(text)
    await callback.answer()


# ── Команды ────────────────────────────────────────────────────────────

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
        "• Распознаю текст с фотографий (OCR)\n"
        "• Проверяю балансы в 6 блокчейн-сетях\n"
        "• Помогаю с кодом, переводами, текстами\n"
        "• Работаю 24/7 без выходных\n\n"
        "📌 <b>Попробуй:</b>\n"
        "/ask <i>твой вопрос</i> — задать вопрос\n"
        "/balance <i>адрес</i> — баланс в сети\n"
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
        "<b>/balance</b> <i>адрес</i> — баланс в сети\n"
        "<b>/risk</b> <i>сумма</i> — стресс-тест портфеля\n"
        "<b>/yield</b> <i>сеть</i> — DeFi-доходность\n"
        "<b>/features</b> — все возможности\n"
        "<b>/pricing</b> — тарифы\n"
        "<b>/about</b> — о боте\n\n"
        "💡 <b>Совет:</b>\n"
        "Просто напиши мне в чат — я отвечу как AI-ассистент.\n"
        "Отправь фото с текстом — распознаю его (OCR).\n\n"
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
        "📷 <b>3. OCR — распознавание текста с фото</b>\n"
        "Отправьте изображение — получу с него текст.\n\n"
        "🌐 <b>4. Блокчейн-модуль</b>\n"
        "Живые балансы в 6 сетях: ETH, SOL, TON, Cosmos, Sui, Aptos.\n"
        "/balance <i>адрес</i>\n\n"
        "📈 <b>5. Финансовые агенты</b>\n"
        "Расчёт риска (VaR), стресс-тесты, подбор DeFi-доходности.\n"
        "/risk <i>сумма</i> · /yield <i>сеть</i>\n\n"
        "🔗 <b>6. REST API</b>\n"
        "Можно подключить к вашему сайту, CRM или приложению.\n\n"
        "🔒 <b>7. Приватность</b>\n"
        "Ваши документы не уходят третьим лицам.\n"
        "Всё обрабатывается локально.\n\n"
        "⚡ <b>8. 24/7 Доступность</b>\n"
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
        "Версия: 2.1.0\n"
        "AI: Mistral AI (mistral-small-latest)\n"
        "Технологии: FastAPI + RAG (гибридный поиск)\n"
        "RAG: BM25 + Векторный поиск + AI\n"
        "Документы: PDF, DOCX, XLSX, TXT\n"
        "OCR: Tesseract (локально, без внешних сервисов)\n"
        "Блокчейн: ETH, SOL, TON, Cosmos, Sui, Aptos\n\n"
        "⚡ <b>Стек:</b>\n"
        "• Python 3.14 / FastAPI / aiogram 3.x\n"
        "• SQLite + SQLAlchemy\n"
        "• Mistral AI (500k req/min free)\n"
        "• SOCKS5 через Tor (безопасность)\n\n"
        "📅 Запущен: июль 2026\n\n"
        "👨‍💻 Разработчик: <a href='https://t.me/mrpkk'>@mrpkk</a>"
    )
    await message.answer(text, reply_markup=bot_links_keyboard())




# ── Монетизация: Telegram Stars ──────────────────────────────────────

def _now_utc():
    from datetime import datetime, timezone, timedelta
    return datetime.now(timezone.utc)


def _today():
    return _now_utc().strftime("%Y-%m-%d")


def get_active_subscription(telegram_id: int):
    db = SessionLocal()
    try:
        sub = db.query(Subscription).filter(
            Subscription.telegram_id == telegram_id).first()
        if sub and sub.expires_at.replace(tzinfo=timezone.utc) > _now_utc():
            return sub
        return None
    finally:
        db.close()


@dp.message(Command("subscribe"))
async def cmd_subscribe(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.insert(InlineKeyboardButton(f"Pro · {PLAN_STARS['pro']}⭐", callback_data="buy:pro"))
    kb.insert(InlineKeyboardButton(f"Enterprise · {PLAN_STARS['enterprise']}⭐", callback_data="buy:enterprise"))
    text = ("💎 <b>Тарифы</b>\n\n" + "\n".join(
        f"• {t}" for t in PLANS_TEXT_RU.values()) +
        "\n\nОплата — Telegram Stars. Выберите план:")
    await message.answer(text, reply_markup=kb)


@dp.callback_query(F.data.startswith("buy:"))
async def cb_buy(call: types.CallbackQuery):
    plan = call.data.split(":", 1)[1]
    if plan not in PLAN_STARS:
        await call.answer("Неизвестный тариф", show_alert=True); return
    await send_plan_invoice(bot, call.message.chat.id, plan)
    await call.answer()


@dp.pre_checkout_query_handler()
async def pre_checkout(q: types.PreCheckoutQuery):
    # payload вида subscribe:<plan>
    if not q.invoice_payload.startswith("subscribe:"):
        await q.answer(ok=False, error_message="Неизвестный товар")
        return
    await q.answer(ok=True)


@dp.message(F.successful_payment)
async def on_paid(message: types.Message):
    sp = message.successful_payment
    if not sp.invoice_payload.startswith("subscribe:"):
        return
    plan = sp.invoice_payload.split(":", 1)[1]
    db = SessionLocal()
    try:
        sub = db.query(Subscription).filter(
            Subscription.telegram_id == message.from_user.id).first()
        if sub is None:
            sub = Subscription(telegram_id=message.from_user.id, plan=plan)
            db.add(sub)
        else:
            # продление поверх активной подписки
            base = sub.expires_at.replace(tzinfo=timezone.utc)
            base = base if base > _now_utc() else _now_utc()
            sub.expires_at = base + timedelta(days=PLAN_DAYS[plan])
        sub.plan = plan
        sub.stars_paid = sp.total_amount
        if sub.starts_at is None or sub.plan != plan:
            sub.starts_at = func.now()
        if getattr(sub, "expires_at", None) is None or sub.expires_at is None:
            sub.expires_at = new_expiry(PLAN_DAYS[plan])
        db.commit()
        exp = sub.expires_at.strftime("%d.%m.%Y") if sub.expires_at else "?"
    finally:
        db.close()
    await message.answer(
        f"✅ <b>Подписка {plan.upper()} активирована!</b>\n"
        f"Оплачено: {sp.total_amount}⭐ · действует до {exp}\n"
        f"Лимит вопросов: {daily_limit_for(plan)}/день")


@dp.message(Command("myplan"))
async def cmd_myplan(message: types.Message):
    sub = get_active_subscription(message.from_user.id)
    if sub:
        await message.answer(
            f"💎 План: <b>{sub.plan.upper()}</b>\n"
            f"До: {sub.expires_at.strftime('%d.%m.%Y')}\n"
            f"Лимит: {daily_limit_for(sub.plan)} вопросов/день")
    else:
        await message.answer(
            "🆓 План: Free — 20 вопросов/день\n"
            "Расширить: /subscribe")

# ── конец блока монетизации ──────────────────────────────────────────


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

    # лимит по тарифу
    from datetime import datetime as _dt, timezone as _tz
    sub = get_active_subscription(message.from_user.id)
    limit = daily_limit_for(sub.plan if sub else "free")
    db = SessionLocal()
    try:
        used_today = db.query(QuestionLog).filter(
            QuestionLog.telegram_id == message.from_user.id,
            QuestionLog.day == _today()).count()
    finally:
        db.close()
    if used_today >= limit:
        await message.answer(
            f"🚧 Дневной лимит исчерпан ({limit} вопросов).\n"
            f"Продлите возможности: /subscribe")
        return
    dbs = SessionLocal()
    try:
        dbs.add(QuestionLog(telegram_id=message.from_user.id, day=_today()))
        dbs.commit()
    finally:
        dbs.close()

    await message.answer("⏳ Анализирую ваш вопрос...")
    try:
        answer = await ask_mistral(question, "ru")
        await send_long(message, f"🤖 <b>Ответ:</b>\n\n{answer}")
    except Exception as e:
        await message.answer(
            "❌ <b>Произошла ошибка</b>\n\n"
            f"<code>{str(e)}</code>\n\n"
            "Попробуй ещё раз или обратись к @mrpkk"
        )


# ── Блокчейн и финансовые агенты ──────────────────────────────────────

async def _get_balance_for_chain(chain: str, address: str) -> float:
    """Возвращает баланс в указанной сети."""
    if chain == "ethereum":
        from app.services.blockchains.ethereum import EthereumClient
        return await EthereumClient().get_balance(address)
    if chain == "solana":
        from app.services.blockchains.solana import SolanaClient
        return await SolanaClient().get_balance(address)
    if chain == "ton":
        from app.services.blockchains.ton import TONClient
        return await TONClient().get_balance(address)
    if chain == "cosmos":
        from app.services.blockchains.cosmos import CosmosClient
        return await CosmosClient().get_balance(address)
    if chain == "sui":
        from app.services.blockchains.sui import SuiClient
        return await SuiClient().get_balance(address)
    if chain == "aptos":
        from app.services.blockchains.aptos import AptosClient
        return await AptosClient().get_balance(address)
    raise ValueError(f"Неизвестная сеть: {chain}")


def _detect_chain(address: str) -> str:
    """Определяет сеть по формату адреса."""
    a = address.strip()
    if a.startswith(("0x",)) and len(a) == 42:
        return "ethereum"
    if a.startswith("UQ") or a.startswith("EQ") or (a.startswith("0:") and len(a) == 66):
        return "ton"
    if a.startswith("0x") and len(a) == 64:
        return "aptos"
    if a.startswith("0x") and len(a) == 66:
        return "sui"
    if a.startswith("cosmos1") or a.startswith("cosmosvaloper"):
        return "cosmos"
    # Solana — base58, 32-44 символа
    if 32 <= len(a) <= 44 and not a.startswith("0x"):
        return "solana"
    return "ethereum"


@dp.message(Command("balance"))
async def cmd_balance(message: types.Message):
    """Баланс в блокчейн-сети."""
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        text = (
            "🌐 <b>Проверка баланса</b>\n\n"
            "Используй:\n"
            "<code>/balance 0x1234...abc</code> — Ethereum/BNB\n"
            "<code>/balance SOL 9x...xyz</code> — Solana\n"
            "<code>/balance TON UQ...abc</code> — TON\n\n"
            "Сети определяются автоматически по формату адреса."
        )
        await message.answer(text)
        return

    if len(parts) == 3 and parts[1].upper() in ("SOL", "TON", "ETH", "COSMOS", "SUI", "APTOS"):
        chain_hint = parts[1].upper()
        address = parts[2]
        chain_map = {
            "SOL": "solana", "TON": "ton", "ETH": "ethereum",
            "COSMOS": "cosmos", "SUI": "sui", "APTOS": "aptos",
        }
        chain = chain_map[chain_hint]
    else:
        address = parts[1]
        chain = _detect_chain(address)

    await message.answer(f"⏳ Запрашиваю баланс в сети <b>{chain}</b>...")
    try:
        balance = await _get_balance_for_chain(chain, address)
        symbols = {
            "ethereum": "ETH", "solana": "SOL", "ton": "TON",
            "cosmos": "ATOM", "sui": "SUI", "aptos": "APT",
        }
        text = (
            f"🌐 <b>Баланс в сети {chain}</b>\n\n"
            f"💰 <code>{balance}</code> {symbols.get(chain, '')}\n"
            f"📍 Адрес: <code>{address}</code>"
        )
        await message.answer(text, disable_web_page_preview=True)
    except Exception as e:
        await message.answer(
            "❌ <b>Не удалось получить баланс</b>\n\n"
            f"<code>{str(e)}</code>\n\n"
            "Проверь адрес или попробуй позже."
        )


@dp.message(Command("risk"))
async def cmd_risk(message: types.Message):
    """Стресс-тест портфеля."""
    parts = message.text.split()
    amount = 10000.0
    if len(parts) > 1:
        try:
            amount = float(parts[1].replace(",", "."))
        except ValueError:
            pass

    await message.answer(f"⏳ Стресс-тест портфеля на <b>{amount:,.0f} ₽</b>...")
    try:
        from app.services.agents.risk.models import StressTester
        scenarios = {
            "flash_crash_-10%": -0.10,
            "correction_-20%": -0.20,
            "bear_market_-40%": -0.40,
            "black_swan_-60%": -0.60,
        }
        results = StressTester.run(amount, scenarios)
        lines = [f"📈 <b>Стресс-тест портфеля</b>\n\n💼 Сумма: {amount:,.0f} ₽\n"]
        for name, value in results.items():
            label = name.replace("_", " ").replace("-", " ").title()
            lines.append(f"🔻 {label}: <b>{value:,.0f} ₽</b>")
        lines.append("\n<i>Сценарии: резкое падение рынка и кризисы разной глубины.</i>")
        await message.answer("\n".join(lines))
    except Exception as e:
        await message.answer(
            "❌ <b>Ошибка расчёта</b>\n\n"
            f"<code>{str(e)}</code>"
        )


@dp.message(Command("yield"))
async def cmd_yield(message: types.Message):
    """DeFi-доходность."""
    parts = message.text.split()
    chain = parts[1].lower() if len(parts) > 1 else "ethereum"

    await message.answer(f"⏳ Ищу лучшие DeFi-пулы в сети <b>{chain}</b>...")
    try:
        import httpx
        from app.core.config import DEFILLAMA_YIELDS_URL
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(DEFILLAMA_YIELDS_URL)
            resp.raise_for_status()
            pools = resp.json().get("data", [])

        candidates = [
            p for p in pools
            if p.get("chain", "").lower() == chain and p.get("apy", 0) and p.get("tvlUsd", 0)
        ]
        candidates.sort(key=lambda p: (p.get("apy", 0), p.get("tvlUsd", 0)), reverse=True)
        top = candidates[:5]

        if not top:
            await message.answer(f"😕 Не нашёл пулов в сети <b>{chain}</b>. Попробуй: ethereum, bsc, polygon, arbitrum, optimism, base.")
            return

        lines = [f"🌾 <b>Топ DeFi-доходность ({chain})</b>\n"]
        for p in top:
            apy = p.get("apy", 0)
            tvl = p.get("tvlUsd", 0)
            project = p.get("project", "?")
            symbol = p.get("symbol", "?")
            lines.append(
                f"• <b>{project}</b> ({symbol})\n"
                f"  APY: <b>{apy:.2f}%</b> · TVL: ${tvl:,.0f}"
            )
        lines.append("\n<i>Данные: DeFiLlama (реальные, без ключей).</i>")
        await send_long(message, "\n".join(lines))
    except Exception as e:
        await message.answer(
            "❌ <b>Ошибка получения данных</b>\n\n"
            f"<code>{str(e)}</code>"
        )


# ── OCR: обработка фото ───────────────────────────────────────────────

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    """Распознавание текста с фотографии (OCR)."""
    if not message.photo:
        return
    file_id = message.photo[-1].file_id
    await message.answer("🔍 Распознаю текст на изображении...")

    tmp_path = None
    try:
        file = await bot.get_file(file_id)
        suffix = os.path.splitext(file.file_path or "")[1] or ".jpg"
        fd, tmp_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        await bot.download_file(file.file_path, destination=tmp_path)

        text = await extract_text_from_image(tmp_path)
        if not text:
            await message.answer(
                "😕 Не удалось распознать текст на изображении.\n"
                "Попробуй фото с более чётким текстом."
            )
        else:
            await send_long(message, f"📄 <b>Распознанный текст:</b>\n\n{text}")
    except Exception as e:
        await message.answer(
            "❌ <b>Ошибка OCR</b>\n\n"
            f"<code>{str(e)}</code>"
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


@dp.message(F.document)
async def handle_document(message: types.Message):
    """Распознавание текста с загруженного изображения-файла (OCR)."""
    doc = message.document
    if not doc or not (doc.mime_type or "").startswith("image/"):
        return
    await message.answer("🔍 Распознаю текст из файла...")

    tmp_path = None
    try:
        file = await bot.get_file(doc.file_id)
        suffix = os.path.splitext(doc.file_name or "")[1] or ".png"
        fd, tmp_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        await bot.download_file(file.file_path, destination=tmp_path)

        text = await extract_text_from_image(tmp_path)
        if not text:
            await message.answer("😕 Не удалось распознать текст на изображении.")
        else:
            await send_long(message, f"📄 <b>Распознанный текст:</b>\n\n{text}")
    except Exception as e:
        await message.answer(
            "❌ <b>Ошибка OCR</b>\n\n"
            f"<code>{str(e)}</code>"
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


# ── Обычные сообщения ─────────────────────────────────────────────────

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
            await send_long(message, f"🤖 {answer}")
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
        await send_long(message, f"🤖 {answer}")
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
