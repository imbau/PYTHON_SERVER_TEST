from flask import Flask, request, jsonify
from call_ai import call_openrouter
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.post("/responder")
def responder():
    WSP_TOKEN = os.getenv("WSP_TOKEN")
    PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
    
    data = request.get_json()
    user_text = data.get("user_text", "")
    user_number = data.get("user_number", "")
    
    # HARDFIX: Reemplazar tu número específico
    if user_number == "5492216982208":
        user_number = "54221156982208"
    
    if not user_text or not user_number or not WSP_TOKEN or not PHONE_NUMBER_ID:
        print(f"❌ Datos incompletos: text={bool(user_text)}, number={bool(user_number)}")
        return jsonify({"error": "Configuración incompleta"}), 400
    
    # Generar respuesta con IA
    try:
        ai_response = call_openrouter(user_text)
    except Exception as e:
        print(f"❌ Error IA: {e}")
        return jsonify({"error": "Error en IA"}), 500
    
    # Enviar a WhatsApp
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WSP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": user_number,
        "type": "text",
        "text": {"body": ai_response}
    }
    
    try:
        wsp_response = requests.post(url, headers=headers, json=payload, timeout=30)
        response_json = wsp_response.json()
        
        if wsp_response.status_code != 200:
            print(f"❌ WhatsApp error {wsp_response.status_code}: {response_json}")
        
        return jsonify({
            "success": wsp_response.status_code == 200,
            "wsp_status": wsp_response.status_code,
            "wsp_response": response_json
        })
        
    except Exception as e:
        print(f"❌ Error enviando a WhatsApp: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
