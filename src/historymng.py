import sqlite3
from datetime import datetime

# DB setup
conn = sqlite3.connect("database/history.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS conversation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    role TEXT,
    content TEXT
)
""")
conn.commit()

def save_message(role, content):
    cursor.execute(
        "INSERT INTO conversation_history (timestamp, role, content) VALUES (?, ?, ?)",
        (datetime.now().isoformat(), role, content)
    )
    conn.commit()

def get_history(limit=10):
    """Fetch last N messages"""
    cursor.execute("SELECT role, content FROM conversation_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    # reverse so oldest → newest
    return rows[::-1]



def build_context(query, limit=10):
    history = get_history(limit)
    context = ""
    for role, content in history:
        if role == "user":
            context += f"🗣️ User: {content}\n"
        elif role == "bot":
            context += f"🤖 Bot: {content}\n"
    context += f"🗣️ User: {query}\n"
    return context
