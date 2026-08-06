# Модуль для моделей данных.
from .user import User
from .analytics import UserAnalytics, AdminAnalytics
from .portfolio import Portfolio
from .strategy import Strategy
from app.core.database import Base, engine


def init_db():
    """Инициализация таблиц БД через SQLAlchemy ORM."""
    Base.metadata.create_all(bind=engine)


from pydantic import BaseModel
from typing import Optional


class FAQCreate(BaseModel):
    question: str
    answer: str
    category: str = "general"


__all__ = ["User", "UserAnalytics", "AdminAnalytics", "Portfolio", "Strategy", "init_db", "get_db", "FAQCreate"]