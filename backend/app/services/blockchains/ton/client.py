"""TON-клиент — через Toncenter HTTP API (без SDK)."""
from app.core.config import TON_API_URL
from app.services.blockchains.base import BlockchainClient


class TONClient(BlockchainClient):
    """Чтение баланса TON (Toncenter API, без ключа для публичных запросов)."""

    def __init__(self):
        super().__init__(TON_API_URL)

    async def get_balance(self, address: str) -> float:
        data = await self._get("/getAddressBalance", params={"address": address})
        nano = int(data.get("result", 0))
        return nano / 10**9  # TON
