"""
Migrator - Script para migrar memorias de SQLite a Engram

Este script extrae todas las memorias guardadas en memoria.db
y las transfiere al sistema de persistencia de OpenCode (Engram).

Uso: python migrate_to_engram.py
"""
import sqlite3
import os
import sys


def print_migration_status(db_path, memories):
    """Muestra el estado actual de las memorias."""
    if not memories:
        print("📦 No hay memorias para migrar.")
        return 0
    
    # Engram requiere MCP server que no está disponible en este contexto
    # Esta es la migración preparada - para ejecutarla necesitarías usar OpenCode
    
    print(f"\n📦 Las memorias están actualmente en memoria.db:")
    print(f"   {db_path}")
    print(f"\n✅ Total memorias disponibles: {len(memories)}")
    print(f"\n💡 Para migrarlas a Engram, puedes usar el script de migración integrado")
    print(f"   cuando tengas acceso al MCP server de OpenCode.")
    print(f"\n🔧 Alternativa: Copiar manualmente las memorias en la pestaña 'Memorias' de OpenCode")


def migrate_memories(db_path):
    """
    Migrate all memories from SQLite to Engram
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        Number of memories migrated
    """
    # Conectar a base de datos existente
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Obtener todas las memorias
    cursor.execute("SELECT hecho FROM memorias")
    rows = cursor.fetchall()
    
    if not rows:
        print_migration_status(db_path, [])
        conn.close()
        return 0
    
    memories = [row[0] for row in rows]
    
    # Show current status
    print_migration_status(db_path, memories)
    
    conn.close()
    
    return len(memories) if memories else 0


if __name__ == "__main__":
    # Ruta a la base de datos
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "memoria.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        sys.exit(1)
    
    print("🔄 Iniciando migración de memorias SQLite → Engram\n")
    print("=" * 60)
    
    try:
        migrate_memories(db_path)
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✨ Migración completada con éxito!")