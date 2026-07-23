from web3 import Web3
from web3.contract import Contract
from app.core.config import WEB3_PROVIDER_URL, LIDO_STETH_ADDRESS

class LidoClient:
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))
        self.steth = self.web3.eth.contract(
            address=LIDO_STETH_ADDRESS,
            abi=self._get_abi()
        )

    def _get_abi(self) -> list:
        # ABI для Lido stETH
        return [
            {
                "inputs": [{"internalType": "address", "name": "_referral", "type": "address"}],
                "name": "submit",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "payable",
                "type": "function"
            }
        ]

    async def stake(self, wallet_address: str, amount: float) -> str:
        tx_hash = self.steth.functions.submit(
            self.web3.to_checksum_address("0x0000000000000000000000000000000000000000")  # referral
        ).transact({
            "from": wallet_address,
            "value": self.web3.to_wei(amount, "ether")
        })
        return tx_hash.hex()