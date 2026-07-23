import json
import os
from typing import Dict

# Загрузка переводов
LOCALES_DIR = os.path.join(os.path.dirname(__file__), "locales")

translations: Dict[str, Dict[str, str]] = {}

# Загружаем все доступные языки
for lang_file in os.listdir(LOCALES_DIR):
    if lang_file.endswith(".json"):
        lang = lang_file.replace(".json", "")
        with open(os.path.join(LOCALES_DIR, lang_file), "r", encoding="utf-8") as f:
            translations[lang] = json.load(f)

def get_translation(lang: str, key: str, **kwargs) -> str:
    """Получить перевод по ключу с подстановкой переменных."""
    if lang not in translations:
        lang = "en"  # Язык по умолчанию
    
    translation = translations[lang].get(key, key)
    return translation.format(**kwargs)

# Пример использования:
# get_translation("ru", "start")
# get_translation("en", "wallet_connected", address="0x123...")