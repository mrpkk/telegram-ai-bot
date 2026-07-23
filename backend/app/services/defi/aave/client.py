from web3 import Web3
from web3.contract import Contract
from app.core.config import WEB3_PROVIDER_URL, AAVE_LENDING_POOL_ADDRESS

class AaveClient:
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))
        self.lending_pool = self.web3.eth.contract(
            address=AAVE_LENDING_POOL_ADDRESS,
            abi=self._get_abi()
        )

    def _get_abi(self) -> list:
        # ABI для Aave LendingPool
        return [
            {
                "inputs": [{"internalType": "address", "name": "asset", "type": "address"}],
                "name": "deposit",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]

    async def deposit(self, wallet_address: str, token: str, amount: float) -> str:
        tx_hash = self.lending_pool.functions.deposit(
            self.web3.to_checksum_address(token),
            self.web3.to_wei(amount, "ether"),
            self.web3.to_checksum_address(wallet_address),
            0  # referralCode
        ).transact({"from": wallet_address})
        return tx_hash.hex()