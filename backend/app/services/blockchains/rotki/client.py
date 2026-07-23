import requests
from typing import Dict, Any, Optional
from app.core.config import ROTKI_API_URL, ROTKI_API_KEY

class RotkiClient:
    """Унифицированный клиент для всех блокчейнов через rotki API."""

    def __init__(self):
        self.base_url = ROTKI_API_URL
        self.headers = {
            "Authorization": f"Bearer {ROTKI_API_KEY}",
            "Content-Type": "application/json"
        }

    async def get_balance(self, address: str, blockchain: str) -> float:
        """Получить баланс кошелька в указанном блокчейне."""
        endpoint = f"{self.base_url}/api/1/blockchains/{blockchain}/balances"
        payload = {"address": address}
        response = requests.post(endpoint, json=payload, headers=self.headers)
        return response.json()["result"]["total_usd_value"]

    async def get_transactions(self, address: str, blockchain: str) -> Dict[str, Any]:
        """Получить список транзакций."""
        endpoint = f"{self.base_url}/api/1/blockchains/{blockchain}/transactions"
        payload = {"address": address}
        response = requests.post(endpoint, json=payload, headers=self.headers)
        return response.json()["result"]