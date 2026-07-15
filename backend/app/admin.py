"""Административный API."""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from config import ADMIN_USERNAME, ADMIN_PASSWORD, DOCUMENTS_PATH
from models import get_db, FAQCreate

log = logging.getLogger("admin")
router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Проверка авторизации."""
    if credentials.username != ADMIN_USERNAME or credentials.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Неверные учётные данные")
    return credentials.username


# ── Документы ──────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    tags: str = "",
    username: str = Depends(verify_credentials)
):
    """Загрузка документа."""
    allowed_types = {".pdf", ".txt", ".md", ".csv", ".docx"}
    suffix = Path(file.filename).suffix.lower()

    if suffix not in allowed_types:
        raise HTTPException(400, f"Неподдерживаемый формат: {suffix}")

    # Сохраняем файл
    file_path = DOCUMENTS_PATH / file.filename
    content = await file.read()
    file_path.write_bytes(content)

    # Добавляем в RAG
    from rag import RAGSystem
    rag = RAGSystem()
    try:
        chunks_count = rag.add_document(file_path, file.filename)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(500, f"Ошибка обработки: {e}")

    # Сохраняем метаданные
    db = get_db()
    try:
        db.execute(
            "INSERT INTO documents (filename, file_path, file_type, file_size, chunks_count, tags) VALUES (?, ?, ?, ?, ?, ?)",
            (file.filename, str(file_path), suffix, len(content), chunks_count, tags)
        )
        db.commit()
    finally:
        db.close()

    return {
        "status": "ok",
        "filename": file.filename,
        "chunks": chunks_count,
        "size": len(content)
    }


@router.get("/documents")
async def list_documents(username: str = Depends(verify_credentials)):
    """Список документов."""
    db = get_db()
    try:
        docs = db.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
        return [dict(doc) for doc in docs]
    finally:
        db.close()


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: int, username: str = Depends(verify_credentials)):
    """Удаление документа."""
    db = get_db()
    try:
        doc = db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
        if not doc:
            raise HTTPException(404, "Документ не найден")

        file_path = Path(doc["file_path"])
        if file_path.exists():
            os.remove(file_path)

        db.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        db.commit()
        return {"status": "deleted", "filename": doc["filename"]}
    finally:
        db.close()


# ── FAQ ────────────────────────────────────────────────────────────────

@router.post("/faq")
async def add_faq(item: FAQCreate, username: str = Depends(verify_credentials)):
    """Добавление FAQ."""
    db = get_db()
    try:
        db.execute(
            "INSERT INTO faq (question, answer, category) VALUES (?, ?, ?)",
            (item.question, item.answer, item.category)
        )
        db.commit()
        return {"status": "created"}
    finally:
        db.close()


@router.get("/faq")
async def list_faq(username: str = Depends(verify_credentials)):
    """Список FAQ."""
    db = get_db()
    try:
        faqs = db.execute("SELECT * FROM faq ORDER BY created_at DESC").fetchall()
        return [dict(f) for f in faqs]
    finally:
        db.close()


@router.delete("/faq/{faq_id}")
async def delete_faq(faq_id: int, username: str = Depends(verify_credentials)):
    """Удаление FAQ."""
    db = get_db()
    try:
        db.execute("DELETE FROM faq WHERE id = ?", (faq_id,))
        db.commit()
        return {"status": "deleted"}
    finally:
        db.close()


# ── Статистика ─────────────────────────────────────────────────────────

@router.get("/stats")
async def get_stats(username: str = Depends(verify_credentials)):
    """Получение статистики."""
    db = get_db()
    try:
        stats = {
            "users_total": db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "users_today": db.execute(
                "SELECT COUNT(*) FROM users WHERE date(last_active) = date('now')"
            ).fetchone()[0],
            "questions_total": db.execute("SELECT COUNT(*) FROM logs").fetchone()[0],
            "questions_today": db.execute(
                "SELECT COUNT(*) FROM logs WHERE date(created_at) = date('now')"
            ).fetchone()[0],
            "avg_response_time": db.execute(
                "SELECT AVG(response_time_ms) FROM logs WHERE date(created_at) = date('now')"
            ).fetchone()[0] or 0,
            "documents_count": db.execute("SELECT COUNT(*) FROM documents").fetchone()[0],
            "faq_count": db.execute("SELECT COUNT(*) FROM faq WHERE is_active = 1").fetchone()[0],
        }

        # Топ вопросов
        top_questions = db.execute(
            "SELECT question, COUNT(*) as count FROM logs GROUP BY question ORDER BY count DESC LIMIT 10"
        ).fetchall()
        stats["top_questions"] = [{"question": q["question"], "count": q["count"]} for q in top_questions]

        # Точность ответов
        helpful = db.execute(
            "SELECT is_helpful, COUNT(*) FROM logs WHERE is_helpful IS NOT NULL GROUP BY is_helpful"
        ).fetchall()
        helpful_dict = {row[0]: row[1] for row in helpful}
        total = helpful_dict.get(1, 0) + helpful_dict.get(0, 0)
        stats["accuracy"] = round(helpful_dict.get(1, 0) / total * 100, 1) if total > 0 else 0

        return stats
    finally:
        db.close()


# ── Логи ───────────────────────────────────────────────────────────────

@router.get("/logs")
async def get_logs(
    page: int = 1,
    per_page: int = 50,
    username: str = Depends(verify_credentials)
):
    """Получение логов."""
    db = get_db()
    try:
        offset = (page - 1) * per_page
        logs = db.execute(
            "SELECT l.*, u.username, u.first_name FROM logs l LEFT JOIN users u ON l.user_id = u.telegram_id ORDER BY l.created_at DESC LIMIT ? OFFSET ?",
            (per_page, offset)
        ).fetchall()
        total = db.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
        return {
            "logs": [dict(log) for log in logs],
            "total": total,
            "page": page,
            "per_page": per_page
        }
    finally:
        db.close()


@router.post("/clear")
async def clear_database(username: str = Depends(verify_credentials)):
    """Очистка базы знаний."""
    db = get_db()
    try:
        db.execute("DELETE FROM documents")
        db.execute("DELETE FROM logs")
        db.commit()

        # Очищаем Chroma
        import shutil
        from config import CHROMA_PATH
        if CHROMA_PATH.exists():
            shutil.rmtree(CHROMA_PATH)
            CHROMA_PATH.mkdir(parents=True, exist_ok=True)

        return {"status": "cleared"}
    finally:
        db.close()
