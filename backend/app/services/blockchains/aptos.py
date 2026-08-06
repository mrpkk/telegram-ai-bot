"""Aptos-клиент — REST API (без SDK)."""
from app.core.config import APTOS_API_URL
from app.services.blockchains.base import BlockchainClient


class AptosClient(BlockchainClient):
    """Чтение баланса APT (Aptos REST API)."""

    def __init__(self):
        super().__init__(APTOS_API_URL)

    async def get_balance(self, address: str) -> float:
        data = await self._get(f"/accounts/{address}/resources")
        for resource in data:
            if resource.get("type", "").endswith("0x1::coin::CoinStore<0x1::aptos_coin::AptosCoin>"):
                value = resource.get("data", {}).get("coin", {}).get("value", 0)
                return int(value) / 10**8  # APT
        return 0.0
