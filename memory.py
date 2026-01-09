import requests
from call_ai import call_openrouter

BASE_URL = "http://tradeboom.epikasoftware.com/api"

def save_history(id, sender, to, direction, message, role, name=None):
    url = f"{BASE_URL}/webhook/whatsapp"
    if name is None:
        payload = {
            "conversation_id": str(id),
            "sender": sender,
            "to": to,
            "message": str(message),
            "role": role
        }
    else:
        payload = {
            "conversation_id": str(id),
            "sender": sender,
            "to": to,
            "message": str(message),
            "role": role,
            "name": name
        }

    try:
        print(f"📡 Guardando en BD ({direction}): {message[:40]}...")
        response = requests.post(url, json=payload, timeout=20)
        print(f"✅ BD: {response.status_code} - {response.text}")
        return True
    except Exception as e:
        print(f"❌ Error BD: {e}")
        return False

def find_name(conversation_id):
    url = f"{BASE_URL}/whatsapp/conversation/{conversation_id}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None

        history_messages = response.json()

        text = " ".join(
            msg["content"]
            for msg in history_messages
            if msg.get("role") == "user" and isinstance(msg.get("content"), str)
        )


        messages = [
            { "role": "system",
             "content": "Eres un experto analítico de conversaciones, y tu trabajo es revisar todos los mensajes del usuario y extraer y retornar únicamente el nombre del usuario. Si no encuentras ningún nombre, solo devuelve 'nuevo'"
            },
            { "role": "user",
             "content": text
            }
        ]

        name = call_openrouter(messages)

        if not name or name.strip().lower() == "nuevo":
            return None
        
        return name.strip()
        
    except Exception as e:
        print(f"❌ Error buscando nombre: {e}")
        return None
