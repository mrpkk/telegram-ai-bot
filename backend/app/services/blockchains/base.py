from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class BlockchainClient(ABC):
    """Абстрактный базовый класс для всех блокчейнов."""

    @abstractmethod
    async def get_balance(self, address: str) -> float:
        """Получить баланс кошелька."""
        pass

    @abstractmethod
    async def send_transaction(self, to_address: str, amount: float, **kwargs) -> str:
        """Отправить транзакцию."""
        pass

    @abstractmethod
    async def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Получить информацию о транзакции."""
        pass

    @abstractmethod
    async def swap(self, from_token: str, to_token: str, amount: float) -> str:
        """Обмен токенов (если поддерживается)."""
        pass