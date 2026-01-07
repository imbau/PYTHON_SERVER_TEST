from call_ai import call_openrouter
import json

def analyze_conversation_for_lead(history):
    prompt = [
        {
            "role": "system",
            "content": """
Eres un analista...
(igual que antes)
"""
        },
        {
            "role": "user",
            "content": str(history)
        }
    ]

    ai_response = call_openrouter(prompt)

    try:
        # si viene string JSON → validamos
        if isinstance(ai_response, str):
            json.loads(ai_response)  
            return ai_response
        
        # si viene dict → lo convertimos a string json
        return json.dumps(ai_response)

    except Exception as e:
        print("ERROR PARSEANDO AI:", e)
        return json.dumps({
            "ready": False,
            "name": "",
            "notes": "",
            "status": "new"
        })
