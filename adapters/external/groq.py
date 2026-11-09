"""
External API Adapter - OpenAI-compatible LLM client (Groq / Omniroute / etc.)
"""
import os
from typing import Optional
from groq import Groq


class GroqAdapter:
    """Adapter para comunicación con APIs OpenAI-compatible (Groq, Omniroute, etc.)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
    ):
        """Inicializa el adapter.

        Args:
            api_key: API key. Si es None, usa LLM_API_KEY o GROQ_API_KEY.
            base_url: Base URL OpenAI-compatible (ej. http://localhost:20128/v1
                para Omniroute). Si es None, usa LLM_BASE_URL o el default de Groq.
            default_model: Modelo por defecto. Si es None, usa LLM_MODEL o MODEL_NAME.
        """
        self.api_key = api_key or os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY")
        self.base_url = base_url or os.getenv("LLM_BASE_URL") or None
        self.default_model = (
            default_model
            or os.getenv("LLM_MODEL")
            or os.getenv("MODEL_NAME")
            or "llama-3.3-70b-versatile"
        )

        if not self.api_key:
            raise ValueError(
                "Missing API key! Set LLM_API_KEY (or GROQ_API_KEY) in .env."
            )

        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        self.client = Groq(**client_kwargs)

    def chat_complete(
        self,
        messages: list,
        model: str = None,
        temperature: float = 0.9,
        max_tokens: int = 512,
        stream: bool = False
    ):
        """Realiza una llamada de chat completion."""
        response = self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )
        return response

    def extract_memories(self, prompt: str) -> list:
        """Extrae memorias basadas en un prompt específico."""
        response = self.client.chat.completions.create(
            model=self.default_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150,
        )

        content = (response.choices[0].message.content or "").strip()
        if content.lower() == "nada":
            return []
        return [h.strip() for h in content.split("|||") if h.strip()]
