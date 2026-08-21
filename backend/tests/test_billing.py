"""Тесты монетизации: тарифы, лимиты, активность подписки (без сети)."""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # корень проекта
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

import pytest


def _import_service():
    try:
        from app.services.stars_payments import (
            PLAN_DAYS, PLAN_STARS, daily_limit_for, new_expiry,
            send_plan_invoice, subscription_active,
        )
        return daily_limit_for, subscription_active
    except ImportError:
        pytest.skip("app-пакет недоступен вне полного окружения")


def test_limits_by_plan():
    dlf, _ = _import_service()
    assert dlf("free") == 20
    assert dlf("pro") > dlf("free")
    assert dlf("enterprise") >= 10**9


def test_subscription_activity_windows():
    _, sa = _import_service()
    now = datetime.now(timezone.utc)
    assert sa("pro", now + timedelta(days=5)) is True
    assert sa("pro", now - timedelta(hours=1)) is False
    assert sa("free", None) is False
    assert sa(None, now + timedelta(days=1)) is False


def test_plans_consistency():
    try:
        from app.services.stars_payments import PLAN_DAYS, PLAN_STARS
    except ImportError:
        pytest.skip("нет app-окружения")
    assert set(PLAN_DAYS) == set(PLAN_STARS)
    assert all(v > 0 for v in PLAN_STARS.values())
