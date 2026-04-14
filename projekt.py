from flask import Flask, request, jsonify, send_file
import requests
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

DB_PATH = os.getenv("DB_PATH", "/data/db.sqlite")

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma3:27b")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# DB SAFE INIT
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
except:
    pass


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
        problem = data.get("problem", "")

        # fallback když API nefunguje
        answer = "AI není dostupná."

        try:
            r = requests.post(
                f"{OPENAI_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MODEL_NAME,
                    "messages": [
                        {"role": "system", "content": "Odpovídej stručně česky."},
                        {"role": "user", "content": problem}
                    ]
                },
                timeout=15
            )

            if r.ok:
                j = r.json()
                answer = j.get("choices", [{}])[0].get("message", {}).get("content", answer)

        except Exception as e:
            print("API error:", e)

        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT INTO history (problem, answer, created_at) VALUES (?, ?, ?)",
                (problem, answer, datetime.now().isoformat())
            )
            conn.commit()
            conn.close()
        except:
            pass

        return jsonify({"answer": answer})

    except Exception as e:
        print("GLOBAL ERROR:", e)
        return jsonify({"answer": "Server error"})


@app.route("/history")
def history():
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("SELECT * FROM history ORDER BY id DESC").fetchall()
        conn.close()

        return jsonify([
            {"id": r[0], "problem": r[1], "answer": r[2], "created_at": r[3]}
            for r in rows
        ])
    except:
        return jsonify([])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
