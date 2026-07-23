from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User

router = APIRouter()

@router.get("/{telegram_id}")
async def get_user(telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{telegram_id}/language")
async def update_language(telegram_id: int, language: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if language not in ["en", "ru", "es", "zh"]:
        raise HTTPException(status_code=400, detail="Invalid language")
    
    user.language = language
    db.commit()
    return {"message": "Language updated", "language": language}