from typing import Dict, List
from app.models.user import User
from app.models.strategy import Strategy
from app.core.database import get_db
from app.services.agents.trading.agent import TradingAgent