from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def call_openrouter(messages):
    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=messages
    )

    return response.choices[0].message.content
