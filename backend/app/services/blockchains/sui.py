from pysui import SuiClient, SyncClient
from pysui.sui.sui_txn import SyncTransaction
from app.core.config import SUI_RPC_URL

class SuiClient:
    def __init__(self):
        self.client = SyncClient(SUI_RPC_URL)

    async def get_balance(self, address: str) -> float:
        balance = self.client.get_balance(address)
        return float(balance.total_balance) / 10**9  # SUI

    async def send_transaction(self, mnemonic: str, to_address: str, amount: float) -> str:
        tx = SyncTransaction(client=self.client)
        tx.transfer_sui(
            signer=tx.signer(mnemonic),
            recipient=to_address,
            amount=int(amount * 10**9)
        )
        result = tx.execute()
        return result.result.digest