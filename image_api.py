import requests
from PIL import Image
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

URL = "https://valentine-bot-api.prasionissy.workers.dev"
HEADERS = {
    "Authorization": "Bearer IFkHiETtB1KpY3XgViq1K1u9SFVWUu7xu9hWNXo_",
    "Content-Type": "application/json",
}

PROMPT = """Valentine Abstract geometric paper collage, modernist bauhaus constructivism style, torn paper edges, layered cutout shapes, scanned paper textures, monochrome black/white with deep red accent, editorial graphic design, high contrast, minimal palette, matte print look, vintage print grain"""

def generate_valentine_image(username: str = None) -> Image.Image:
    """Генерирует валентинку через API"""
    
    # Добавляем username в промпт, если он передан
    if username:
        prompt = f"{PROMPT}, handwritten text '@{username}' in messy pencil on one of the paper pieces"
    else:
        prompt = PROMPT
    
    data = {"prompt": prompt}
    
    try:
        print("🔄 Отправка запроса к API...")
        response = requests.post(URL, headers=HEADERS, json=data, timeout=60)
        response.raise_for_status()
        
        print("✅ Изображение получено!")
        img = Image.open(BytesIO(response.content))
        return img
        
    except Exception as e:
        logger.error(f"Ошибка генерации изображения: {e}")
        raise Exception(f"Не удалось сгенерировать изображение: {str(e)}")


if __name__ == "__main__":
    # Этот блок выполняется только при прямом запуске файла
    try:
        print("🚀 Генерация тестового изображения...")
        img = generate_valentine_image("gottl1ebb")  # Можно указать тестовый username
        img.show()  # Показываем изображение
        print("💾 Изображение сохранено как test_valentine.png")
        print("✅ Готово!")
        
        # Держим окно открытым
        input("Нажмите Enter для выхода...")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        input("Нажмите Enter для выхода...")