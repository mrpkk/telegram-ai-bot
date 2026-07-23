from sqlalchemy import Column, Integer, String, Float, JSON, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # dca, grid, yield
    blockchain = Column(String, nullable=False)  # ethereum, solana, ton, cosmos, sui, aptos
    from_token = Column(String, nullable=False)
    to_token = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    frequency = Column(Integer, nullable=True)  # Для DCA
    levels = Column(JSON, nullable=True)  # Для Grid
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())