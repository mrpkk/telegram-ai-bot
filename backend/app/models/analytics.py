from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float
from sqlalchemy.sql import func
from app.core.database import Base

class UserAnalytics(Base):
    __tablename__ = "user_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    query_count = Column(Integer, default=0)
    last_query_at = Column(DateTime(timezone=True), nullable=True)
    avg_response_time = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AdminAnalytics(Base):
    __tablename__ = "admin_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    active_users = Column(Integer, default=0)
    total_queries = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    date = Column(DateTime(timezone=True), server_default=func.now())