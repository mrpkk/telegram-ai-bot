from tonsdk.utils import to_nano, from_nano
from tonsdk.contract.wallet import Wallets, WalletVersionEnum

def create_wallet(mnemonic: str) -> Wallets:
    """Создать кошелёк TON из мнемоники."""
    return Wallets.create(WalletVersionEnum.v4r2, mnemonic.split())