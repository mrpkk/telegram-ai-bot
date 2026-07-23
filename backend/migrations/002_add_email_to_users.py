"""Миграция для добавления поля email в таблицу users."""

import sqlite3
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))
from app.config import DB_PATH


def up():
    """Применение миграции."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Проверяем, существует ли уже поле email
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if "email" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
        conn.commit()
        print("✅ Поле 'email' добавлено в таблицу 'users'")
    else:
        print("ℹ️ Поле 'email' уже существует в таблице 'users'")
    
    conn.close()


def down():
    """Откат миграции."""
    print("⚠️ Откат миграции не поддерживается для ALTER TABLE в SQLite")


if __name__ == "__main__":
    up()