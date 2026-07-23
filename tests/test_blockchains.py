import pytest
from unittest.mock import AsyncMock, patch
from app.services.blockchains.ethereum.client import EthereumClient

@pytest.mark.asyncio
async def test_get_balance():
    with patch("web3.Web3.eth.get_balance", return_value=10**18):
        client = EthereumClient()
        balance = await client.get_balance("0x123...")
        assert balance == 1.0