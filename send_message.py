from call_ai import call_openrouter
import os
import requests
import json

WSP_TOKEN = os.getenv('WSP_TOKEN')
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')

def send_message(to, messages_override=None):
    # Si no recibimos mensajes, fallamos (la lógica ahora está en server.py)
    if messages_override is None:
        print("❌ Error: send_message llamado sin mensajes")
        return {"message": ""}
        
    messages = messages_override

    # DEBUG: Ver cómo llega el diálogo a la IA ahora
    print("🧠 CONTEXTO IA (Últimos 3 mensajes):")
    print(json.dumps(messages[-3:], indent=2, ensure_ascii=False))

    # Llamar a OpenRouter
    text = call_openrouter(messages)
    
    # Enviar a WhatsApp
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WSP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    
    try:
        res = requests.post(url, headers=headers, json=data)
        print(f"✅ Enviado a WSP: {res.status_code}")
    except Exception as e:
        print(f"❌ Error enviando a WSP: {e}")

    return {"message": text}
