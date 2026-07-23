from cosmos_sdk.client.lcd import LCDClient
from cosmos_sdk.key.mnemonic import MnemonicKey
from app.core.config import COSMOS_RPC_URL

class CosmosClient:
    def __init__(self):
        self.client = LCDClient(
            chain_id="cosmoshub-4",
            url=COSMOS_RPC_URL
        )

    async def get_balance(self, address: str) -> float:
        balance = self.client.bank.balance(address)
        return float(balance[0].amount) / 10**6  # ATOM

    async def send_transaction(self, mnemonic: str, to_address: str, amount: float) -> str:
        mk = MnemonicKey(mnemonic=mnemonic)
        wallet = self.client.wallet(mk)
        tx = wallet.create_and_sign_tx(
            msgs=[{
                "type": "cosmos-sdk/MsgSend",
                "value": {
                    "from_address": wallet.key.address,
                    "to_address": to_address,
                    "amount": [{"denom": "uatom", "amount": str(int(amount * 10**6))}]
                }
            }]
        )
        result = self.client.tx.broadcast(tx)
        return result.txhash