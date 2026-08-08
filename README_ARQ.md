# 🤖 CHAT-O — Arquitectura Limpia v2.0

CHAT-O es un chatbot divertido para niños, refactorizado con **Arquitectura Limpia** y principios de **Arquitectura Hexagonal**.

## 🎯 ¿Qué es la Arquitectura Limpia?

La arquitectura limpia separa la lógica de negocio de las dependencias externas (bases de datos, APIs, UI), haciendo el código:
- ✅ Más mantenible
- ✅ Más fácil de testear  
- ✅ Más flexible para cambiar tecnologías
- ✅ Más profesional

## 📁 Nueva Estructura de Archivos

```
kids-chatbot/
├── app.py                      # Entrada principal (UI con Gradio)
├── config/
│   └── settings.py             # Configuración externa (prompts, palabras prohibidas)
├── adapters/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── database.py         # Adapter para persistencia (SQLite)
│   └── external/
│       ├── __init__.py
│       └── groq.py             # Adapter para API externa (Groq)
├── use_cases/
│   ├── __init__.py
│   └── chat.py                 # Lógica principal del chatbot
├── utils/
│   ├── __init__.py
│   └── moderation.py           # Módulo de moderación de contenido
├── migrate_to_engram.py        # Script para migrar memorias a Engram
├── memoria.db                   # Base de datos SQLite (persistente)
├── .env                         # API keys y configuración
└── README.md                    # Este archivo
```

## 🏗️ Principios Aplicados

### 1. **Dependency Injection**
Los adaptadores se inyectan en el use case, no creados dentro de la lógica:

```python
chat_use_case = ChatUseCase(
    system_prompt=SYSTEM_PROMPT,
    groq_adapter=groq_adapter,      # Inyectado desde fuera
    database_adapter=database_adapter,  # Inyectado desde fuera
    content_moderator=content_moderator,   # Inyectado desde fuera
)
```

### 2. **Separación de Responsabilidades**
- **UI** (`app.py`): Solo se encarga de mostrar la interfaz con Gradio
- **Use Cases** (`use_cases/chat.py`): Lógica de negocio pura
- **Adapters** (`adapters/`): Hablan con sistemas externos
- **Config** (`config/settings.py`): Configuración externa

### 3. **Ports and Adapters**
- **Port**: Contrato que define qué necesita el use case (interfaz abstracta)
- **Adapter**: Implementación concreta (SQLite, Groq API)

## 🚀 Cómo Usar

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar API Key

Crear archivo `.env` en la raíz:

```env
GROQ_API_KEY=tu_api_key_aqui
```

### 3. Ejecutar el chatbot

```bash
python app.py
```

Abre **http://localhost:7860** en tu navegador.

## 🔄 Migración de Memorias (Opcional)

Si tienes memorias guardadas en `memoria.db` y quieres migrarlas a Engram:

```bash
python migrate_to_engram.py
```

Esto transferirá automáticamente todas las memorias al sistema de memoria persistente de OpenCode.

## 📊 Comparativa: Antes vs Después

| Aspecto | v1.0 (Antes) | v2.0 (Ahora) |
|---------|--------------|---------------|
| **Estructura** | Todo en un archivo | Modular y organizado |
| **Configuración** | Incrustada en código | Archivo externo `.py` |
| **Adaptadores** | Acoplados a la lógica | Inyectados desde fuera |
| **Testabilidad** | Difícil de testear | Fácil de probar componentes |
| **Mantenibilidad** | Difícil de entender | Clara separación de responsabilidades |

## 🎓 Beneficios de esta Arquitectura

### ✅ Para el Desarrollador
- Código más limpio y legible
- Fácil de agregar nuevas funcionalidades
- Simple cambiar de base de datos (ej: SQLite → PostgreSQL)
- Simple cambiar de API (ej: Groq → OpenAI)

### ✅ Para el Producto
- Más estable y confiable
- Fácil de debuggear problemas
- Simple implementar tests unitarios
- Mejor experiencia de usuario (menos errores)

## 🛠️ Tecnologías Usadas

- **Python 3.9+**
- **Gradio** - UI para chatbot
- **Groq API** - Modelo Llama 3.3 70B
- **SQLite** - Persistencia local (puede cambiarse)
- **Engram** - Memoria persistente (OpenCode)

## 📝 Principios SOLID Aplicados

1. **S**ingle Responsibility: Cada módulo tiene una sola responsabilidad
2. **O**pen/Closed: Fácil agregar nuevas funcionalidades sin romper existentes
3. **L**iskov Substitution: Adaptadores intercambiables
4. **I**nterface Segregation: Interfaces específicas para cada caso de uso
5. **D**ependency Inversion: Dependencia de abstracciones, no concretos

## 🎯 Siguientes Pasos (Opcionales)

- [ ] Implementar tests unitarios para cada componente
- [ ] Agregar logging con Python `logging`
- [ ] Implementar caching de respuestas frecuentes
- [ ] Agregar analytics básico (contadores de uso)
- [ ] Implementar sistema de usuarios (opcional)

## 📚 Recursos Recomendados

- ["Clean Architecture" - Robert C. Martin](https://www.amazon.com/Clean-Architecture-CleanCoders/dp/1939389097)
- ["Dependency Injection in .NET" - Martin Fowler](https://martinfowler.com/articles/dependencyInversion.html)
- [Arquitectura Hexagonal en Python](https://sourcemaking.com/design_patterns/hexagonal_architecture)

## 🤖 CHAT-O sigue siendo igual de divertido!

Aunque el código es ahora más profesional, la personalidad de CHAT-O sigue intacta:
- ✅ Habla como un pibe argentino
- ✅ Cuenta chistes y datos curiosos
- ✅ Es 100% apto para menores de 12 años
- ✅ Recuerda todo sobre el nene

¡Solo que ahora está construido con mejores fundamentos! 🚀
