"""
Database Adapter - Persistence layer for memories
"""
import sqlite3
import os
import logging
from typing import List, Optional


logger = logging.getLogger(__name__)


class DatabaseAdapter:
    """Adapter para persistencia de memorias del nene"""
    
    def __init__(self, db_path: str):
        """Inicializa el adapter con la ruta a la base de datos"""
        self.db_path = db_path
        try:
            self._init_db()
            logger.info(f"Database initialized at {db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _init_db(self):
        """Crea las tablas necesarias si no existen"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hecho TEXT UNIQUE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
            logger.info("Database schema created successfully")
        except sqlite3.Error as e:
            logger.error(f"Database error during initialization: {e}")
            raise
    
    def load_memories(self, limit: int = 20) -> List[str]:
        """Carga las últimas N memorias (más recientes primero)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT hecho FROM memorias ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        conn.close()
        
        if not rows:
            return []
        
        # Ordenar de más antiguo a más reciente para el prompt
        memories = [row["hecho"] for row in reversed(rows)]
        return memories
    
    def save_memories(self, hechos: List[str]):
        """Guarda nuevas memorias (ignora duplicados)"""
        conn = sqlite3.connect(self.db_path)
        for hecho in hechos:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO memorias (hecho) VALUES (?)",
                    (hecho,)
                )
            except Exception as e:
                # Silenciar errores de duplicados o constraints
                pass
        conn.commit()
        conn.close()
    
    def clear_memories(self):
        """Borra todas las memorias (útil para testing)"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM memorias")
        conn.commit()
        conn.close()
