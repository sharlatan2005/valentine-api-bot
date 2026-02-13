import aiohttp
from PIL import Image
from io import BytesIO
import logging
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)

URL = "https://valentine-bot-api.prasionissy.workers.dev"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('IMG_TOKEN')}",
    "Content-Type": "application/json",
}

PROMPT = """Abstract geometric paper collage, modernist bauhaus constructivism poster style, torn paper edges, layered cutout shapes, scanned paper textures, monochrome black/white with deep red accent, editorial graphic design, high contrast, minimal palette, matte print look, vintage print grain, composition dominated by a single large heart as the absolute central focal point, oversized valentine motif, heart as the primary and main subject, heart shape cut from textured deep red paper, all geometric elements secondary and framing the heart, balanced asymmetry, bold graphic statement"""
async def generate_valentine_image(username: str = None) -> Image.Image:
    """Асинхронно генерирует валентинку через API"""
    
    if username:
        prompt = f"{PROMPT}, handwritten text '@{username}' in messy pencil on one of the paper pieces"
    else:
        prompt = PROMPT
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            URL, 
            headers=HEADERS, 
            json={"prompt": prompt},
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            response.raise_for_status()
            content = await response.read()
            return Image.open(BytesIO(content))


if __name__ == "__main__":
    async def test():
        try:
            print("🚀 Генерация тестового изображения...")
            img = await generate_valentine_image("gottl1ebb")
            img.show()
            print("✅ Изображение получено!")
            
            input("Нажмите Enter для выхода...")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            input("Нажмите Enter для выхода...")
    
    asyncio.run(test())