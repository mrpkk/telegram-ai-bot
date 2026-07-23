from aiogram import types, Dispatcher
from app.core.i18n import get_translation
from app.models.user import User
from app.models.analytics import UserAnalytics
from app.core.database import get_db

async def handle_stats(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    analytics = db.query(UserAnalytics).filter(UserAnalytics.user_id == user.id).first()
    
    if not analytics:
        await message.reply(get_translation(user.language, "stats_error"))
        return
    
    await message.reply(get_translation(
        user.language, 
        "stats", 
        query_count=analytics.query_count,
        last_query_at=analytics.last_query_at,
        avg_response_time=analytics.avg_response_time
    ))

def setup_analytics_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_stats, commands=["stats"])