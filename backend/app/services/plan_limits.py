"""Тарифные лимиты (единый источник для бота и API)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

DOCS_LIMITS = {"free": 5, "pro": 50, "enterprise": None}      # None = ∞


def plan_of_user(db, telegram_id: int) -> str:
    """Активный план пользователя: subscriptions.expires_at > now -> план."""
    from app.models.billing import Subscription

    sub = db.query(Subscription).filter(
        Subscription.telegram_id == telegram_id).first()
    if sub and sub.plan in DOCS_LIMITS:
        exp = sub.expires_at
        if exp is not None:
            exp = exp if exp.tzinfo else exp.replace(tzinfo=timezone.utc)
            if exp > datetime.now(timezone.utc):
                return sub.plan
    return "free"


def docs_limit_for(plan: str) -> Optional[int]:
    return DOCS_LIMITS.get(plan, DOCS_LIMITS["free"])
