from web3 import Web3
from web3.contract import Contract
from app.core.config import WEB3_PROVIDER_URL, YEARN_VAULT_ADDRESS

class YearnClient:
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))
        self.vault = self.web3.eth.contract(
            address=YEARN_VAULT_ADDRESS,
            abi=self._get_abi()
        )

    def _get_abi(self) -> list:
        # ABI для Yearn Vault
        return [
            {
                "inputs": [{"internalType": "uint256", "name": "_amount", "type": "uint256"}],
                "name": "deposit",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]

    async def deposit(self, wallet_address: str, token: str, amount: float) -> str:
        tx_hash = self.vault.functions.deposit(
            self.web3.to_wei(amount, "ether")
        ).transact({"from": wallet_address})
        return tx_hash.hex()