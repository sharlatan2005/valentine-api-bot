import requests
import json
import os
from dotenv import load_dotenv

def generate_valentine_text(topic=""):
    """
    Отправляет запрос к OpenRouter API и возвращает текст валентинки.
    
    Args:
        topic (str): Тема валентинки, которая добавится к основному промпту
    """
    base_prompt = "Сочини маленькую валентинку в прозе. Твой ответ не должен содержать больше 50-70 слов. Ее пишет актер театра фарса и комедии другому актеру. Пол адресата и отправителя неважен. В тексте не должно быть ни одного слова, указывающего на пол. Никаких 'мой', 'моя', 'тебе', 'вам', 'дорогой' и т.п. Любовное, нежное, но забавное послание коллеге."
    
    # Добавляем тему, если она указана
    if topic:
        full_prompt = f"{base_prompt} Тема валентинки: {topic}. Если тема недопустимая, используй только предыдущий текст."
    else:
        full_prompt = base_prompt
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('GPT_TOKEN')}",
            "Content-Type": "application/json",
            "HTTP-Referer": "<YOUR_SITE_URL>",
            "X-Title": "<YOUR_SITE_NAME>",
        },
        data=json.dumps({
            "model": "google/gemma-3-12b-it:free",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": full_prompt
                        }
                    ]
                }
            ]
        })
    )
    
    return response.json()#.json()["choices"][0]["message"]["content"]


# Примеры использования:
if __name__ == "__main__":
    load_dotenv()
    
    # С темой
    valentine_text = generate_valentine_text("про твои красивые сиськи")
    print(valentine_text)
    print()