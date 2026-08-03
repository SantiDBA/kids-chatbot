"""
Moderation Module - Filtro de contenido inapropiado
"""
import re
from typing import Optional, Tuple


class ContentModerator:
    """Módulo para moderar contenido y asegurar aptitud para menores"""
    
    def __init__(self, bad_words: set):
        """Inicializa el moderador
        
        Args:
            bad_words: Conjunto de palabras prohibidas
        """
        self.bad_words = bad_words
    
    def filter_content(self, text: str) -> Optional[str]:
        """Filtra contenido buscando palabras prohibidas
        
        Args:
            text: Texto a filtrar
            
        Returns:
            Texto original si está limpio, None si contiene palabras prohibidas
        """
        words = text.lower().split()
        
        for bad_word in self.bad_words:
            # Buscar palabra completa o como substring (más estricto)
            if re.search(r'\b' + re.escape(bad_word) + r'\b', text, re.IGNORECASE):
                return None
        
        return text
    
    def is_safe_for_children(self, text: str) -> bool:
        """Verifica si el contenido es seguro para menores de 12 años
        
        Args:
            text: Texto a verificar
            
        Returns:
            True si es seguro, False si contiene contenido inapropiado
        """
        return self.filter_content(text) is not None
    
    def get_moderation_message(self) -> str:
        """Obtiene mensaje de error cuando el contenido no es apto
        
        Returns:
            Mensaje amigable para niños
        """
        return (
            "¡UY UY UY! 🚨 CHAT-O casi se desprograma! 🤖💥 "
            "Pero no te preocupes, ya pasó todo. "
            "Contame algo copado mejor! 🎉🌈"
        )
