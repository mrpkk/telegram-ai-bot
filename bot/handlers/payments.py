from aiogram import types
from app.core.i18n import get_translation
from app.models.user import User
from app.core.database import get_db
from app.services.payments import create_subscription_checkout

def setup_payments_handlers(dp):
    """Настройка обработчиков для платежей."""
    dp.register_message_handler(handle_subscribe, commands=['subscribe'])
    dp.register_callback_query_handler(handle_subscribe_change, lambda c: c.data.startswith('subscribe_'))


async def handle_subscribe(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()

    # Создаём клавиатуру для выбора тарифа
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(get_translation(user.language, "subscribe_pro"), callback_data="subscribe_pro"))
    keyboard.add(types.InlineKeyboardButton(get_translation(user.language, "subscribe_enterprise"), callback_data="subscribe_enterprise"))

    await message.reply(get_translation(user.language, "subscribe_select"), reply_markup=keyboard)


async def handle_subscribe_change(callback_query: types.CallbackQuery):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == callback_query.from_user.id).first()

    plan = callback_query.data.replace("subscribe_", "")
    if plan in ["pro", "enterprise"]:
        checkout_url = await create_subscription_checkout(user.telegram_id, plan)
        await callback_query.message.edit_text(
            get_translation(user.language, "subscribe_payment_link", link=checkout_url)
        )
    else:
        await callback_query.answer(get_translation(user.language, "subscribe_error"), show_alert=True)