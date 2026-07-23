from aiogram import types
from aiogram.dispatcher.filters import ContentTypeFilter
from app.core.i18n import get_translation
from app.models.user import User
from app.core.database import get_db
from app.services.voice import speech_to_text, text_to_speech
import os

async def handle_voice_message(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    # Сохраняем голосовое сообщение
    voice_file = await message.voice.get_file()
    voice_path = f"temp/voice_{message.message_id}.ogg"
    os.makedirs("temp", exist_ok=True)
    await voice_file.download(voice_path)
    
    # Распознаём речь
    text = await speech_to_text(voice_path)
    await message.reply(get_translation(user.language, "voice_recognized", text=text))
    
    # Отправляем ответ голосом
    audio = await text_to_speech(get_translation(user.language, "ask_response", answer=text))
    await message.reply_voice(voice=audio)

def setup_voice_handlers(dp):
    dp.register_message_handler(handle_voice_message, ContentTypeFilter(types.ContentType.VOICE))