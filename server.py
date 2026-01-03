from flask import Flask, request, jsonify
from call_ai import call_openrouter
import os

app = Flask(__name__)

@app.post("/responder")
def responder():
    data = request.get_json()

    user_text = data.get("user_text", "")
    user_number = data.get("user_number", "")

    print("📩 Mensaje recibido desde Node:", user_text)
    print("📞 Número:", user_number)

    ai_response = call_openrouter(user_text)

    return jsonify({
        "reply_text": ai_response
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
