from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.analytics import UserAnalytics, AdminAnalytics
from app.models.user import User
from app.models.query import Query
from datetime import datetime, timedelta
import pandas as pd

router = APIRouter()

@router.get("/user/{telegram_id}")
async def get_user_analytics(telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    analytics = db.query(UserAnalytics).filter(UserAnalytics.user_id == user.id).first()
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found")
    
    return {
        "query_count": analytics.query_count,
        "last_query_at": analytics.last_query_at,
        "avg_response_time": analytics.avg_response_time
    }

@router.get("/admin")
async def get_admin_analytics(db: Session = Depends(get_db)):
    # Активные пользователи за последние 7 дней
    active_users = db.query(User).filter(
        User.last_active_at >= datetime.now() - timedelta(days=7)
    ).count()
    
    # Общее количество запросов
    total_queries = db.query(Query).count()
    
    # Доходы от подписок
    revenue = db.query(func.sum(User.subscription_price)).filter(
        User.subscription_plan != "free"
    ).scalar() or 0.0
    
    # Топ-5 команд
    top_commands = db.query(
        Query.command, func.count(Query.id).label("count")
    ).group_by(Query.command).order_by(func.count(Query.id).desc()).limit(5).all()
    
    return {
        "active_users": active_users,
        "total_queries": total_queries,
        "revenue": revenue,
        "top_commands": [{"command": cmd, "count": count} for cmd, count in top_commands]
    }