import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.agents.trading.agent import TradingAgent
from app.models.strategy import Strategy

@pytest.mark.asyncio
async def test_execute_strategies():
    # Mock user and strategies
    user = MagicMock()
    user.id = 1
    
    strategy = Strategy(
        id=1,
        user_id=1,
        name="DCA ETH",
        type="dca",
        blockchain="ethereum",
        from_token="ETH",
        to_token="USDC",
        amount=0.1,
        frequency=5
    )
    
    # Mock EthereumClient
    eth_client = AsyncMock()
    eth_client.swap.return_value = "0x123..."
    
    # Mock database
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = user
    db.query.return_value.filter.return_value.all.return_value = [strategy]
    
    # Test TradingAgent
    agent = TradingAgent(user.id)
    agent.db = db
    agent.strategies = [strategy]
    
    results = await agent.execute_strategies()
    assert "DCA ETH" in results
    assert len(results["DCA ETH"]) == 5