from aiogram import types
from app.core.i18n import get_translation
from app.models.user import User
from app.core.database import get_db
from app.services.defi import get_wallet_balance, connect_wallet

async def handle_wallet(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()

    # Создаём клавиатуру для подключения кошелька
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(get_translation(user.language, "wallet_connect")))

    await message.reply(get_translation(user.language, "wallet_placeholder"), reply_markup=keyboard)

async def handle_wallet_connect(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()

    # Заглушка для подключения кошелька
    wallet_address = "0x1234567890abcdef1234567890abcdef12345678"

    if await connect_wallet(wallet_address):
        user.wallet_address = wallet_address
        db.commit()
        await message.reply(get_translation(user.language, "wallet_connected", address=wallet_address))
    else:
        await message.reply(get_translation(user.language, "wallet_error", error="Не удалось подключить кошелёк"))

async def handle_balance(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()

    if not user.wallet_address:
        await message.reply(get_translation(user.language, "wallet_not_connected"))
        return

    balance = await get_wallet_balance(user.wallet_address)
    await message.reply(get_translation(user.language, "balance", balance=balance))


def setup_wallet_handlers(dp):
    """Настройка обработчиков для кошелька."""
    dp.register_message_handler(handle_wallet, commands=['wallet'])
    dp.register_message_handler(handle_wallet_connect, lambda message: get_translation(message.from_user.language, "wallet_connect") in message.text)
    dp.register_message_handler(handle_balance, commands=['balance'])