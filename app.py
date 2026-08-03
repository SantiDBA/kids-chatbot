"""
CHAT-O Kids Chatbot - Aplicación principal con arquitectura limpia

Esta es la entrada del sistema que inicializa todos los componentes
y configura la interfaz de usuario con Gradio.
"""
import os
import sys
from dotenv import load_dotenv

# Configuración de directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cargar variables de entorno
dotenv_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

# Importar componentes con arquitectura limpia
from config.settings import (
    SYSTEM_PROMPT,
    BAD_WORDS,
    MODEL_CONFIG,
    MEMORY_CONFIG
)
from adapters.data.database import DatabaseAdapter
from adapters.external.groq import GroqAdapter
from utils.moderation import ContentModerator
from use_cases.chat import ChatUseCase

# Importar Gradio para la UI
import gradio as gr


def create_app():
    """
    Factory function que crea y configura toda la aplicación.
    
    Esta función encapsula la creación de todos los componentes,
    siguiendo el patrón Dependency Injection.
    
    Returns:
        ChatUseCase instance configurado y listo para usar
    """
    # 1. Inicializar adaptadores
    
    # Adapter de base de datos (SQLite)
    db_path = os.path.join(BASE_DIR, "memoria.db")
    database_adapter = DatabaseAdapter(db_path)
    
    # Adapter de API externa (Groq)
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError(
            "Missing GROQ_API_KEY! Set it in .env file or as environment variable."
        )
    groq_adapter = GroqAdapter(groq_api_key)
    
    # 2. Inicializar componentes de negocio
    
    # Moderador de contenido
    content_moderator = ContentModerator(BAD_WORDS)
    
    # Use case principal (lógica de negocio)
    chat_use_case = ChatUseCase(
        system_prompt=SYSTEM_PROMPT,
        groq_adapter=groq_adapter,
        database_adapter=database_adapter,
        content_moderator=content_moderator,
        memory_config=MEMORY_CONFIG
    )
    
    return chat_use_case


def chat_fn(message: str, history):
    """
    Función de callback para Gradio ChatInterface.
    
    Esta función actúa como puente entre la UI y el use case principal.
    
    Args:
        message: Mensaje del usuario (el nene)
        history: Historial de conversaciones anteriores
        
    Yields:
        Respuesta formateada para Gradio
    """
    chat_use_case = create_app()
    
    try:
        # Procesar mensaje y obtener respuesta + memorias extraídas
        for reply, _ in chat_use_case.process_message(message, history):
            yield reply
            
    except Exception as e:
        # Error handling - mostrar mensaje amigable
        error_messages = [
            "¡Uy! Parece que CHAT-O está pensando mucho... 🤔",
            "🤖 *BEEP BOOP* ... Creo que necesito un descanso. ¡Contame algo copado!",
            "¡POW! 💥 Hubo un pequeño problema técnico. ¡Pero no te preocupes!"
        ]
        yield error_messages[0]


# Configuración CSS personalizada para la UI
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


def main():
    """
    Punto de entrada principal de la aplicación.
    
    Inicializa y lanza la interfaz de usuario con Gradio.
    """
    # Crear use case con factory function
    chat_use_case = create_app()
    
    # Configurar y lanzar demo con Gradio
    with gr.Blocks(theme=gr.themes.Soft(), css=CUSTOM_CSS) as demo:
        gr.Markdown(
            "# 🤖 CHAT-O el Robot Divertido! 🎉\n### El amigo más copado de todo internet! 🚀"
        )
        
        # Configurar chat interface con callback
        chatbot = gr.ChatInterface(
            fn=chat_fn,
            multimodal=False,
            examples=[
                "Contame un chiste! 🎭",
                "Por qué el cielo es azul? 🌌",
                "Enseñame algo copado! 🧠",
                "Cuál es tu juego favorito? 🎮",
            ],
        )
    
    # Lanzar aplicación
    demo.launch(
        server_name="0.0.0.0",  # Habilitar acceso de red
        server_port=7860        # Puerto de Gradio
    )


if __name__ == "__main__":
    main()
