"""
Logging Configuration - Configuración de logging para CHAT-O
"""
import logging
import sys


def setup_logging():
    """
    Configura logging para la aplicación.
    
    Returns:
        logging.Logger instance configurado
    """
    # Configurar formato de log
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Crear logger principal
    logger = logging.getLogger("CHAT-O")
    
    # Sub-loggers para diferentes componentes
    logger_chat = logging.getLogger("CHAT-O.chat")
    logger_db = logging.getLogger("CHAT-O.database")
    logger_api = logging.getLogger("CHAT-O.api")
    logger_moderation = logging.getLogger("CHAT-O.moderation")
    
    return logger


# Logger principal
logger = setup_logging()
