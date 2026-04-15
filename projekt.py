<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>AI IT Asistent</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: white;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        .container {
            width: 520px;
            background: #111827;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
        }

        h1 {
            text-align: center;
            margin-bottom: 5px;
        }

        .author {
            text-align: center;
            font-size: 13px;
            color: #9ca3af;
            margin-bottom: 10px;
        }

        .info {
            text-align: center;
            font-size: 12px;
            color: #9ca3af;
            margin-bottom: 15px;
        }

        textarea {
            width: 100%;
            height: 80px;
            border-radius: 10px;
            border: none;
            padding: 10px;
            resize: none;
            outline: none;
        }

        button {
            width: 100%;
            margin-top: 10px;
            padding: 10px;
            background: #3b82f6;
            border: none;
            border-radius: 10px;
            color: white;
            cursor: pointer;
        }

        button:hover {
            background: #2563eb;
        }

        .chat {
            margin-top: 15px;
            max-height: 250px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .msg {
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
            white-space: pre-wrap;
        }

        .user {
            background: #374151;
            align-self: flex-end;
        }

        .ai {
            background: #1f2937;
            align-self: flex-start;
        }

        .loading {
            text-align: center;
            font-size: 12px;
            color: #9ca3af;
        }
    </style>
</head>

<body>

<div class="container">
    <h1>🤖 AI IT Asistent</h1>

    <div class="author">Ondřej Buček</div>

    <div class="info">
        Nástroj pro <b>stručné odpovědi IT podpory</b>
    </div>

    <textarea id="problem" placeholder="např. Nejde mi internet..."></textarea>

    <button onclick="send()">Odeslat</button>
    <button onclick="loadHistory()">Načíst historii</button>

    <div class="chat" id="chat"></div>
</div>

<script>
async function send() {
    const problem = document.getElementById("problem").value;
    const chat = document.getElementById("chat");

    if (!problem.trim()) return;

    // zobraz user zprávu
    chat.innerHTML += `<div class="msg user">${problem}</div>`;
    chat.innerHTML += `<div class="loading" id="loading">⏳ AI přemýšlí...</div>`;

    chat.scrollTop = chat.scrollHeight;

    try {
        const res = await fetch("/ai", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({problem})
        });

        const data = await res.json();

        document.getElementById("loading").remove();

        chat.innerHTML += `<div class="msg ai">${data.answer}</div>`;
        chat.scrollTop = chat.scrollHeight;

    } catch (e) {
        document.getElementById("loading").remove();
        chat.innerHTML += `<div class="msg ai">❌ Chyba API</div>`;
    }
}

async function loadHistory() {
    const chat = document.getElementById("chat");
    chat.innerHTML = `<div class="loading">Načítám historii...</div>`;

    try {
        const res = await fetch("/history");
        const data = await res.json();

        chat.innerHTML = "";

        if (data.length === 0) {
            chat.innerHTML = `<div class="msg ai">Žádná historie.</div>`;
            return;
        }

        data.reverse().forEach(item => {
            chat.innerHTML += `<div class="msg user">${item.problem}</div>`;
            chat.innerHTML += `<div class="msg ai">${item.answer}</div>`;
        });

        chat.scrollTop = chat.scrollHeight;

    } catch (e) {
        chat.innerHTML = `<div class="msg ai">❌ Nepodařilo se načíst historii</div>`;
    }
}
</script>

</body>
</html>
