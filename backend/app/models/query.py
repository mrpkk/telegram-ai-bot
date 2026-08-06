from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from app.core.database import Base

class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    question = Column(Text)
    answer = Column(Text)
    response_time_ms = Column(Float, default=0.0)
    source = Column(String(50), default="rag")
    is_helpful = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
