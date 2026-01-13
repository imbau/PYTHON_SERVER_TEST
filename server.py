import sys
import logging
from flask import Flask, request, jsonify
import os
import requests
from send_message import send_message, send_text_message
from memory import save_history, find_name
from get_business import get_active_businesses, wants_businesses

NAME_LOCK = set()

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

SYSTEM_PROMPT = "Eres un chatbot de Tradeboom, una página web de compra y venta de fondos de comercio. Tu tarea es asistir en español a los clientes que escriben sobre la compra de fondos de comercio. Es muy importante que lo primero que preguntes en absolutamente todas las conversaciones sea el nombre del usuario. Cuando quieras resaltar una palabra o ponerla en negrita, solo pon un par de asteriscos, *de esta manera*."

@app.post("/responder")
def responder():
    log.info("📩 ====== NUEVA REQUEST ======")

    WSP_TOKEN = os.getenv("WSP_TOKEN")
    PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

    log.info(f"🔐 ENV: TOKEN={'OK' if WSP_TOKEN else 'MISSING'} | PHONE_ID={'OK' if PHONE_NUMBER_ID else 'MISSING'}")

    data = request.get_json() or {}
    log.info(f"📥 RAW REQUEST DATA: {data}")

    expired = bool(data.get("expired", False))

    user_text = str(data.get("user_text") or "")
    user_number = str(data.get("user_number") or "")

    log.info(f"👤 USER TEXT: {user_text}")
    log.info(f"📞 USER NUMBER RAW: {user_number}")

    if user_number == "5492216982208":
        user_number = "54221156982208"
    elif user_number == "5492216216025":
        user_number = "54221156216025"
    elif user_number == "5491170650235":
        user_number = "54111570650235"

    log.info(f"📞 NORMALIZED NUMBER: {user_number}")

    if expired:
        log.info("⏰ Conversación expirada (controlada por webhook)")
    
        send_text_message(
            user_number,
            "⏳ *El tiempo de esta conversación ha finalizado.*\n\n"
            "Si querés continuar, podés hablar con un agente humano."
        )
    
        return jsonify({"success": True, "expired": True})

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

            if len(history_messages) < 2 and conversation_id in NAME_LOCK:
                NAME_LOCK.remove(conversation_id)
                log.info("🧹 NAME_LOCK limpiado (historial mínimo)")

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

    business_context = None
    
    if wants_businesses(user_text):
        log.info("📦 Usuario solicitó negocios disponibles")
        businesses = get_active_businesses()

        if businesses:
            business_context = (
                "Estos son los negocios disponibles actualmente en Tradeboom:\n"
                f"{businesses}\n"
                "Usa SOLO esta información para responder. "
                "No inventes negocios que no estén en la lista."
            )

    messages_for_ai = [{"role": "system", "content": SYSTEM_PROMPT}]

    if business_context:
        messages_for_ai.append({
            "role": "system",
            "content": business_context
        })


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
    
    name = None
    
    if conversation_id not in NAME_LOCK:
        name = find_name(conversation_id)
    
        if name is not None:
            NAME_LOCK.add(conversation_id)
            log.info(f"🔒 Nombre fijado: {name}")
        else:
            log.info("No se ha encontrado un nombre")
    else:
        log.info("Ya existe un nombre en la memoria")
            

    if name != None:
        save_history(
            conversation_id,
            "USER",
            "BOT",
            "in",
            user_text,
            "user",
            name
        )
    else:
        save_history(
            conversation_id,
            "USER",
            "BOT",
            "in",
            user_text,
            "user"
        )

    
    log.info("💾 Guardando bot...")
    save_history(conversation_id, "BOT", "USER", "out", bot_text, "assistant")

    log.info("✅ FINALIZADO REQUEST")
    return jsonify({"success": True})

    log.info(f"HEADERS: {dict(request.headers)}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    log.info(f"🚀 Iniciando servidor en puerto {port}")
    app.run(host="0.0.0.0", port=port)
