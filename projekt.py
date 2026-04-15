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

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma3:27b")

# ======================
# DB INIT
# ======================
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

try:
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
except Exception as e:
    print("DB INIT ERROR:", e)


# ======================
# ROUTES
# ======================
@app.route("/")
def home():
    return send_file("index.html")


@app.route("/ping")
def ping():
    return "pong"


@app.route("/ai", methods=["POST"])
def ai():
    try:
        data = request.get_json(force=True) or {}
        problem = data.get("problem", "").strip()

        if not problem:
            return jsonify({"answer": "Zadej nějaký problém."})

        answer = "AI není dostupná."

        # ======================
        # AI REQUEST
        # ======================
        try:
            response = requests.post(
                f"{OPENAI_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MODEL_NAME,
                    "messages": [
                        {"role": "system", "content": "Jsi IT asistent. Odpovídej stručně a česky."},
                        {"role": "user", "content": problem}
                    ]
                },
                timeout=15
            )

            if response.ok:
                data = response.json()
                answer = (
                    data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", answer)
                )

        except Exception as e:
            print("API ERROR:", e)

        # ======================
        # SAVE TO DB
        # ======================
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT INTO history (problem, answer, created_at) VALUES (?, ?, ?)",
                (problem, answer, datetime.now().isoformat())
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print("DB SAVE ERROR:", e)

        return jsonify({"answer": answer})

    except Exception as e:
        print("GLOBAL ERROR:", e)
        return jsonify({"answer": "Server error"})


@app.route("/history")
def history():
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT problem, answer FROM history ORDER BY id DESC LIMIT 20"
        ).fetchall()
        conn.close()

        return jsonify([
            {"problem": r[0], "answer": r[1]}
            for r in rows
        ])

    except Exception as e:
        print("DB READ ERROR:", e)
        return jsonify([])


# ======================
# RUN
# ======================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
