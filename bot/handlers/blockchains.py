from aiogram import types
from aiogram.dispatcher import F
from app.core.i18n import get_translation
from app.models.user import User
from app.core.database import get_db
from app.services.blockchains.ethereum import EthereumClient
from app.services.blockchains.solana import SolanaClient
from app.services.blockchains.ton import TONClient
from app.services.blockchains.cosmos import CosmosClient
from app.services.blockchains.sui import SuiClient
from app.services.blockchains.aptos import AptosClient

async def handle_ton_balance(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user.wallet_address:
        await message.reply(get_translation(user.language, "wallet_not_connected"))
        return
    
    client = TONClient()
    balance = await client.get_balance(user.wallet_address)
    await message.reply(get_translation(user.language, "balance", balance=balance, symbol="TON"))

async def handle_cosmos_balance(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user.wallet_address:
        await message.reply(get_translation(user.language, "wallet_not_connected"))
        return
    
    client = CosmosClient()
    balance = await client.get_balance(user.wallet_address)
    await message.reply(get_translation(user.language, "balance", balance=balance, symbol="ATOM"))

async def handle_sui_balance(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user.wallet_address:
        await message.reply(get_translation(user.language, "wallet_not_connected"))
        return
    
    client = SuiClient()
    balance = await client.get_balance(user.wallet_address)
    await message.reply(get_translation(user.language, "balance", balance=balance, symbol="SUI"))

async def handle_aptos_balance(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user.wallet_address:
        await message.reply(get_translation(user.language, "wallet_not_connected"))
        return
    
    client = AptosClient()
    balance = await client.get_balance(user.wallet_address)
    await message.reply(get_translation(user.language, "balance", balance=balance, symbol="APT"))

def setup_blockchains_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_ton_balance, commands=["ton_balance"])
    dp.register_message_handler(handle_cosmos_balance, commands=["cosmos_balance"])
    dp.register_message_handler(handle_sui_balance, commands=["sui_balance"])
    dp.register_message_handler(handle_aptos_balance, commands=["aptos_balance"])