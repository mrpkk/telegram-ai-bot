"""Тарифные лимиты документов (RTM FR-10) — без сети и БД."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

try:
    from app.services.plan_limits import DOCS_LIMITS, docs_limit_for, plan_of_user
except ImportError:
    pytest.skip("нет backend/app окружения", allow_module_level=True)


def test_limits_by_plan():
    assert docs_limit_for("free") == 5
    assert docs_limit_for("pro") == 50
    assert docs_limit_for("enterprise") is None   # ∞


def test_unknown_plan_falls_back_to_free():
    assert docs_limit_for("vip") == 5


def test_expired_subscription_is_free():
    class FakeSub:
        plan = "pro"

        from datetime import datetime, timedelta, timezone
        expires_at = datetime.now(timezone.utc) - timedelta(days=1)

    class FakeDB:
        def query(self, *a):
            return self

        def filter(self, *a):
            return self

        def first(self):
            return FakeSub()

    # подписка истекла -> free (проверяем через публичную функцию)
    from datetime import datetime, timedelta, timezone
    FakeSub.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    assert plan_of_user(FakeDB(), telegram_id=1) == "free"
