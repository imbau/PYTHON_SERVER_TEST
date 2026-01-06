from call_ai import call_openrouter
import os
import requests

WSP_TOKEN = os.getenv('WSP_TOKEN')
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')

def get_history(conversation_id):
    url = f"http://tradeboom.epikasoftware.com/api/whatsapp/conversation/{conversation_id}"
    res = requests.get(url, timeout=20)
    res.raise_for_status()
    return res.json()

def format_messages(history):
    # Si es dict → intentamos sacar data
    if isinstance(history, dict):
        history = history.get("data", [])
    # Si no es lista, forzamos lista vacía
    if not isinstance(history, list):
        history = []
    
    formatted = [
        {
            "role": h.get("role", "user"),
            "content": h.get("message", "")
        }
        for h in history
    ]
    
    # 🔍 DEBUG: Ver qué mensajes estamos enviando a la IA
    print("=" * 50)
    print("📨 MENSAJES QUE SE ENVÍAN A LA IA:")
    for i, msg in enumerate(formatted):
        print(f"{i+1}. [{msg['role']}]: {msg['content'][:100]}")
    print("=" * 50)
    
    return formatted

def send_message(to):
    conversation_id = to
    
    # Obtener historial
    history = get_history(conversation_id)
    print(f"📖 Historial recibido de la API: {history}")
    
    # Formatear mensajes
    messages = format_messages(history)
    
    # Llamar a la IA
    print(f"🤖 Llamando a OpenRouter con {len(messages)} mensajes...")
    text = call_openrouter(messages)
    print(f"✅ Respuesta de la IA: {text[:200]}")
    
    # Enviar por WhatsApp
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
