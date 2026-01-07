import requests

BASE_URL = "http://tradeboom.epikasoftware.com/api"

def save_history(id, sender, to, direction, message, role):
    if direction == "in":
        url = f"{BASE_URL}/webhook/whatsapp"
    else:
        url = f"{BASE_URL}/whatsapp/bot-message"

    payload = {
        "conversation_id": str(id),
        "sender": sender,
        "to": to,
        "message": str(message)
    }

    try:
        print(f"📡 Guardando en BD ({direction}): {message[:40]}...")
        response = requests.post(url, json=payload, timeout=20)
        print(f"✅ BD: {response.status_code} - {response.text}")
        return True
    except Exception as e:
        print(f"❌ Error BD: {e}")
        return False
