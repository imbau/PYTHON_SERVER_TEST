from flask import Flask, request, jsonify
from call_ai import call_openrouter
import os
import requests
from send_message import send_message
from memory import save_history
from lead_detector import analyze_conversation_for_lead
from lead_parser import extract_lead_data
from create_lead import create_lead
from datetime import datetime
import json

app = Flask(__name__)

SYSTEM_PROMPT = "Eres un chatbot de Tradeboom, una página web de compra y venta de fondos de comercio. Tu tarea es asistir en español a los clientes que escriben sobre la compra de fondos de comercio."

@app.post("/responder")
def responder():
    print("\n📩 ====== NUEVA REQUEST ======")

    WSP_TOKEN = os.getenv("WSP_TOKEN")
    PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

    print(f"🔐 ENV: TOKEN={'OK' if WSP_TOKEN else 'MISSING'} | PHONE_ID={'OK' if PHONE_NUMBER_ID else 'MISSING'}")

    data = request.get_json() or {}
    print(f"📥 RAW REQUEST DATA: {data}")

    user_text = str(data.get("user_text") or "")
    user_number = str(data.get("user_number") or "")

    print(f"👤 USER TEXT: {user_text}")
    print(f"📞 USER NUMBER RAW: {user_number}")

    if user_number == "5492216982208":
        user_number = "54221156982208"
    elif user_number == "5492216216025":
        user_number = "54221156216025"

    print(f"📞 NORMALIZED NUMBER: {user_number}")

    if not user_text.strip() or not user_number.strip() or not WSP_TOKEN or not PHONE_NUMBER_ID:
        print(f"❌ ERROR: Datos inválidos para procesar mensaje")
        return jsonify({"error": "Faltan datos"}), 400

    conversation_id = user_number

    # =========================================
    # 1️⃣ OBTENER HISTORIAL
    # =========================================
    history_messages = []
    try:
        print(f"🗂️ Buscando historial para conversación: {conversation_id}")
        response = requests.get(
            f"http://tradeboom.epikasoftware.com/api/whatsapp/conversation/{conversation_id}",
            timeout=10
        )

        print(f"🌐 API HISTORY STATUS: {response.status_code}")

        if response.status_code == 200:
            history_messages = response.json()
            print(f"📚 HISTORIAL RECIBIDO ({len(history_messages)} mensajes)")
        else:
            print("⚠️ No se pudo recuperar historial, usando vacío")
            history_messages = []
    except Exception as e:
        print(f"❌ ERROR obteniendo historial: {e}")
        history_messages = []

    # =========================================
    # 2️⃣ ARMAMOS CONTEXTO PARA IA
    # =========================================
    print("🧠 Construyendo contexto para IA...")

    messages_for_ai = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    for i, msg in enumerate(history_messages):
        content = str(msg.get("message") or msg.get("content") or "").strip()
        role = msg.get("role", "user")

        if not content or content == SYSTEM_PROMPT:
            continue
        
        if "How can I assist you" in content or i == len(history_messages) - 1:
            if i % 2 != 0:
                role = "assistant"

        messages_for_ai.append({"role": role, "content": content})

    messages_for_ai.append({"role": "user", "content": user_text})

    print("📤 CONTEXTO ENVIADO A IA:")
    for m in messages_for_ai:
        print(f" - {m['role'].upper()}: {m['content']}")

    # =========================================
    # 3️⃣ ENVIAR RESPUESTA AL USUARIO
    # =========================================
    bot_response = send_message(user_number, messages_override=messages_for_ai)
    bot_text = bot_response.get("message", "")

    print(f"🤖 BOT RESPONSE: {bot_text}")

    # =========================================
    # 4️⃣ GUARDAR HISTORIAL
    # =========================================
    print("💾 Guardando mensaje del usuario...")
    save_history(conversation_id, "USER", "BOT", "in", user_text, "user")
    
    print("💾 Guardando respuesta del bot...")
    save_history(conversation_id, "BOT", "USER", "out", bot_text, "assistant")

    # =========================================
    # 5️⃣ EVALUAR LEAD
    # =========================================
    try:
        print("\n🔎 Evaluando si ya podemos crear Lead...")
        evaluation = analyze_conversation_for_lead(history_messages)
        print(f"📥 RAW IA Lead Evaluator RESPONSE: {evaluation}")

        data = json.loads(evaluation)
        print(f"📊 Lead Evaluation Parsed: {data}")

        if data.get("ready"):
            print("🚀 Lead listo para crear!")

            lead_data = extract_lead_data(history_messages)
            print(f"📌 Lead Data Extraída: {lead_data}")

            visit_date = datetime.now().strftime("%Y-%m-%d")
            print(f"📅 Visit Date asignada: {visit_date}")

            success = create_lead(
                name = lead_data["name"],
                phone = user_number,
                notes = lead_data["notes"],
                status = lead_data["status"],
                visit_date = visit_date
            )

            print(f"🏁 Resultado creación lead: {success}")

        else:
            print("⏳ Aún no hay datos suficientes para Lead")

    except Exception as e:
        print("❌ ERROR TOTAL EN PROCESO DE LEAD:", e)

    print("✅ FINALIZADO REQUEST")
    return jsonify({"success": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Iniciando servidor en puerto {port}")
    app.run(host="0.0.0.0", port=port)
