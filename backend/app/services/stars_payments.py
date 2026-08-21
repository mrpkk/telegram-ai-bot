"""Telegram Stars (XTR) payments — самодостаточная монетизация без внешних мерчантов.

Почему Stars: Stripe недоступен для РФ, CryptoBot требует отдельной регистрации.
Stars работает через существующий токен бота (sendInvoice с currency="XTR").

Тарифы (звёзды ≈ $0.013–0.02 за ⭐ на момент ввода):
- pro:        500⭐ / 30 дней
- enterprise: 2500⭐ / 30 дней
"""
from datetime import datetime, timedelta, timezone

from aiogram.types import LabeledPrice

PLAN_STARS = {"pro": 500, "enterprise": 2500}
PLAN_DAYS = {"pro": 30, "enterprise": 30}
FREE_DAILY_LIMIT = 20          # вопросов /ask в сутки для free
PAID_DAILY_LIMIT = 300

PLANS_TEXT_RU = {
    "free": "Free — 20 вопросов в день",
    "pro": "Pro — 300 вопросов в день, приоритетная очередь (500⭐/мес)",
    "enterprise": "Enterprise — без лимитов + API-доступ (2500⭐/мес)",
}


def daily_limit_for(plan: str) -> int:
    if plan == "pro":
        return PAID_DAILY_LIMIT
    if plan == "enterprise":
        return 10**9
    return FREE_DAILY_LIMIT


def subscription_active(plan: str | None, expires_at: datetime | None) -> bool:
    if plan in PLAN_DAYS and expires_at is not None:
        return expires_at > datetime.now(timezone.utc)
    return False


async def send_plan_invoice(bot, chat_id: int, plan: str) -> None:
    """Отправить счёт Telegram Stars. payload = subscribe:<plan>."""
    stars = PLAN_STARS.get(plan)
    if not stars:
        raise ValueError(f"Unknown plan: {plan}")
    await bot.send_invoice(
        chat_id=chat_id,
        title=f"Подписка {plan.upper()}",
        description=PLANS_TEXT_RU.get(
            "pro" if plan == "pro" else "enterprise", PLANS_TEXT_RU["free"]
        ),
        payload=f"subscribe:{plan}",
        currency="XTR",
        prices=[LabeledPrice(label=f"{plan.upper()} · 30 дней", amount=stars)],
    )


def new_expiry(days: int = 30) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days)
