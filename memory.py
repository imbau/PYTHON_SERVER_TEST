import requests
import os

def save_history(id, sender, to, dir, message):
  url = f"http://tradeboom.epikasoftware.com/api/webhook/whatsapp"
  
  payload = {
    "conversation_id": id,
    "from": sender,
    "to": to,
    "direction": dir,
    "message": message
  }

  try:
    response = requests.post(url, json=payload, timeout=20)
    response.raise_for_status()
    return {
      "success": True,
      "status": response.status_code,
      "data": response.json()
    }
  except Exception as e:
    return {
      "success": False,
      "error": str(e)
    }
