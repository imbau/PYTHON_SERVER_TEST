from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def call_openrouter(user_text):
    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente de compra y venta de fondos de comercio."},
            {"role": "user", "content": user_text}
        ]
    )
      # Extract the assistant message with reasoning_details
  response = response.choices[0].message

  # Preserve the assistant message with reasoning_details
  messages = [
    {"role": "user", "content": user_text},
    {
      "role": "assistant",
      "content": response.content,
      "reasoning_details": response.reasoning_details  # Pass back unmodified
    }
  ]
    return response.choices[0].message.content
