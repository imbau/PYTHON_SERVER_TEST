from call_ai import call_openrouter
import json

SYSTEM_EXTRACTOR_PROMPT = """
Eres un analista experto de conversaciones de WhatsApp para ventas de fondos de comercio.
Tu tarea es leer el historial y extraer datos para un LEAD.
Devuelve SIEMPRE un JSON válido, sin nada más de texto.

Campos:

name: nombre del cliente si lo dijo, sino "".
phone: número del cliente si lo mencionó explícito, sino "" (no inventes).
status: uno de estos valores:
  - "new"
  - "interested"
  - "not_interested"
  - "need_followup"
  Si no está claro, usa "need_followup".

notes: resumen breve útil para ventas.

NO inventes fechas.
NO agregues campos extras.
Solo responde JSON.
"""


def extract_lead_data(history_messages):
    """
    history_messages = [
        {"role": "user", "message": "Hola quiero comprar una panadería"},
        {"role": "assistant", "message": "..."}
    ]
    """

    try:
        text_history = ""

        for msg in history_messages:
            role = msg.get("role", "user")
            content = msg.get("message") or msg.get("content") or ""
            text_history += f"{role.upper()}: {content}\n"

        ai_response = call_openrouter(
            [
                {"role": "system", "content": SYSTEM_EXTRACTOR_PROMPT},
                {"role": "user", "content": text_history}
            ]
        )

        raw = ai_response.get("message", "{}")
        
        try:
            data = json.loads(raw)
        except:
            data = {}

        # Garantizamos estructura segura
        return {
          "name": data.get("name", ""),
          "phone": data.get("phone", ""),
          "status": data.get("status", "need_followup"),
          "notes": data.get("notes", "")
        }


    except Exception as e:
        print("❌ Error extrayendo lead:", e)
        return {
            "name": "",
            "phone": "",
            "status": "need_followup",
            "notes": ""
        }
