from flask import Flask, request, jsonify
from call_ai import call_openrouter
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.post("/responder")
def responder():
    print("\n" + "=" * 60)
    print("🔔 NUEVO MENSAJE RECIBIDO")
    print("=" * 60)
    
    # Verificar variables de entorno
    WSP_TOKEN = os.getenv("WSP_TOKEN")
    PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
    
    print(f"🔑 WSP_TOKEN: {'✅ Configurado (' + WSP_TOKEN[:20] + '...)' if WSP_TOKEN else '❌ NO CONFIGURADO'}")
    print(f"📱 PHONE_NUMBER_ID: {PHONE_NUMBER_ID if PHONE_NUMBER_ID else '❌ NO CONFIGURADO'}")
    
    # Obtener datos del request
    data = request.get_json()
    user_text = data.get("user_text", "")
    user_number = data.get("user_number", "")
    
    print(f"📩 Texto del usuario: '{user_text}'")
    print(f"📞 Número del usuario: '{user_number}'")
    
    if not user_text or not user_number:
        print("❌ Faltan datos en el request")
        return jsonify({"error": "Faltan user_text o user_number"}), 400
    
    if not WSP_TOKEN or not PHONE_NUMBER_ID:
        print("❌ Faltan variables de entorno")
        return jsonify({"error": "Configuración incompleta"}), 500
    
    # Generar respuesta con IA
    print("🤖 Llamando a OpenRouter...")
    try:
        ai_response = call_openrouter(user_text)
        print(f"✅ IA respondió ({len(ai_response)} caracteres):")
        print(f"   '{ai_response[:150]}{'...' if len(ai_response) > 150 else ''}'")
    except Exception as e:
        print(f"❌ Error en IA: {e}")
        return jsonify({"error": f"Error en IA: {str(e)}"}), 500
    
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
    
    print(f"📤 Enviando a WhatsApp...")
    print(f"   URL: {url}")
    print(f"   Destino: {user_number}")
    print(f"   Mensaje: {len(ai_response)} caracteres")
    
    try:
        wsp_response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        print(f"📬 WhatsApp STATUS: {wsp_response.status_code}")
        print(f"📬 WhatsApp RESPONSE:")
        print(f"   {wsp_response.text}")
        
        response_json = wsp_response.json()
        
        if wsp_response.status_code == 200:
            print("✅ Mensaje enviado exitosamente a WhatsApp")
        else:
            print(f"⚠️ WhatsApp respondió con error: {response_json}")
        
        print("=" * 60 + "\n")
        
        return jsonify({
            "success": wsp_response.status_code == 200,
            "reply_text": ai_response,
            "wsp_status": wsp_response.status_code,
            "wsp_response": response_json
        })
        
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT al enviar a WhatsApp")
        return jsonify({"error": "Timeout enviando mensaje"}), 500
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR de requests: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"❌ ERROR general: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "Python WhatsApp Server is running",
        "endpoints": {
            "/responder": "POST - Procesa mensajes y responde via WhatsApp"
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Servidor Flask iniciando en puerto {port}...")
    app.run(host="0.0.0.0", port=port)
