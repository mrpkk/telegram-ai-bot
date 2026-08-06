"""Ethereum-клиент — JSON-RPC через публичный RPC."""
from app.core.config import ETH_RPC_URL
from app.services.blockchains.base import BlockchainClient


class EthereumClient(BlockchainClient):
    """Чтение баланса Ethereum (публичный RPC, без ключа)."""

    def __init__(self):
        super().__init__(ETH_RPC_URL)

    async def get_balance(self, address: str) -> float:
        data = await self._post({
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": [address, "latest"],
            "id": 1,
        })
        wei = int(data.get("result", "0x0"), 16)
        return wei / 10**18  # ETH
