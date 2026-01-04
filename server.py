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

def fix_argentinian_number(number):
    """
    Corrige números argentinos agregando el 15 si falta
    Formato esperado:
    - Entrada: 5492216982208 (54 + 221 + 6982208)
    - Salida: 54221156982208 (54 + 221 + 15 + 6982208)
    """
    number = ''.join(filter(str.isdigit, str(number)))
    
    log(f"🔧 Número original: {number}")
    
    # Verificar si es argentino (empieza con 54) y tiene 13 dígitos
    if number.startswith('54') and len(number) == 13:
        # Extraer partes: 54 + código de área (3 dígitos) + resto
        country_code = number[:2]  # "54"
        area_code = number[2:5]    # "221"
        local_number = number[5:]   # "6982208"
        
        # Construir número con 15
        fixed_number = country_code + area_code + '15' + local_number
        log(f"🔧 Número corregido: {fixed_number}")
        return fixed_number
    
    # Si ya tiene 15 dígitos, probablemente ya está correcto
    if len(number) == 15:
        log(f"🔧 Número ya tiene 15 dígitos, sin cambios")
        return number
    
    log(f"🔧 Número sin cambios: {number}")
    return number

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
    
    # Corregir número argentino
    user_number = fix_argentinian_number(user_number)
    
    log(f"📩 Texto del usuario: '{user_text}'")
    log(f"📞 Número del usuario (corregido): '{user_number}'")
    
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
