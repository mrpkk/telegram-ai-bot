"""Административный API."""

import os
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import text

from app.core.config import ADMIN_USERNAME, ADMIN_PASSWORD, DOCUMENTS_PATH, CHROMA_PATH
from app.core.database import SessionLocal
from app.models import FAQCreate

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

    # Добавляем в RAG (упрощённый сплиттер — локально, без внешних сервисов)
    try:
        text_content = content.decode("utf-8", errors="ignore")
        chunks_count = max(1, (len(text_content) + 999) // 1000)  # ~1000 символов на чанк
    except Exception:
        chunks_count = 1

    # Сохраняем метаданные
    db = SessionLocal()
    try:
        db.execute(
            text("INSERT INTO documents (filename, file_path, file_type, file_size, chunks_count, tags) VALUES (?, ?, ?, ?, ?, ?)"),
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
    db = SessionLocal()
    try:
        docs = db.execute(text("SELECT * FROM documents ORDER BY created_at DESC")).fetchall()
        return [dict(doc) for doc in docs]
    finally:
        db.close()


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: int, username: str = Depends(verify_credentials)):
    """Удаление документа."""
    db = SessionLocal()
    try:
        doc = db.execute(text("SELECT * FROM documents WHERE id = ?"), (doc_id,)).fetchone()
        if not doc:
            raise HTTPException(404, "Документ не найден")

        file_path = Path(doc["file_path"])
        if file_path.exists():
            os.remove(file_path)

        db.execute(text("DELETE FROM documents WHERE id = ?"), (doc_id,))
        db.commit()
        return {"status": "deleted", "filename": doc["filename"]}
    finally:
        db.close()


# ── FAQ ────────────────────────────────────────────────────────────────

@router.post("/faq")
async def add_faq(item: FAQCreate, username: str = Depends(verify_credentials)):
    """Добавление FAQ."""
    db = SessionLocal()
    try:
        db.execute(
            text("INSERT INTO faq (question, answer, category) VALUES (?, ?, ?)"),
            (item.question, item.answer, item.category)
        )
        db.commit()
        return {"status": "created"}
    finally:
        db.close()


@router.get("/faq")
async def list_faq(username: str = Depends(verify_credentials)):
    """Список FAQ."""
    db = SessionLocal()
    try:
        faqs = db.execute(text("SELECT * FROM faq ORDER BY created_at DESC")).fetchall()
        return [dict(f) for f in faqs]
    finally:
        db.close()


@router.delete("/faq/{faq_id}")
async def delete_faq(faq_id: int, username: str = Depends(verify_credentials)):
    """Удаление FAQ."""
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM faq WHERE id = ?"), (faq_id,))
        db.commit()
        return {"status": "deleted"}
    finally:
        db.close()


# ── Статистика ─────────────────────────────────────────────────────────

@router.get("/stats")
async def get_stats(username: str = Depends(verify_credentials)):
    """Получение статистики."""
    db = SessionLocal()
    try:
        stats = {
            "users_total": db.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0],
            "users_today": db.execute(
                text("SELECT COUNT(*) FROM users WHERE date(created_at) = date('now')")
            ).fetchone()[0],
            "questions_total": db.execute(text("SELECT COUNT(*) FROM logs")).fetchone()[0],
            "questions_today": db.execute(
                text("SELECT COUNT(*) FROM logs WHERE date(created_at) = date('now')")
            ).fetchone()[0],
            "avg_response_time": db.execute(
                text("SELECT AVG(response_time_ms) FROM logs WHERE date(created_at) = date('now')")
            ).fetchone()[0] or 0,
            "documents_count": db.execute(text("SELECT COUNT(*) FROM documents")).fetchone()[0],
            "faq_count": db.execute(text("SELECT COUNT(*) FROM faq WHERE is_active = 1")).fetchone()[0],
        }

        # Топ вопросов
        top_questions = db.execute(
            text("SELECT question, COUNT(*) as count FROM logs GROUP BY question ORDER BY count DESC LIMIT 10")
        ).fetchall()
        stats["top_questions"] = [{"question": q["question"], "count": q["count"]} for q in top_questions]

        # Точность ответов
        helpful = db.execute(
            text("SELECT is_helpful, COUNT(*) FROM logs WHERE is_helpful IS NOT NULL GROUP BY is_helpful")
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
    db = SessionLocal()
    try:
        offset = (page - 1) * per_page
        logs = db.execute(
            text("SELECT l.*, u.username, u.full_name FROM logs l LEFT JOIN users u ON l.user_id = u.telegram_id ORDER BY l.created_at DESC LIMIT :per_page OFFSET :offset"),
            {"per_page": per_page, "offset": offset}
        ).fetchall()
        total = db.execute(text("SELECT COUNT(*) FROM logs")).fetchone()[0]
        return {
            "logs": [dict(log) for log in logs],
            "total": total,
            "page": page,
            "per_page": per_page
        }
    finally:
        db.close()


@router.get("/export")
async def export_report(
    fmt: str = "xlsx",
    username: str = Depends(verify_credentials)
):
    """Экспорт отчёта: логи запросов + пользователи (CSV или Excel)."""
    import io
    import csv as csv_mod

    db = SessionLocal()
    try:
        users = db.execute(text("SELECT id, telegram_id, username, full_name, language, subscription_plan, created_at FROM users ORDER BY id")).fetchall()
        logs = db.execute(text("SELECT id, user_id, question, answer, response_time_ms, source, is_helpful, created_at FROM logs ORDER BY created_at DESC")).fetchall()

        user_cols = ["id", "telegram_id", "username", "full_name", "language", "subscription_plan", "created_at"]
        log_cols = ["id", "user_id", "question", "answer", "response_time_ms", "source", "is_helpful", "created_at"]
        users = [dict(u._mapping) for u in users]
        logs = [dict(l._mapping) for l in logs]

        if fmt == "csv":
            buf = io.StringIO()
            w = csv_mod.writer(buf)
            w.writerow(["=== USERS ==="])
            w.writerow(user_cols)
            for u in users:
                w.writerow([u[c] for c in user_cols])
            w.writerow([])
            w.writerow(["=== LOGS ==="])
            w.writerow(log_cols)
            for l in logs:
                w.writerow([l[c] for c in log_cols])
            content = "\ufeff" + buf.getvalue()  # BOM для корректной кириллицы в Excel
            return Response(
                content=content,
                media_type="text/csv; charset=utf-8",
                headers={"Content-Disposition": "attachment; filename=report.csv"}
            )

        # xlsx
        import openpyxl
        wb = openpyxl.Workbook()
        ws_users = wb.active
        ws_users.title = "Users"
        ws_users.append(user_cols)
        for u in users:
            ws_users.append([u[c] for c in user_cols])

        ws_logs = wb.create_sheet("Logs")
        ws_logs.append(log_cols)
        for l in logs:
            ws_logs.append([l[c] for c in log_cols])

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return Response(
            content=buf.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=report.xlsx"}
        )
    finally:
        db.close()


@router.post("/clear")
async def clear_database(username: str = Depends(verify_credentials)):
    """Очистка базы знаний."""
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM documents"))
        db.execute(text("DELETE FROM logs"))
        db.commit()

        # Очищаем Chroma
        import shutil
        if CHROMA_PATH.exists():
            shutil.rmtree(CHROMA_PATH)
            CHROMA_PATH.mkdir(parents=True, exist_ok=True)

        return {"status": "cleared"}
    finally:
        db.close()
