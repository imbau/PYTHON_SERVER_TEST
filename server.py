from flask import Flask, request, jsonify
from call_ai import call_openrouter
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

WSP_TOKEN = os.getenv("WSP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

@app.post("/responder")
def responder():
    data = request.get_json()
    user_text = data.get("user_text", "")
    user_number = data.get("user_number", "")
    
    print("📩 Mensaje recibido:", user_text)
    print("📞 Número:", user_number)
    
    # Generar respuesta con IA
    ai_response = call_openrouter(user_text)
    
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
    
    wsp_response = requests.post(url, headers=headers, json=payload)
    print("WhatsApp STATUS:", wsp_response.status_code)
    print("WhatsApp RESPONSE:", wsp_response.json())
    
    return jsonify({
        "reply_text": ai_response,
        "wsp_status": wsp_response.status_code
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
