import requests

BASE_URL = "http://tradeboom.epikasoftware.com/api/leads"

def lead_exists(phone_number):
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
        leads_existentes = response.json()
    
        ya_existe = any(lead.get('phone') == phone_number for lead in leads_existentes)
    
        if ya_existe:
            print(f"Lógica: El número {phone_number} ya existe. No se envía lead.")
            return False
        else:
            print(f"Lógica: El número {phone_number} no existe. Enviando nuevo lead...")
            create_lead(phone_number)
            return True
    
    except Exception as e:
        print(f"Error al conectar con el endpoint: {e}")

def create_lead(name, phone, notes, status, visit_date):

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

