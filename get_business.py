import requests
import logging

log = logging.getLogger("tradeboom")

def get_active_businesses():
    try:
        response = requests.get(
            "http://tradeboom.epikasoftware.com/api/business/active",
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        log.exception("❌ Error obteniendo negocios activos")
    return []

def find_relevant_businesses(user_text, businesses, limit=3):
    keywords = user_text.lower().split()
    matches = []

    for b in businesses:
        haystack = " ".join([
            str(b.get("title", "")),
            str(b.get("description", "")),
            str(b.get("city", "")),
            str(b.get("category", "")),
        ]).lower()

        score = sum(1 for k in keywords if k in haystack)

        if score > 0:
            matches.append((score, b))

    matches.sort(key=lambda x: x[0], reverse=True)

    return [b for _, b in matches[:limit]]

def build_business_context(businesses):
    if not businesses:
        return None

    lines = ["Negocios disponibles que pueden interesar al cliente:"]

    for b in businesses:
        lines.append(
            f"- {b.get('title')} | {b.get('city')} | "
            f"Precio: {b.get('price')} | "
            f"Rubro: {b.get('category')}"
        )

    return "\n".join(lines)
