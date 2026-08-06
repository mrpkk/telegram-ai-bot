"""Сервис изображений: генерация (DALL·E) и OCR (локальный Tesseract)."""
import os
import subprocess

from fastapi import HTTPException


async def generate_image(prompt: str, size: str = "1024x1024") -> str:
    """Генерация изображения через OpenAI DALL·E (если ключ настроен)."""
    api_key = os.getenv("DALLE_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise HTTPException(503, "Генерация изображений не настроена (нет DALLE_API_KEY)")

    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=api_key)
    resp = await client.images.generate(model="dall-e-3", prompt=prompt, size=size, n=1)
    return resp.data[0].url


async def extract_text_from_image(image_path: str) -> str:
    """OCR — локальный Tesseract (без внешних сервисов и ключей)."""
    if not os.path.exists(image_path):
        raise HTTPException(400, "Файл не найден")

    try:
        result = subprocess.run(
            ["tesseract", image_path, "stdout", "-l", "rus+eng"],
            capture_output=True, text=True, timeout=30,
        )
        text = result.stdout.strip()
        if not text and result.stderr:
            # Пробуем без языкового пакета rus
            result = subprocess.run(
                ["tesseract", image_path, "stdout"],
                capture_output=True, text=True, timeout=30,
            )
            text = result.stdout.strip()
        return text
    except FileNotFoundError:
        raise HTTPException(503, "Tesseract OCR не установлен на сервере")
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "Превышено время OCR-обработки")
