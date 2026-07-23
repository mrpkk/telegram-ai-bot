from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.agents.trading_agent import TradingAgent
from app.services.agents.risk_agent import RiskAgent
from app.services.agents.yield_agent import YieldAgent

router = APIRouter()

@router.post("/trading/execute")
async def execute_trading_strategies(user_id: int, db: Session = Depends(get_db)):
    agent = TradingAgent(user_id)
    results = await agent.execute_strategies()
    return results

@router.get("/risk/var")
async def calculate_var(user_id: int, confidence: float = 0.95, db: Session = Depends(get_db)):
    agent = RiskAgent(user_id)
    results = await agent.calculate_var(confidence)
    return results

@router.get("/risk/stress-test")
async def stress_test(user_id: int, db: Session = Depends(get_db)):
    agent = RiskAgent(user_id)
    results = await agent.stress_test()
    return results

@router.post("/yield/optimize")
async def optimize_yield(user_id: int, db: Session = Depends(get_db)):
    agent = YieldAgent(user_id)
    results = await agent.optimize_yield()
    return results