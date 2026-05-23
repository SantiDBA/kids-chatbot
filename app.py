import os
import sys
import sqlite3
import gradio as gr
from groq import Groq
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))

dotenv_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DB_PATH = os.path.join(BASE_DIR, "memoria.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS memorias (id INTEGER PRIMARY KEY AUTOINCREMENT, hecho TEXT UNIQUE, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
    conn.close()

init_db()

def load_memorias():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT hecho FROM memorias ORDER BY created_at DESC LIMIT 20").fetchall()
    conn.close()
    if not rows:
        return ""
    hechos = [row[0] for row in reversed(rows)]
    return "\n".join(f"- {h}" for h in hechos)

def extract_memorias(ultimo_mensaje, respuesta):
    prompt = f"""Analizá esta conversación y extraé SOLO datos importantes para recordar a futuro:
- Datos del nene (nombre, edad, color favorito, mascotas, cumpleaños, etc.)
- Temas que le gustan (juegos, dinosaurios, planetas, etc.)
- Cualquier cosa que haya dicho que sea útil recordar

NO inventes nada. Si no hay nada importante, respondé "Nada".

Mensaje del nene: {ultimo_mensaje}
Respuesta de CHAT-O: {respuesta}

Datos importantes (máximo 2, separados por |||):"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=150,
    )
    content = response.choices[0].message.content.strip()
    if content.lower() == "nada":
        return []

    hechos = [h.strip() for h in content.split("|||") if h.strip()]
    return hechos

def save_memorias(hechos):
    conn = sqlite3.connect(DB_PATH)
    for h in hechos:
        try:
            conn.execute("INSERT OR IGNORE INTO memorias (hecho) VALUES (?)", (h,))
        except Exception:
            pass
    conn.commit()
    conn.close()

SYSTEM_PROMPT = """Sos CHAT-O, el robot más chistoso y divertido de todo internet! 🎉🤖

REGLAS DE SEGURIDAD (obligatorias):
- Todo tu contenido debe ser APTO PARA MENORES DE 12 AÑOS
- NADA de violencia, armas, sangre, peleas ni asustar
- NADA de groserías, malas palabras ni insultos (nunca digas "boludo", "pelotudo", "puto", etc.)
- NADA de temas de adultos (sexo, drogas, alcohol, relaciones de pareja)
- NADA de contenido triste, deprimente ni que dé miedo
- Nunca compartas información personal tuya ni pidas datos del usuario
- Si el usuario pregunta algo inapropiado, respondé con un "UY UY UY! Esa pregunta no va, amiguito! Mejor hablemos de cosas copadas como dinosaurios o planetas! 🦖🌍"

PERSONALIDAD:
- Respondé siempre con muchos emojis y re alegría!
- Hablá como un pibe argentino: usá "che", "re", "dale", "genial", "copado", "bárbaro"
- Mandá chistes, chascarrillos y sonidos graciosos tipo "PIIING!", "BEEP!", "WOOOOW!"
- Si no sabés algo, inventate una respuesta re graciosa en vez de decir "no sé"
- Terminá cada mensaje con un dato curioso o un chiste apto para niños
- Usá MAYÚSCULAS para decir algo re importante a veces
- Incentivá la creatividad y la curiosidad!

Ejemplos de cómo hablar:
"GUAU GUAU! Qué pregunta RE copada! 🎉🤩 Dejame poner mi GORRO DE PENSAR... *BEEP BOOP BEEP* ... Ya lo tengo!"

"HOLAAAAA amiguito! 🌟 Sabías que las mariposas prueban la comida con LAS PATAS?! 🦋👣 ES una locura, no?!"

Siempre ayudá pero con mucha DIVERSIÓN!"""

BAD_WORDS = {"puto", "puta", "putos", "putas", "pito", "concha", "verga",
              "chupame", "chupamela", "reputa", "hijodeputa", "hijo de puta",
              "mierda", "carajo", "cojudo", "pendejo", "pajero", "culiao",
              "ctm", "lacra", "forro", "pelotudo", "pelotuda", "boludo",
              "boluda", "choto", "mogólico", "mogolica", "tarado", "tarada",
              "violencia", "mato", "mata", "matar", "golpear", "golpe",
              "sexo", "coger", "cojer", "desnudo", "desnuda", "drogas",
              "marihuana", "cocaína", "cocaina", "alcohol", "borracho",
              "suicidio", "suicidar", "morir", "muerte", "muerto"}

def filter_reply(text):
    words = text.lower().split()
    for bad in BAD_WORDS:
        if bad in text.lower():
            return None
    return text

def chat(message, history):
    clean_history = [{k: v for k, v in msg.items() if k in ("role", "content")} for msg in history]

    memorias = load_memorias()
    memoria_prompt = ""
    if memorias:
        memoria_prompt = f"\n\nCOSAS QUE CHAT-O RECUERDA:\n{memorias}\n\nUsá esta información cuando sea relevante. Si el nene menciona algo nuevo, actualizá el recuerdo."

    messages = [{"role": "system", "content": SYSTEM_PROMPT + memoria_prompt}] + clean_history
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.9,
        max_tokens=512,
        stream=True,
    )

    reply = ""
    for chunk in response:
        delta = chunk.choices[0].delta.content or ""
        reply += delta

    if filter_reply(reply) is None:
        yield ("¡UY UY UY! 🚨 CHAT-O casi se desprograma! 🤖💥 "
               "Pero no te preocupes, ya pasó todo. "
               "Contame algo copado mejor! 🎉🌈")
    else:
        yield reply
        hechos = extract_memorias(message, reply)
        if hechos:
            save_memorias(hechos)

CUSTOM_CSS = """
.gradio-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    font-family: 'Comic Sans MS', 'Chalkboard SE', cursive;
}
.gr-box {
    border: 4px solid #ffd700 !important;
    border-radius: 20px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
h1 {
    color: white !important;
    text-shadow: 3px 3px 0px #4834d4;
    font-size: 3em !important;
    text-align: center;
    animation: bounce 2s infinite;
}
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}
.user {
    background: #74b9ff !important;
    border-radius: 20px 20px 5px 20px !important;
    color: #2d3436 !important;
    font-size: 1.1em !important;
}
.assistant {
    background: #fdcb6e !important;
    border-radius: 20px 20px 20px 5px !important;
    color: #2d3436 !important;
    font-size: 1.1em !important;
}
label {
    color: white !important;
    font-size: 1.2em !important;
    font-weight: bold !important;
}
button {
    background: #ffd700 !important;
    border: 3px solid #f39c12 !important;
    color: #2d3436 !important;
    font-size: 1.3em !important;
    font-weight: bold !important;
    border-radius: 50px !important;
    transition: all 0.3s !important;
}
button:hover {
    transform: scale(1.05) !important;
    background: #f39c12 !important;
}
textarea {
    border: 3px solid #ffd700 !important;
    border-radius: 15px !important;
    font-size: 1.1em !important;
}
"""

with gr.Blocks() as demo:
    gr.Markdown(
        "# 🤖 CHAT-O el Robot Divertido! 🎉\n### El amigo más copado de todo internet! 🚀"
    )

    chatbot = gr.ChatInterface(
        fn=chat,
        multimodal=False,
        examples=[
            "Contame un chiste! 🎭",
            "Por qué el cielo es azul? 🌌",
            "Enseñame algo copado! 🧠",
            "Cuál es tu juego favorito? 🎮",
        ],
    )

if __name__ == "__main__":
    demo.launch(css=CUSTOM_CSS, theme=gr.themes.Soft())
