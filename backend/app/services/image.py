import openai
from app.core.config import DALLE_API_KEY

# Инициализация OpenAI для DALL·E
openai.api_key = DALLE_API_KEY

# Генерация изображения
async def generate_image(prompt: str, size: str = "1024x1024") -> str:
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size=size
    )
    return response["data"][0]["url"]

# OCR (распознавание текста на изображении)
async def extract_text_from_image(image_path: str) -> str:
    import pytesseract
    from PIL import Image
    
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text