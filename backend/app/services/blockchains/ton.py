from pytonlib import TonlibClient
from tonsdk.utils import to_nano, from_nano
from tonsdk.contract.wallet import Wallets, WalletVersionEnum
from app.core.config import TON_RPC_URL

class TONClient:
    def __init__(self):
        self.client = TonlibClient(
            ls_index=2,
            config="https://ton.org/global.config.json",
            keystore="~/ton_keystore"
        )
        self.client.init()

    async def get_balance(self, address: str) -> float:
        balance = await self.client.get_balance(address)
        return from_nano(balance, "ton")

    async def send_transaction(self, mnemonic: str, to_address: str, amount: float) -> str:
        wallet = Wallets.create(WalletVersionEnum.v4r2, mnemonic.split())
        query = wallet.create_transfer_message(
            to_addr=to_address,
            amount=to_nano(amount, "ton"),
            seqno=await self.client.get_seqno(wallet.address.to_string())
        )
        await self.client.raw_send_message(query['message'].to_boc(False))
        return query['hash'].hex()