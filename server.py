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
    
    # HARDFIX: Reemplazar tu número específico
    if user_number == "5492216982208":
        user_number = "54221156982208"
    elif user_number == "5492216216025":
        user_number = "54221156216025"
    
    if not user_text or not user_number or not WSP_TOKEN or not PHONE_NUMBER_ID:
        print(f"❌ Datos incompletos: text={bool(user_text)}, number={bool(user_number)}")
        return jsonify({"error": "Configuración incompleta"}), 400

    conversation_id = user_number

    # Guardar mensaje de usuario

    save_history(
        conversation_id,
        sender=user_number,
        to="BOT",
        direction="in",
        message=user_text
    )

    # Enviar mensaje
    
    bot_response = send_message(user_number, user_text)

    # Guardar mensaje de bot

    save_history(
        conversation_id,
        sender="BOT",
        to=user_number,
        direction="out",
        message=bot_response.get("message", "Respuesta enviada")
    )
    
    return jsonify({"success": True})

@app.route("/")
def home():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
