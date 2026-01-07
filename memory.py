import requests
import os

def save_history(id, sender, to, direction, message, role):
    url = "http://tradeboom.epikasoftware.com/api/webhook/whatsapp"
    
    payload = {
        "conversation_id": str(id),
        "from": sender,
        "to": to,
        "direction": direction,
        "message": str(message),
        "role" : role # Asegúrate que tu API acepte este campo 'role'
    }

    try:
        print(f"📡 Intentando guardar en BD: {role} -> {message[:30]}...")
        response = requests.post(url, json=payload, timeout=20)
        print(f"✅ Respuesta BD: {response.status_code} - {response.text}")
        return {"success": True, "data": response.json()}
    except Exception as e:
        print(f"❌ Error crítico al guardar: {e}")
        return {"success": False, "error": str(e)}
