from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from app.core.config import TELEGRAM_BOT_TOKEN
from app.core.database import Base, engine

# Создаём таблицы в базе данных
Base.metadata.create_all(bind=engine)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Импорт обработчиков
from bot.handlers import setup_ai_handlers, setup_payments_handlers, setup_wallet_handlers, setup_defi_handlers, setup_voice_handlers, setup_analytics_handlers, setup_agents_handlers, setup_blockchains_handlers
setup_ai_handlers(dp)
setup_payments_handlers(dp)
setup_wallet_handlers(dp)
setup_defi_handlers(dp)
setup_voice_handlers(dp)
setup_analytics_handlers(dp)
setup_agents_handlers(dp)
setup_blockchains_handlers(dp)

def run_bot():
    """Запуск Telegram-бота в отдельном потоке."""
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    run_bot()