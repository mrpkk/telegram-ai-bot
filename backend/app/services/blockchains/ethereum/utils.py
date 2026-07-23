from web3 import Web3

def validate_address(address: str) -> bool:
    """Проверить валидность Ethereum-адреса."""
    return Web3.is_address(address)