import requests
import json

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer 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",
    "Content-Type": "application/json",
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  data=json.dumps({
    "model": "google/gemma-3-4b-it:free",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Текст любовной валентинки от одного актера театра фарса и комедии 'ВиД' другому. Без личностей и гендеров. Просто обращение. Шуточный и одновременно ласковый."
          }
        ]
      }
    ]
  })
)

json_response = response.json()
content = json_response.get('choices', [{}])[0].get('message', {}).get('content')
if content:
    print("Content:", content)
else:
    print("Content not found")