from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def call_openrouter(user_text):
    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": user_text,
            },
            {
                "role": "system",
                "content": "Eres un asistente de compra y venta de fondos de comercio."
            }
        ],
    )
    
    response = response.choices[0].message
    
    messages = [
        {"role": "user", "content": user_text},
        {
            "role": "assistant",
            "content": response.content,
        }
    ]
    
    response2 = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=messages,
    )
    
    return response2.choices[0].message.content
