"""Модели данных (SQLAlchemy + Pydantic)."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

DB_PATH: Optional[Path] = None


def get_db() -> sqlite3.Connection:
    """Получить соединение с БД."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Инициализация таблиц БД."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_size INTEGER,
            chunks_count INTEGER DEFAULT 0,
            tags TEXT DEFAULT '',
            uploaded_by INTEGER,
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
            source TEXT,
            response_time_ms INTEGER,
            is_helpful INTEGER DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


# ── Pydantic модели ──────────────────────────────────────────────────

class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None

class DocumentCreate(BaseModel):
    filename: str
    file_path: str
    file_type: str
    file_size: int = 0
    chunks_count: int = 0
    tags: str = ""
    uploaded_by: Optional[int] = None

class FAQCreate(BaseModel):
    question: str
    answer: str
    category: str = "general"

class LogCreate(BaseModel):
    user_id: Optional[int] = None
    question: str = ""
    answer: str = ""
    source: str = ""
    response_time_ms: int = 0
    is_helpful: Optional[int] = None
