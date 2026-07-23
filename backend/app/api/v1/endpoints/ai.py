from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.services.rag import ask_rag
from app.core.i18n import get_translation

router = APIRouter()

@router.post("/ask")
async def ask_question(telegram_id: int, question: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    answer = await ask_rag(question, user.language)
    return {
        "question": question,
        "answer": answer,
        "language": user.language
    }