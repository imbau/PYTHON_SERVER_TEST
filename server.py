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
    
    data = request.get_json()
    user_text = data.get("user_text", "")
    user_number = data.get("user_number", "")
    
    # Normalización de números
    if user_number == "5492216982208":
        user_number = "54221156982208"
    elif user_number == "5492216216025":
        user_number = "54221156216025"
    
    if not user_text or not user_number or not WSP_TOKEN or not PHONE_NUMBER_ID:
        return jsonify({"error": "Configuración incompleta"}), 400
    
    conversation_id = user_number
    
    # --- 1. OBTENER Y LIMPIAR HISTORIAL ---
    history_messages = []
    try:
        response = requests.get(f"http://tradeboom.epikasoftware.com/api/whatsapp/conversation/{conversation_id}", timeout=10)
        if response.status_code == 200:
            history_data = response.json()
            raw_data = history_data.get("data", []) if isinstance(history_data, dict) else history_data
            if isinstance(raw_data, list):
                history_messages = raw_data
    except Exception as e:
        print("Error historial:", e)
        history_messages = []

    # --- 2. CONSTRUIR CONTEXTO PARA LA IA ---
    messages_for_ai = []
    
    # A) Inyectar SIEMPRE el System Prompt primero (con el rol correcto)
    messages_for_ai.append({
        "role": "system",
        "content": SYSTEM_PROMPT
    })
    
    # B) Procesar historial para arreglar roles incorrectos
    for msg in history_messages:
        content = msg.get("message") or msg.get("content") or ""
        
        # IMPORTANTE: Si encontramos el texto del System Prompt en el historial (como 'user'), LO SALTAMOS
        if content.strip() == SYSTEM_PROMPT.strip():
            continue
            
        # INTENTO DE ARREGLAR ROL:
        # A veces las APIs devuelven 'direction': 'in' (usuario) o 'out' (bot)
        role = "user" # Por defecto
        
        # Si la API devuelve el rol explícito correcto, úsalo, si no, intenta deducirlo
        api_role = msg.get("role")
        direction = msg.get("direction") # Chequear si tu API tiene esto
        
        if api_role == "assistant" or api_role == "system":
            role = api_role
        elif direction == "out" or msg.get("sender") == "BOT":
            role = "assistant"
        
        # Agregamos al historial limpio
        if content:
            messages_for_ai.append({
                "role": role,
                "content": content
            })

    # C) Agregar el mensaje ACTUAL del usuario
    messages_for_ai.append({
        "role": "user",
        "content": user_text
    })

    # --- 3. GUARDAR MENSAJE DE USUARIO EN BD ---
    save_history(conversation_id, "USER", "BOT", "in", user_text, "user")
    
    # --- 4. ENVIAR A LA IA ---
    # Pasamos 'messages_for_ai' que YA TIENE el historial arreglado
    bot_response = send_message(user_number, messages_override=messages_for_ai)
    bot_message = bot_response.get("message", "")
    
    # --- 5. GUARDAR RESPUESTA BOT EN BD ---
    if bot_message:
        save_history(conversation_id, "BOT", "USER", "out", bot_message, "assistant")
    
    return jsonify({"success": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
