"""
Chat Use Case - Lógica principal del chatbot
"""
from typing import List, Optional, Generator, Tuple
import sys


class ChatUseCase:
    """
    Use case principal que encapsula toda la lógica del chat.
    
    Esta clase representa el caso de uso "Procesar mensaje de chat"
    y coordina todos los adaptadores necesarios.
    """
    
    def __init__(
        self,
        system_prompt: str,
        groq_adapter,
        database_adapter,
        content_moderator,
        memory_config: dict = None  # type: ignore
    ):
        """Inicializa el use case con todos los adaptadores
        
        Args:
            system_prompt: Prompt del sistema con personalidad de CHAT-O
            groq_adapter: Adapter para comunicación con Groq API
            database_adapter: Adapter para persistencia de memorias
            content_moderator: Moderador de contenido
            memory_config: Configuración de memoria (opcional)
        """
        self.system_prompt = system_prompt
        self.groq_adapter = groq_adapter
        self.database_adapter = database_adapter
        self.content_moderator = content_moderator
        self.memory_config = memory_config or {
            "max_memories": 20,
            "separator": "|||"
        }
    
    def process_message(
        self,
        message: str,
        history: List[dict] = None
    ) -> Generator[Tuple[str, List[str]], None, None]:
        """
        Procesa un mensaje de chat completo.
        
        Args:
            message: Mensaje del usuario (el nene)
            history: Historial de conversaciones previas
            
        Yields:
            Tuple[str, List[str]]: (respuesta, memorias_extraidas)
        """
        # 1. Preparar contexto con memorias existentes
        memories = self.database_adapter.load_memories(
            limit=self.memory_config["max_memories"]
        ) or []
        
        memoria_prompt = ""
        if memories:
            memorias_texto = "\n".join(f"- {m}" for m in memories)
            memoria_prompt = f"\n\nCOSAS QUE CHAT-O RECUERDA:\n{memorias_texto}\n\n" \
                            "Usá esta información cuando sea relevante. " \
                            "Si el nene menciona algo nuevo, actualizá el recuerdo."
        
        # 2. Construir mensajes para la API
        clean_history = []
        for msg in (history or []):
            if isinstance(msg, dict):
                clean_history.append({
                    k: v for k, v in msg.items()
                    if k in ("role", "content")
                })
            elif isinstance(msg, (list, tuple)) and len(msg) >= 2:
                clean_history.append({"role": "user", "content": str(msg[0])})
                clean_history.append({"role": "assistant", "content": str(msg[1])})
        
        messages = [
            {"role": "system", "content": self.system_prompt + memoria_prompt}
        ] + clean_history
        messages.append({"role": "user", "content": message})
        
        # 3. Obtener respuesta de la API
        try:
            response_stream = self.groq_adapter.chat_complete(
                messages=messages,
                temperature=self.memory_config.get("temperature_chat", 0.9),
                max_tokens=self.memory_config.get("max_tokens_chat", 512),
                stream=True
            )
            
            # Consumir streaming
            reply = ""
            for chunk in response_stream:
                delta = chunk.choices[0].delta.content or ""
                reply += delta
            
        except Exception as e:
            # Error handling - devolver mensaje amigable
            error_messages = [
                "¡Uy! Parece que CHAT-O está pensando mucho... 🤔",
                "🤖 *BEEP BOOP* ... Creo que necesito un descanso. ¡Contame algo copado!",
                "¡POW! 💥 Hubo un pequeño problema técnico. ¡Pero no te preocupes!"
            ]
            import random
            reply = random.choice(error_messages)
        
        # 4. Moderar respuesta
        filtered_reply = self.content_moderator.filter_content(reply)
        
        if filtered_reply is None:
            yield (self.content_moderator.get_moderation_message(), memories)
            return
        
        # 5. Extraer memorias de la conversación
        try:
            extract_prompt = f"""Analizá esta conversación y extraé SOLO datos importantes para recordar a futuro:
- Datos del nene (nombre, edad, color favorito, mascotas, cumpleaños, etc.)
- Temas que le gustan (juegos, dinosaurios, planetas, etc.)
- Cualquier cosa que haya dicho que sea útil recordar

NO inventes nada. Si no hay nada importante, respondé "Nada".

Mensaje del nene: {message}
Respuesta de CHAT-O: {filtered_reply}

Datos importantes (máximo 2, separados por |||):"""
            
            memories_extracted = self.groq_adapter.extract_memories(extract_prompt) or []
            
            # 6. Guardar memorias en base de datos
            if memories_extracted:
                self.database_adapter.save_memories(memories_extracted)
            
        except Exception:
            # Silenciar errores de extracción de memorias
            pass
        
        yield (filtered_reply, memories_extracted)
