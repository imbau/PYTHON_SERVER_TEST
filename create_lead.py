import requests

def create_lead(name, phone, notes, status, visit_date):
  url = "https://tradeboom.epikasoftware.com/api/leads"

  payload = {
    "name": name,
    "phone": phone,
    "source": "whatsapp",
    "status": status,
    "visit_date": visit_date,
    "notes": notes
  }

  try:
    print(f"Guardando Lead...")
    response = requests.post(url, json=payload, timeout=20)
    print(f"✅ BD: {response.status_code} - {response.text}")
    return True
  except Exception as e:
    print(f"❌ Error BD: {e}")
    return False
