from typing import Dict
import numpy as np
from app.models.user import User
from app.models.portfolio import Portfolio
from app.core.database import get_db
from app.services.agents.risk.models import VaRCalculator, StressTester

class RiskAgent:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.db = next(get_db())
        self.user = self.db.query(User).filter(User.id == user_id).first()
        self.portfolio = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).first()

    async def calculate_var(self, confidence: float = 0.95) -> Dict[str, float]:
        returns = [asset["historical_returns"] for asset in self.portfolio.assets]
        var = VaRCalculator.calculate(returns, confidence)
        return {"var": var, "confidence": confidence}

    async def stress_test(self) -> Dict[str, float]:
        scenarios = {
            "market_crash": -0.3,
            "recession": -0.15,
            "bull_market": 0.2
        }
        return StressTester.run(self.portfolio.total_value, scenarios)