from aptos_sdk.client import RestClient
from aptos_sdk.account import Account
from app.core.config import APTOS_RPC_URL

class AptosClient:
    def __init__(self):
        self.client = RestClient(APTOS_RPC_URL)

    async def get_balance(self, address: str) -> float:
        balance = self.client.account_balance(address)
        return float(balance) / 10**8  # APT

    async def send_transaction(self, mnemonic: str, to_address: str, amount: float) -> str:
        account = Account.load_key(mnemonic)
        txn_hash = self.client.transfer(
            account,
            to_address,
            int(amount * 10**8)
        )
        return txn_hash