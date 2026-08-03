"""
External API Adapter - Groq client wrapper
"""
import os
from typing import Optional
from groq import Groq


class GroqAdapter:
    """Adapter para comunicación con la API de Groq"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Inicializa el adapter con la API key
        
        Args:
            api_key: API key de Groq. Si es None, usa la del entorno (GROQ_API_KEY)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Missing GROQ_API_KEY! Set it in .env file or as environment variable."
            )
        
        self.client = Groq(api_key=self.api_key)
    
    def chat_complete(
        self,
        messages: list,
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.9,
        max_tokens: int = 512,
        stream: bool = False
    ):
        """Realiza una llamada de chat completion
        
        Args:
            messages: Lista de mensajes del contexto
            model: Nombre del modelo a usar
            temperature: Temperatura del modelo (0.0-2.0)
            max_tokens: Máximo tokens en respuesta
            stream: Si True, devuelve streaming
            
        Returns:
            Response object o generator si stream=True
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
        
        return response
    
    def extract_memories(self, prompt: str) -> list:
        """Extrae memorias basadas en un prompt específico
        
        Args:
            prompt: Prompt para extraer memorias
            
        Returns:
            Lista de memorias extraídas (o lista vacía si no hay nada)
        """
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150,
        )
        
        content = response.choices[0].message.content.strip()
        
        if content.lower() == "nada":
            return []
        
        memories = [h.strip() for h in content.split("|||") if h.strip()]
        return memories  # type: ignore
