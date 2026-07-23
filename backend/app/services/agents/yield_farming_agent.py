from typing import Dict, List
from app.models.user import User
from app.models.portfolio import Portfolio
from app.services.defi.aave.client import AaveClient
from app.services.defi.lido.client import LidoClient
from app.services.defi.yearn.client import YearnClient
from app.core.database import get_db

class YieldAgent:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.db = next(get_db())
        self.user = self.db.query(User).filter(User.id == user_id).first()
        self.portfolio = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).first()

    async def optimize_yield(self) -> Dict[str, List[str]]:
        results = {}
        
        # Aave
        aave_client = AaveClient()
        aave_result = await aave_client.deposit(
            self.user.wallet_address,
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
            self.portfolio.get_asset("USDC")["amount"]
        )
        results["aave"] = [aave_result]
        
        # Lido
        lido_client = LidoClient()
        lido_result = await lido_client.stake(
            self.user.wallet_address,
            self.portfolio.get_asset("ETH")["amount"]
        )
        results["lido"] = [lido_result]
        
        # Yearn
        yearn_client = YearnClient()
        yearn_result = await yearn_client.deposit(
            self.user.wallet_address,
            "0x6B175474E89094C44Da98b954EedeAC495271d0F",  # DAI
            self.portfolio.get_asset("DAI")["amount"]
        )
        results["yearn"] = [yearn_result]
        
        return results