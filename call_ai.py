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
    model="openai/gpt-oss-120b:free",
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
    extra_body={"reasoning": {"enabled": True}}
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

  # Second API call - model continues reasoning from where it left off
  response2 = client.chat.completions.create(
    model="openai/gpt-oss-120b:free",
    messages=messages,
    extra_body={"reasoning": {"enabled": True}}
  )

  return response2.choices[0].message.content
