from call_ai import call_openrouter
import json

def analyze_conversation_for_lead(history):
    prompt = [
        {
            "role": "system",
            "content": """
Eres un analista. Tu tarea es evaluar una conversación de WhatsApp.
Determina si ya hay suficiente información para crear un lead.

Debes responder SIEMPRE en JSON:

{
 "ready": true|false,
 "name": "string o vacío",
 "notes": "resumen claro de interés del usuario o vacío",
 "status": "new | interested | not_interested | need_followup"
}

Criterio:
- ready = true SOLO si el usuario ya expresó interés claro y dio su nombre.
- Si falta algo, ready = false.
"""
        },
        {
            "role": "user",
            "content": str(history)
        }
    ]

    ai_response = call_openrouter(prompt)

    try:
        # Si viene string → parseamos
        if isinstance(ai_response, str):
            data = json.loads(ai_response)
        else:
            # Si ya es dict lo usamos directo
            data = ai_response

        return data

    except Exception as e:
        print("ERROR PARSEANDO AI:", e)
        return {
            "ready": False,
            "name": "",
            "notes": "",
            "status": "new"
        }
