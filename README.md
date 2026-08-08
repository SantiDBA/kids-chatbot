# 🤖 CHAT-O — Chatbot divertido para chicos

CHAT-O es un chatbot pensado para niños, con una interfaz colorida y divertida. Habla en español argentino, cuenta chistes, da datos curiosos y siempre responde de forma segura y apta para menores de 12 años.

## ✨ Funcionalidades

- **Interfaz moderna** con FastAPI y frontend estático, colores vibrantes y estilo divertido
- **Moderación parental** — bloquea contenido inapropiado, violencia y malas palabras
- **Memoria persistente** — recuerda datos del nene (nombre, edad, gustos, mascotas, etc.)
- **Streaming de respuestas** con el modelo `llama-3.3-70b-versatile` de Groq
- **100% en español argentino** — "che", "re", "copado", "bárbaro"

## 🚀 Cómo usar

1. Creá un archivo `.env` con tu API key de Groq:

```
GROQ_API_KEY=gsk_tu_api_key_aqui
```

2. Instalá las dependencias y ejecutá:

```bash
pip install -r requirements.txt
venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 7860
```

3. Abrí **http://localhost:7860** en el navegador

## 🪟 Versión .exe para Windows

Ejecutá `build_exe.bat` para generar un ejecutable portable.
