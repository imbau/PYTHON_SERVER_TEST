from flask import Flask, request, jsonify
from call_ai import call_openrouter
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

sys.stdout.flush()
sys.stderr.flush()

def log(message):
    print(message, flush=True)

@app.post("/responder")
def responder():
    log("\n" + "=" * 60)
    log("🔔 NUEVO MENSAJE RECIBIDO")
    log("=" * 60)
    
    WSP_TOKEN = os.getenv("WSP_TOKEN")
    PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
    
    log(f"🔑 WSP_TOKEN: {'✅ Configurado (' + WSP_TOKEN[:20] + '...)' if WSP_TOKEN else '❌ NO CONFIGURADO'}")
    log(f"📱 PHONE_NUMBER_ID: {PHONE_NUMBER_ID if PHONE_NUMBER_ID else '❌ NO CONFIGURADO'}")
    
    data = request.get_json()
    log(f"📦 Request body completo: {data}")
    
    user_text = data.get("user_text", "")
    user_number = data.get("user_number", "")
    
    # HARDFIX: Reemplazar tu número específico
    if user_number == "5492216982208":
        user_number = "54221156982208"
        log(f"🔧 Número reemplazado automáticamente: {user_number}")
    
    log(f"📩 Texto del usuario: '{user_text}'")
    log(f"📞 Número del usuario: '{user_number}'")
    
    if not user_text or not user_number:
        log("❌ Faltan datos en el request")
        return jsonify({"error": "Faltan user_text o user_number"}), 400
    
    if not WSP_TOKEN or not PHONE_NUMBER_ID:
        log("❌ Faltan variables de entorno")
        return jsonify({"error": "Configuración incompleta"}), 500
    
    log("🤖 Llamando a OpenRouter...")
    try:
        ai_response = call_openrouter(user_text)
        log(f"✅ IA respondió ({len(ai_response)} caracteres):")
        log(f"   '{ai_response[:150]}{'...' if len(ai_response) > 150 else ''}'")
    except Exception as e:
        log(f"❌ Error en IA: {e}")
        return jsonify({"error": f"Error en IA: {str(e)}"}), 500
    
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
    
    log(f"📤 Enviando a WhatsApp...")
    log(f"   URL: {url}")
    log(f"   Destino: {user_number}")
    
    try:
        wsp_response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        log(f"📬 WhatsApp STATUS: {wsp_response.status_code}")
        log(f"📬 WhatsApp RESPONSE: {wsp_response.text}")
        
        response_json = wsp_response.json()
        
        if wsp_response.status_code == 200:
            log("✅ Mensaje enviado exitosamente a WhatsApp")
        else:
            log(f"⚠️ WhatsApp respondió con error: {response_json}")
        
        log("=" * 60 + "\n")
        
        return jsonify({
            "success": wsp_response.status_code == 200,
            "reply_text": ai_response,
            "wsp_status": wsp_response.status_code,
            "wsp_response": response_json
        })
        
    except requests.exceptions.Timeout:
        log("❌ TIMEOUT al enviar a WhatsApp (30s)")
        return jsonify({"error": "Timeout enviando mensaje"}), 500
    except requests.exceptions.ConnectionError as e:
        log(f"❌ ERROR de conexión: No se puede alcanzar graph.facebook.com")
        log(f"   Detalles: {e}")
        return jsonify({"error": "Error de red al conectar con WhatsApp API"}), 500
    except requests.exceptions.RequestException as e:
        log(f"❌ ERROR de requests: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        log(f"❌ ERROR general: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    log("🏠 Endpoint raíz accedido")
    return jsonify({
        "status": "ok",
        "message": "Python WhatsApp Server is running"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    log(f"🌐 Servidor Flask iniciando en puerto {port}...")
    app.run(host="0.0.0.0", port=port)
