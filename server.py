from flask import Flask, request, jsonify
from call_ai import call_openrouter
import os
import requests
from send_message import send_message
from memory import save_history

app = Flask(__name__)

# DEFINIMOS EL SYSTEM PROMPT COMO CONSTANTE
SYSTEM_PROMPT = "Eres un chatbot de Tradeboom, una página web de compra y venta de fondos de comercio. Tu tarea es asistir en español a los clientes que escriben sobre la compra de fondos de comercio."

@app.post("/responder")
def responder():
    WSP_TOKEN = os.getenv("WSP_TOKEN")
    PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
    
    data = request.get_json() or {}
    
    # 🛡️ SEGURIDAD: Convertir explícitamente a string.
    # Si viene null en el JSON, 'or ""' lo convierte a vacío.
    user_text = str(data.get("user_text") or "")
    user_number = str(data.get("user_number") or "")
    
    # Normalización de números
    if user_number == "5492216982208":
        user_number = "54221156982208"
    elif user_number == "5492216216025":
        user_number = "54221156216025"
    
    # Validar que tengamos datos reales
    if not user_text.strip() or not user_number.strip() or not WSP_TOKEN or not PHONE_NUMBER_ID:
        print(f"❌ Datos inválidos: text='{user_text}', number='{user_number}'")
        return jsonify({"error": "Faltan datos"}), 400
    
    conversation_id = user_number
    # 1. Obtener Historial de la API
    history_messages = []
    try:
        response = requests.get(f"http://tradeboom.epikasoftware.com/api/whatsapp/conversation/{conversation_id}", timeout=10)
        if response.status_code == 200:
            history_messages = response.json()
        else:
            history_messages = []
    except:
        history_messages = []

    # 2. CONSTRUCCIÓN DEL CONTEXTO (CORRIGIENDO TU API AL VUELO)
    messages_for_ai = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    for i, msg in enumerate(history_messages):
        content = str(msg.get("message") or msg.get("content") or "").strip()
        if not content or content == SYSTEM_PROMPT: continue

        # REGLA DE ORO: Si el historial dice que todo es 'user', 
        # vamos a alternar: impar = user, par = assistant (o viceversa)
        # O mejor aún: si el mensaje NO es el actual, y es el anterior al actual,
        # es muy probable que sea la respuesta vieja del bot.
        
        role = msg.get("role", "user")
        
        # Corrección manual: Si detectamos el mensaje en inglés que pusiste arriba, 
        # sabemos que es el BOT aunque la API diga 'user'
        if "How can I assist you" in content or i == len(history_messages) - 1:
            if i % 2 != 0: # Lógica simple de alternancia si la API está rota
                role = "assistant"

        messages_for_ai.append({"role": role, "content": content})

    # 3. AGREGAR MENSAJE ACTUAL
    messages_for_ai.append({"role": "user", "content": user_text})

    # 4. ENVIAR A IA
    bot_response = send_message(user_number, messages_override=messages_for_ai)
    bot_text = bot_response.get("message", "")

    # 5. GUARDAR (Y ver los logs para saber por qué no se guarda)
    print("💾 Guardando mensaje del usuario...")
    save_history(conversation_id, "USER", "BOT", "in", user_text, "user")
    
    print("💾 Guardando respuesta del bot...")
    save_history(conversation_id, "BOT", "USER", "out", bot_text, "assistant")

    return jsonify({"success": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
