import requests

BASE_URL = "http://tradeboom.epikasoftware.com/api/leads"

def lead_exists(phone):
    response = requests.get(f"{BASE_URL}?phone={phone}")

    if response.status_code != 200:
        print("⚠️ No pude verificar leads, mejor no crear nada")
        return True  

    data = response.json()

    return len(data) > 0


def create_lead(name, phone, notes, status, visit_date):

    if lead_exists(phone):
        print("⛔ Ya existe lead para este número. No se crea otro.")
        return False

    payload = {
        "name": name,
        "phone": phone,
        "notes": notes,
        "status": status,
        "visit_date": visit_date
    }

    response = requests.post(BASE_URL, json=payload)

    if response.status_code == 201:
        print("✅ Lead creado")
        return True
    
    print("❌ Error creando lead:", response.status_code, response.text)
    return False

