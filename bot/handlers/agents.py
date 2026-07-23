from aiogram import types
from aiogram.dispatcher.filters import Command
from app.core.i18n import get_translation
from app.models.user import User
from app.core.database import get_db
from app.services.agents.trading.agent import TradingAgent
# from app.services.agents.risk_agent import RiskAgent  # Временно отключено
from app.services.agents.yield_farming_agent import YieldAgent

async def handle_execute_strategies(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    agent = TradingAgent(user.id)
    results = await agent.execute_strategies()
    
    response = get_translation(user.language, "strategies_executed") + "\n"
    for strategy, tx_hashes in results.items():
        response += f"- {strategy}: {', '.join(tx_hashes[:3])}...\n"
    
    await message.reply(response)

async def handle_calculate_var(message: types.Message):
    await message.reply("RiskAgent временно отключён.")

async def handle_stress_test(message: types.Message):
    await message.reply("RiskAgent временно отключён.")

async def handle_optimize_yield(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    agent = YieldAgent(user.id)
    results = await agent.optimize_yield()
    
    response = get_translation(user.language, "yield_optimized") + "\n"
    for protocol, tx_hashes in results.items():
        response += f"- {protocol}: {', '.join(tx_hashes[:3])}...\n"
    
    await message.reply(response)

def setup_agents_handlers(dp):
    dp.message.register(handle_execute_strategies, Command("execute_strategies"))
    dp.message.register(handle_calculate_var, Command("var"))
    dp.message.register(handle_stress_test, Command("stress_test"))
    dp.message.register(handle_optimize_yield, Command("optimize_yield"))