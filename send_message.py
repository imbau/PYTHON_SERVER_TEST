from call_ai import call_openrouter
import os
import requests
from dotenv import load_dotenv

load_dotenv()

WSP_TOKEN = "EAAU7yAI6f0ABQRCx1RXlUiSETR26jvaY6VCIfywL561lMpH3rZAUPBfqXYJY2Y79HkgR6BNZCreGFZAQc1UX1PKnZAyKrHmnjlPHpmvCxSGfdSdX6cICRyvS1KZCLL8UNRBTRhnI5HBbs5DUYapFJ7ecwby7omCoZBKNvoUQ61r07HSYF1wMwUBsHYOydxarwDndkZBbv5gCwIUZC1zNOW03jFCb7H6udwFOTMSEcndZA"
PHONE_NUMBER_ID = 904783266046247

def send_message(to, user_text):
    text = call_openrouter(user_text)

    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WSP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": text
        }
    }

    response = requests.post(url, headers=headers, json=data)
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.json())
    return response.json()

