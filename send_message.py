from call_ai import call_openrouter
import os
import requests

WSP_TOKEN = os.getenv('WSP_TOKEN')
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')

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
    return {
        "whatsapp_response": response.json(),
        "message": text
    }
