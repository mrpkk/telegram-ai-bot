from typing import List, Dict
from app.models.strategy import Strategy

class DCAStrategy:
    """Стратегия Dollar-Cost Averaging (DCA)."""

    @staticmethod
    async def execute(strategy: Strategy, client) -> List[str]:
        tx_hashes = []
        for _ in range(strategy.frequency):
            tx_hash = await client.swap(
                strategy.from_token,
                strategy.to_token,
                strategy.amount
            )
            tx_hashes.append(tx_hash)
        return tx_hashes

class GridStrategy:
    """Стратегия Grid Trading."""

    @staticmethod
    async def execute(strategy: Strategy, client) -> List[str]:
        tx_hashes = []
        for level in strategy.levels:
            tx_hash = await client.swap(
                strategy.from_token,
                strategy.to_token,
                level["amount"]
            )
            tx_hashes.append(tx_hash)
        return tx_hashes