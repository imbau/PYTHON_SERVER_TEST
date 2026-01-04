from openai import OpenAI
import os
import sys
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY no está configurada")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def call_openrouter(user_text):
    print(f"🔵 call_openrouter iniciado con: '{user_text}'", flush=True)
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente de compra y venta de fondos de comercio."
                },
                {
                    "role": "user",
                    "content": user_text,
                }
            ]
        )
        
        result = response.choices[0].message.content
        print(f"🔵 OpenRouter respondió exitosamente", flush=True)
        return result
        
    except Exception as e:
        print(f"🔴 Error en call_openrouter: {e}", flush=True)
        raise
