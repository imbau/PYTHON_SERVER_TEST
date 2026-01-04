from flask import Flask, request, jsonify
from call_ai import call_openrouter
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

WSP_TOKEN = os.getenv("WSP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

print(f"🔑 WSP_TOKEN cargado: {WSP_TOKEN[:20] if WSP_TOKEN else 'NO CONFIGURADO'}...")
print(f"📱 PHONE_NUMBER_ID: {PHONE_NUMBER_ID}")

@app.post("/responder")
def responder():
    data = request.get_json()
    user_text = data.get("user_text", "")
    user_number = data.get("user_number", "")
    
    print("=" * 50)
    print("📩 DATOS RECIBIDOS:")
    print(f"   Texto: {user_text}")
    print(f"   Número: {user_number}")
    print("=" * 50)
    
    # Generar respuesta con IA
    print("🤖 Llamando a OpenRouter...")
    ai_response = call_openrouter(user_text)
    print(f"✅ Respuesta de IA: {ai_response[:100]}...")
    
    # Enviar mensaje por WhatsApp
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WSP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": user_number,
        "type": "text",
        "text": {
            "body": ai_response
        }
    }
    
    print("📤 ENVIANDO A WHATSAPP:")
    print(f"   URL: {url}")
    print(f"   To: {user_number}")
    print(f"   Body length: {len(ai_response)} caracteres")
    
    try:
        wsp_response = requests.post(url, headers=headers, json=payload)
        print(f"📬 WhatsApp STATUS: {wsp_response.status_code}")
        print(f"📬 WhatsApp RESPONSE: {wsp_response.json()}")
        
        return jsonify({
            "reply_text": ai_response,
            "wsp_status": wsp_response.status_code,
            "wsp_response": wsp_response.json()
        })
    except Exception as e:
        print(f"❌ ERROR enviando a WhatsApp: {e}")
        return jsonify({
            "error": str(e),
            "reply_text": ai_response
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
