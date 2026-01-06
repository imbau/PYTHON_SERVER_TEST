import os
import psycopg2
from psycopg2.extras import RealDictCursor

DB_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DB_URL)

def save_message(user_number, role, content):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO chat_memory (user_number, role, content)
        VALUES (%s, %s, %s)
    """, (user_number, role, content))

    conn.commit()
    cur.close()
    conn.close()

def get_history(user_number, limit=10):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT role, content
        FROM chat_memory
        WHERE user_number = %s
        ORDER BY id DESC
        LIMIT %s
    """, (user_number, limit))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Lo devolvemos del más viejo al más nuevo
    return list(reversed(rows))
