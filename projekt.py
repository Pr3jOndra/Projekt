from flask import Flask, request, jsonify, send_file
import requests
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# ======================
# CONFIG
# ======================
DB_PATH = os.getenv("DB_PATH", "/data/db.sqlite")

OPENAI_BASE_URL = os.getenv(
    "OPENAI_BASE_URL",
    "https://kurim.ithope.eu/v1"
)

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    "sk-4cv4dSfPAv3YxI2jh..."
)

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "gemma3:27b"
)

# ======================
# DB
# ======================
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
conn.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem TEXT,
    answer TEXT,
    created_at TEXT
)
""")
conn.close()

# ======================
# WEB (HTML)
# ======================
@app.route("/")
def home():
    return send_file("index.html")


# ======================
# API
# ======================
@app.route("/ping")
def ping():
    return "pong"


@app.route("/ai", methods=["POST"])
def ai():
    return jsonify({"answer": "TEST OK"})
    data = request.get_json(force=True)
    problem = data.get("problem", "")

    url = f"{OPENAI_BASE_URL}/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "Jsi IT asistent. Odpovídej stručně a česky."
            },
            {
                "role": "user",
                "content": problem
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()

        answer = response.json()["choices"][0]["message"]["content"]

    except:
        answer = "AI není dostupná."

    # save to DB
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO history (problem, answer, created_at) VALUES (?, ?, ?)",
        (problem, answer, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    return jsonify({"answer": answer})


@app.route("/history")
def history():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT * FROM history ORDER BY id DESC").fetchall()
    conn.close()

    return jsonify([
        {"id": r[0], "problem": r[1], "answer": r[2], "created_at": r[3]}
        for r in rows
    ])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
