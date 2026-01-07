from flask import Flask, request, jsonify
from call_ai import call_openrouter
import os
import requests
from send_message import send_message
from memory import save_history

app = Flask(__name__)

@app.post("/responder")
def responder():
    WSP_TOKEN = os.getenv("WSP_TOKEN")
    PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
    
    data = request.get_json()
    user_text = data.get("user_text", "")
    user_number = data.get("user_number", "")
    
    if user_number == "5492216982208":
        user_number = "54221156982208"
    elif user_number == "5492216216025":
        user_number = "54221156216025"
    
    if not user_text or not user_number or not WSP_TOKEN or not PHONE_NUMBER_ID:
        print(f"❌ Datos incompletos: text={bool(user_text)}, number={bool(user_number)}")
        return jsonify({"error": "Configuración incompleta"}), 400
    
    conversation_id = user_number
   
    try:
        response = requests.get(f"http://tradeboom.epikasoftware.com/api/whatsapp/conversation/{conversation_id}", timeout=10)
        if response.status_code == 404:
            messages = []
            is_first_message = True
        else:
            response.raise_for_status()
            history = response.json()
            messages = history.get("data", []) if isinstance(history, dict) else history
            is_first_message = len(messages) == 0
    except requests.exceptions.RequestException as e:
        print("Error consultando historial:", e)
        messages = []
        is_first_message = True
    
    # Construir historial completo en memoria
    if is_first_message:
        messages.append({
            "role": "system",
            "message": "Eres un chatbot de Tradeboom, una página web de compra y venta de fondos de comercio. Tu tarea es asistir en español a los clientes que escriben sobre la compra de fondos de comercio."
        })
        # Guardar en la API
        save_history(
            conversation_id,
            sender="SYSTEM",
            to="BOT",
            direction="out",
            message=messages[-1]["message"],
            role="system"
        )
    
    # Agregar mensaje del usuario al historial en memoria
    messages.append({
        "role": "user",
        "message": user_text
    })
    
    # Guardar mensaje de usuario (sin esperar la respuesta)
    save_history(
        conversation_id,
        sender="USER",
        to="BOT",
        direction="in",
        message=user_text,
        role="user"
    )
    
    # Enviar mensaje pasando el historial directamente
    bot_response = send_message(user_number, messages_override=messages)
    bot_message = bot_response.get("message", "Respuesta enviada")
    
    # Guardar mensaje de bot
    save_history(
        conversation_id,
        sender="BOT",
        to="USER",
        direction="out",
        message=bot_message,
        role="assistant"
    )
    
    return jsonify({"success": True})

@app.route("/")
def home():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
