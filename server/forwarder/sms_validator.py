import requests
import json
from django.conf import settings


def valid_sms(text: str) -> bool:
    # URL for the API request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}"

    # Data to be sent in the POST request
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"""Moderate the following SMS in English, Bangla, or Banglish. If it contains sexual, harassment, attacking, hateful, romantic, or hurtful words, reply with “BAD” in plain text. If the SMS does not contain any of these words, reply with “GOOD” in plain text.
                        SMS: ```{text}```""",
                    }
                ]
            }
        ]
    }

    # Headers for the request
    headers = {"Content-Type": "application/json"}

    # Send the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check if the request was successful and return the response
    if response.status_code == 200:
        return "GOOD" in response.json()["candidates"][0]["content"]["parts"][0]["text"]

    else:
        return False
