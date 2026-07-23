from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.image import generate_image, extract_text_from_image

router = APIRouter()

@router.post("/generate")
async def generate_image_endpoint(prompt: str):
    try:
        url = await generate_image(prompt)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ocr")
async def ocr_endpoint(image: UploadFile = File(...)):
    try:
        text = await extract_text_from_image(image.file)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))