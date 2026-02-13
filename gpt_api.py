import requests
import json
import os
from dotenv import load_dotenv

def generate_valentine_text():
    """
    Отправляет запрос к OpenRouter API и возвращает текст валентинки.
    """
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('GPT_TOKEN')}",
            "Content-Type": "application/json",
            "HTTP-Referer": "<YOUR_SITE_URL>",
            "X-Title": "<YOUR_SITE_NAME>",
        },
        data=json.dumps({
            "model": "google/gemma-3-4b-it:free",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Сочини маленькую валентинку в прозе. Ее пишет актер театра фарса и комедии другому актеру. Пол адресата и отправителя неважен. В тексте не должно быть ни одного слова, указывающего на пол. Никаких 'мой', 'моя', 'тебе', 'вам', 'дорогой' и т.п. Любовное, нежное, но забавное послание коллеге."
                        }
                    ]
                }
            ]
        })
    )
    
    return response.json()["choices"][0]["message"]["content"]


# Пример использования:
if __name__ == "__main__":
    load_dotenv()
    valentine_text = generate_valentine_text()
    print(valentine_text)