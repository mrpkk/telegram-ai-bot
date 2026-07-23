from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.publickey import PublicKey
from app.core.config import SOLANA_RPC_URL
from app.services.blockchains.base import BlockchainClient
from typing import Dict, Any

class SolanaClient(BlockchainClient):
    def __init__(self):
        self.client = AsyncClient(SOLANA_RPC_URL)

    async def get_balance(self, address: str) -> float:
        balance = await self.client.get_balance(PublicKey(address))
        return balance["result"]["value"] / 10**9  # SOL

    async def send_transaction(self, to_address: str, amount: float, private_key: str) -> str:
        from_public_key = Keypair.from_secret_key(bytes.fromhex(private_key)).public_key
        to_public_key = PublicKey(to_address)
        tx = Transaction().add(
            spl_token.transfer(
                spl_token.TransferParams(
                    program_id=PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
                    source=from_public_key,
                    dest=to_public_key,
                    owner=from_public_key,
                    amount=int(amount * 10**9),
                )
            )
        )
        tx_hash = await self.client.send_transaction(tx, Keypair.from_secret_key(bytes.fromhex(private_key)))
        return tx_hash["result"]

    async def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        return await self.client.get_transaction(PublicKey(tx_hash))

    async def swap(self, from_token: str, to_token: str, amount: float) -> str:
        # Реализация через Raydium или Jupiter
        raise NotImplementedError("Swap not implemented for Solana yet.")