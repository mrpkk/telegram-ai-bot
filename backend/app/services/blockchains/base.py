"""Базовый клиент блокчейна — чистый HTTP (JSON-RPC / REST), без SDK.

Использует публичные RPC-эндпоинты, работает без API-ключей.
"""
from abc import ABC, abstractmethod

import httpx


class BlockchainClient(ABC):
    """Базовый клиент блокчейна."""

    def __init__(self, rpc_url: str, timeout: float = 15.0):
        self.rpc_url = rpc_url
        self._timeout = httpx.Timeout(timeout)

    async def _post(self, payload: dict) -> dict:
        """JSON-RPC POST-запрос."""
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(self.rpc_url, json=payload)
            resp.raise_for_status()
            return resp.json()

    async def _get(self, path: str, params: dict | None = None) -> dict | list:
        """REST GET-запрос (путь добавляется к rpc_url)."""
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(f"{self.rpc_url}{path}", params=params)
            resp.raise_for_status()
            return resp.json()

    @abstractmethod
    async def get_balance(self, address: str) -> float:
        """Баланс нативного токена (в единицах монеты)."""
        raise NotImplementedError
