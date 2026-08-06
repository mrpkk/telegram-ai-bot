"""Cosmos-клиент — REST API (без SDK)."""
from app.core.config import COSMOS_REST_URL
from app.services.blockchains.base import BlockchainClient


class CosmosClient(BlockchainClient):
    """Чтение баланса ATOM (Cosmos REST API)."""

    def __init__(self):
        super().__init__(COSMOS_REST_URL)

    async def get_balance(self, address: str) -> float:
        data = await self._get(f"/cosmos/bank/v1beta1/balances/{address}")
        for item in data.get("balances", []):
            if item.get("denom") == "uatom":
                return int(item.get("amount", 0)) / 10**6  # ATOM
        return 0.0
