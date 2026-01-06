import requests
import os

def save_history(id, sender, to, direction, message, role):
  url = "http://tradeboom.epikasoftware.com/api/webhook/whatsapp"
  
  payload = {
    "conversation_id": id,
    "from": sender,
    "to": to,
    "direction": direction,
    "message": message,
    "role" : role
  }

  try:
    response = requests.post(url, json=payload, timeout=20)
    response.raise_for_status()

    return {
        "success": True,
        "status": response.status_code,
        "data": response.json()
    }

  except requests.exceptions.Timeout:
    return {
      "success": False,
      "error": "Request timeout"
    }

  except requests.exceptions.HTTPError as err:
    return {
      "success": False,
      "error": f"HTTP error: {err}",
      "status": getattr(err.response, "status_code", None)
    }

  except Exception as e:
    return {
      "success": False,
      "error": str(e)
    }
