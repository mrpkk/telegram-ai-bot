"""Сервис голоса: STT (Whisper) и TTS (ElevenLabs)."""
import os

from fastapi import HTTPException


async def speech_to_text(audio_file_path: str) -> str:
    """Распознавание речи через OpenAI Whisper (если ключ настроен)."""
    api_key = os.getenv("WHISPER_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise HTTPException(503, "Распознавание речи не настроено (нет WHISPER_API_KEY)")

    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=api_key)
    with open(audio_file_path, "rb") as audio:
        transcript = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio,
        )
    return transcript.text


async def text_to_speech(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> bytes:
    """Синтез речи через ElevenLabs (если ключ настроен)."""
    api_key = os.getenv("ELEVENLABS_API_KEY", "")
    if not api_key:
        raise HTTPException(503, "Синтез речи не настроен (нет ELEVENLABS_API_KEY)")

    import httpx
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key,
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=data, headers=headers)
        resp.raise_for_status()
        return resp.content
