"""Solana-клиент — JSON-RPC через публичный RPC."""
from app.core.config import SOLANA_RPC_URL
from app.services.blockchains.base import BlockchainClient


class SolanaClient(BlockchainClient):
    """Чтение баланса SOL (публичный RPC, без ключа)."""

    def __init__(self):
        super().__init__(SOLANA_RPC_URL)

    async def get_balance(self, address: str) -> float:
        data = await self._post({
            "jsonrpc": "2.0",
            "method": "getBalance",
            "params": [address],
            "id": 1,
        })
        lamports = data.get("result", {}).get("value", 0)
        return lamports / 10**9  # SOL
