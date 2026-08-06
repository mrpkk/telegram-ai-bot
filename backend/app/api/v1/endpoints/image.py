import os
import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.image import generate_image, extract_text_from_image

router = APIRouter()

@router.post("/generate")
async def generate_image_endpoint(prompt: str):
    try:
        url = await generate_image(prompt)
        return {"url": url}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ocr")
async def ocr_endpoint(image: UploadFile = File(...)):
    # Tesseract работает с файлом на диске — сохраняем upload во временный файл
    suffix = os.path.splitext(image.filename or "")[1] or ".png"
    fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(await image.read())
        text = await extract_text_from_image(tmp_path)
        return {"text": text}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
