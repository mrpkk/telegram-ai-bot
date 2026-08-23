"""Загрузка документов в RAG с тарифными лимитами (RTM FR-2/FR-10).

Лимиты по плану подписки: free=5, pro=50, enterprise=без лимита.
Учёт — таблица DocumentRegistry; дубликаты имён одного пользователя запрещены.
"""
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.billing import DocumentRegistry
from app.services.plan_limits import docs_limit_for, plan_of_user
from app.models.user import User

router = APIRouter()

ALLOWED_SUFFIXES = {".pdf", ".xlsx", ".xls", ".docx", ".txt", ".md", ".csv"}
MAX_FILE_MB = 25


def _docs_dir() -> Path:
    d = Path(os.getenv("DOCS_DIR", "data/documents"))
    d.mkdir(parents=True, exist_ok=True)
    return d


import os  # noqa: E402


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    telegram_id: int = 0,
    db: Session = Depends(get_db),
):
    """Загрузить документ в персональный RAG (с учётом тарифа)."""
    if not file.filename:
        raise HTTPException(400, "Файл без имени")
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(415,
            f"Формат {suffix} не поддерживается. Доступны: {sorted(ALLOWED_SUFFIXES)}")

    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден — отправьте /start боту")

    plan = plan_of_user(db, telegram_id)
    limit = docs_limit_for(plan)

    used = db.query(DocumentRegistry).filter(
        DocumentRegistry.telegram_id == telegram_id).count()
    if limit is not None and used >= limit:
        raise HTTPException(402, (
            f"Лимит тарифа {plan}: {limit} документов (использовано {used}). "
            "Расширить: /subscribe"))

    dup = db.query(DocumentRegistry).filter(
        DocumentRegistry.telegram_id == telegram_id,
        DocumentRegistry.filename == file.filename).first()
    if dup:
        raise HTTPException(409, f"«{file.filename}» уже загружен")

    # размер до записи на диск
    size = 0
    tmp = _docs_dir() / f"{telegram_id}__{file.filename}"
    with tmp.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_FILE_MB * 1024 * 1024:
                out.close()
                tmp.unlink(missing_ok=True)
                raise HTTPException(413, f"Файл >{MAX_FILE_MB}MB")
            out.write(chunk)

    try:
        from app.rag import RAGSystem
        rag = RAGSystem()
        chunks = await rag.add_document(tmp, file.filename)
    except Exception as e:
        tmp.unlink(missing_ok=True)
        raise HTTPException(500, f"Индексация не удалась: {e}")

    db.add(DocumentRegistry(telegram_id=telegram_id,
                            filename=file.filename, chunks=chunks))
    db.commit()

    return {
        "ok": True, "filename": file.filename, "chunks": chunks,
        "plan": plan, "docs_used": used + 1, "docs_limit": limit or "∞",
    }


@router.get("/documents")
async def list_documents(telegram_id: int, db: Session = Depends(get_db)):
    rows = db.query(DocumentRegistry).filter(
        DocumentRegistry.telegram_id == telegram_id).all()
    return {"items": [{"filename": r.filename, "chunks": r.chunks,
                       "added_at": str(r.added_at)} for r in rows]}
