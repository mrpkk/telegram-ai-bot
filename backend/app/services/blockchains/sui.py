"""Sui-клиент — JSON-RPC через публичный RPC."""
from app.core.config import SUI_RPC_URL
from app.services.blockchains.base import BlockchainClient


class SuiClient(BlockchainClient):
    """Чтение баланса SUI (публичный RPC, без ключа)."""

    def __init__(self):
        super().__init__(SUI_RPC_URL)

    async def get_balance(self, address: str) -> float:
        data = await self._post({
            "jsonrpc": "2.0",
            "method": "suix_getBalance",
            "params": [address, "0x2::sui::SUI"],
            "id": 1,
        })
        total = data.get("result", {}).get("totalBalance", 0)
        return int(total) / 10**9  # SUI
