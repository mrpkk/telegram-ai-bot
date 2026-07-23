from web3 import Web3
from web3.middleware import geth_poa_middleware
from app.core.config import WEB3_PROVIDER_URL
from app.services.blockchains.base import BlockchainClient
from typing import Dict, Any

class EthereumClient(BlockchainClient):
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    async def get_balance(self, address: str) -> float:
        return self.web3.from_wei(self.web3.eth.get_balance(address), "ether")

    async def send_transaction(self, to_address: str, amount: float, private_key: str) -> str:
        tx = {
            "to": to_address,
            "value": self.web3.to_wei(amount, "ether"),
            "gas": 21000,
            "gasPrice": self.web3.eth.gas_price,
            "nonce": self.web3.eth.get_transaction_count(self.web3.eth.account.from_key(private_key).address),
        }
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash.hex()

    async def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        return self.web3.eth.get_transaction(tx_hash)

    async def swap(self, from_token: str, to_token: str, amount: float) -> str:
        # Реализация через 1inch или Uniswap
        raise NotImplementedError("Swap not implemented for Ethereum yet.")