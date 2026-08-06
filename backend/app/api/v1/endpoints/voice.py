from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.voice import speech_to_text, text_to_speech

router = APIRouter()

@router.post("/stt")
async def speech_to_text_endpoint(audio: UploadFile = File(...)):
    try:
        text = await speech_to_text(audio.file)
        return {"text": text}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts")
async def text_to_speech_endpoint(text: str):
    try:
        audio = await text_to_speech(text)
        return {"audio": audio}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
