from typing import Dict, List
from app.models.user import User
from app.models.strategy import Strategy
from app.services.agents.trading.strategies import DCAStrategy, GridStrategy
from app.core.database import get_db

class TradingAgent:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.db = next(get_db())
        self.user = self.db.query(User).filter(User.id == user_id).first()
        self.strategies = self.db.query(Strategy).filter(Strategy.user_id == user_id).all()

    async def execute_strategies(self) -> Dict[str, List[str]]:
        results = {}
        
        for strategy in self.strategies:
            if strategy.blockchain == "ethereum":
                from app.services.blockchains.ethereum.client import EthereumClient
                client = EthereumClient()
            elif strategy.blockchain == "solana":
                from app.services.blockchains.solana.client import SolanaClient
                client = SolanaClient()
            
            if strategy.type == "dca":
                result = await DCAStrategy.execute(strategy, client)
            elif strategy.type == "grid":
                result = await GridStrategy.execute(strategy, client)
            
            results[strategy.name] = result
        
        return results