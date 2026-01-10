import requests
import logging

log = logging.getLogger("tradeboom")

KEYWORDS = [
    "negocios",
    "fondos",
    "oportunidades",
    "disponibles",
    "comprar",
    "opciones",
    "invertir",
    "disponible",
    "disponibles",
    "adquirir"
]

def get_active_businesses():
    try:
        response = requests.get("http://tradeboom.epikasoftware.com/api/business/active", timeout=10)
        return response.json()
    except Exception as e:
        log.exception("❌ Error obteniendo negocios activos")
        return []

def wants_businesses(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in KEYWORDS)
