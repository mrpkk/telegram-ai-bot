from aiogram import types
from aiogram.dispatcher.filters import Command
from app.core.i18n import get_translation
from app.models.user import User
from app.core.database import get_db
from app.services.defi import swap_tokens

async def handle_swap(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user.wallet_address:
        await message.reply(get_translation(user.language, "wallet_not_connected"))
        return
    
    # Пример команды: /swap ETH USDC 0.1
    args = message.text.split()
    if len(args) != 4:
        await message.reply(get_translation(user.language, "swap_usage"))
        return
    
    from_token, to_token, amount = args[1], args[2], float(args[3])
    result = await swap_tokens(from_token, to_token, amount, user.wallet_address)
    await message.reply(get_translation(user.language, "swap_success", result=result))

def setup_defi_handlers(dp):
    dp.message.register(handle_swap, Command("swap"))