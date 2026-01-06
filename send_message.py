from call_ai import call_openrouter
import os
import requests

WSP_TOKEN = os.getenv('WSP_TOKEN')
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')

def get_history(conversation_id):
    url = f"http://tradeboom.epikasoftware.com/api/webhook/whatsapp/{conversation_id}"
    res = requests.get(url, timeout=20)
    res.raise_for_status()
    return res.json()

def format_messages(history):
    data = history.get("data", history)

    return [
        {
            "role": h.get("role", "user"),
            "content": h.get("message", "")
        }
        for h in data
    ]

def send_message(to):
    conversation_id = to
    history = get_history(conversation_id)
    messages = format_messages(history)
    text = call_openrouter(messages)

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
