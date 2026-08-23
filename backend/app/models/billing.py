"""Модели монетизации: подписка (Telegram Stars) и дневной счётчик вопросов.

Новая таблица вместо ALTER users — create_all подхватит её безопасно.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    plan = Column(String, default="free")            # pro | enterprise
    stars_paid = Column(Integer, default=0)          # последняя оплата в ⭐
    starts_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)


class DocumentRegistry(Base):
    __tablename__ = "document_registry"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, index=True)
    filename = Column(String)
    chunks = Column(Integer, default=0)
    added_at = Column(DateTime(timezone=True), server_default=func.now())


class QuestionLog(Base):
    __tablename__ = "question_log"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, index=True)
    day = Column(String, index=True)                 # YYYY-MM-DD UTC
    created_at = Column(DateTime(timezone=True), server_default=func.now())
