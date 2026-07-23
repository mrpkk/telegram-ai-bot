from sqlalchemy.orm import Session
from app.models.analytics import UserAnalytics, AdminAnalytics
from app.models.user import User
from app.models.query import Query
from datetime import datetime, timedelta
from typing import Optional

class AnalyticsService:
    @staticmethod
    def update_user_analytics(db: Session, user_id: int, response_time: float) -> None:
        analytics = db.query(UserAnalytics).filter(UserAnalytics.user_id == user_id).first()
        if not analytics:
            analytics = UserAnalytics(user_id=user_id)
            db.add(analytics)
        
        analytics.query_count += 1
        analytics.last_query_at = datetime.now()
        analytics.avg_response_time = (
            (analytics.avg_response_time * (analytics.query_count - 1) + response_time) / analytics.query_count
        )
        db.commit()

    @staticmethod
    def update_admin_analytics(db: Session) -> None:
        # Активные пользователи за последние 7 дней
        active_users = db.query(User).filter(
            User.last_active_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        # Общее количество запросов
        total_queries = db.query(Query).count()
        
        # Доходы от подписок
        revenue = db.query(User).filter(User.subscription_plan != "free").with_entities(
            User.subscription_price
        ).all()
        revenue = sum(price for (price,) in revenue) if revenue else 0.0
        
        # Сохраняем в БД
        analytics = AdminAnalytics(
            active_users=active_users,
            total_queries=total_queries,
            revenue=revenue,
            date=datetime.now()
        )
        db.add(analytics)
        db.commit()