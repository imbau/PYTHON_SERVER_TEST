import sys
import logging
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

# ========= 🔥 FORZAR LOGS EN RENDER =========
# No buffer en stdout
sys.stdout.reconfigure(line_buffering=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

log = logging.getLogger("tradeboom")

# ============================================

app = Flask(__name__)

SYSTEM_PROMPT = "Eres un chatbot de Tradeboom, una página web de compra y venta de fondos de comercio. Tu tarea es asistir en español a los clientes que escriben sobre la compra de fondos de comercio."

@app.post("/responder")
def responder():
    log.info("📩 ====== NUEVA REQUEST ======")

    WSP_TOKEN = os.getenv("WSP_TOKEN")
    PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

    log.info(f"🔐 ENV: TOKEN={'OK' if WSP_TOKEN else 'MISSING'} | PHONE_ID={'OK' if PHONE_NUMBER_ID else 'MISSING'}")

    data = request.get_json() or {}
    log.info(f"📥 RAW REQUEST DATA: {data}")

    user_text = str(data.get("user_text") or "")
    user_number = str(data.get("user_number") or "")

    log.info(f"👤 USER TEXT: {user_text}")
    log.info(f"📞 USER NUMBER RAW: {user_number}")

    if user_number == "5492216982208":
        user_number = "54221156982208"
    elif user_number == "5492216216025":
        user_number = "54221156216025"

    log.info(f"📞 NORMALIZED NUMBER: {user_number}")

    if not user_text.strip() or not user_number.strip() or not WSP_TOKEN or not PHONE_NUMBER_ID:
        log.error("❌ ERROR: Datos inválidos")
        return jsonify({"error": "Faltan datos"}), 400

    conversation_id = user_number

    # ===========================
    # 1️⃣ HISTORIAL
    # ===========================
    history_messages = []
    try:
        log.info(f"🗂️ Buscando historial {conversation_id}")
        response = requests.get(
            f"http://tradeboom.epikasoftware.com/api/whatsapp/conversation/{conversation_id}",
            timeout=10
        )

        log.info(f"🌐 API HISTORY STATUS: {response.status_code}")

        if response.status_code == 200:
            history_messages = response.json()
            log.info(f"📚 HISTORIAL RECIBIDO ({len(history_messages)})")
        else:
            log.warning("⚠️ No se pudo recuperar historial")
            history_messages = []
    except Exception as e:
        log.exception("❌ ERROR obteniendo historial")
        history_messages = []

    # ===========================
    # 2️⃣ CONTEXTO
    # ===========================
    log.info("🧠 Construyendo contexto...")

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

    log.info("📤 CONTEXTO ENVIADO A IA:")
    for m in messages_for_ai:
        log.info(f" - {m['role'].upper()}: {m['content']}")

    # ===========================
    # 3️⃣ RESPUESTA BOT
    # ===========================
    bot_response = send_message(user_number, messages_override=messages_for_ai)
    bot_text = bot_response.get("message", "")

    log.info(f"🤖 BOT RESPONSE: {bot_text}")

    # ===========================
    # 4️⃣ GUARDAR HISTORIAL
    # ===========================
    log.info("💾 Guardando usuario...")
    save_history(conversation_id, "USER", "BOT", "in", user_text, "user")
    
    log.info("💾 Guardando bot...")
    save_history(conversation_id, "BOT", "USER", "out", bot_text, "assistant")

    # ===========================
    # 5️⃣ LEAD
    # ===========================
    try:
        log.info("🔎 Evaluando Lead...")
        evaluation = analyze_conversation_for_lead(history_messages)
        log.info(f"📥 RAW LEAD EVALUATION: {evaluation}")

        data = json.loads(evaluation)
        log.info(f"📊 Parsed Lead: {data}")

        if data.get("ready"):
            log.info("🚀 Lead listo!")

            lead_data = extract_lead_data(history_messages)
            log.info(f"📌 Lead Data RAW: {lead_data}")
            
            # 👇 FIX MAGISTRAL
            if isinstance(lead_data, str):
                lead_data = json.loads(lead_data)
            
            log.info(f"📌 Lead Data Parsed: {lead_data}")


            visit_date = datetime.now().strftime("%Y-%m-%d")
            log.info(f"📅 Visit Date: {visit_date}")

            success = create_lead(
                name = lead_data["name"],
                phone = user_number,
                notes = lead_data["notes"],
                status = lead_data["status"],
                visit_date = visit_date
            )

            log.info(f"🏁 Lead creado: {success}")

        else:
            log.info("⏳ Aún no hay datos suficientes")
    except Exception as e:
        log.exception("❌ ERROR PROCESANDO LEAD")

    log.info("✅ FINALIZADO REQUEST")
    return jsonify({"success": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    log.info(f"🚀 Iniciando servidor en puerto {port}")
    app.run(host="0.0.0.0", port=port)
