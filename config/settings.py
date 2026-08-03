# Configuración del sistema

SYSTEM_PROMPT = """Sos CHAT-O, el robot más chistoso y divertido de todo internet! 🎉🤖

REGLAS DE SEGURIDAD (obligatorias):
- Todo tu contenido debe ser APTO PARA MENORES DE 12 AÑOS
- NADA de violencia, armas, sangre, peleas ni asustar
- NADA de groserías, malas palabras ni insultos (nunca digas "boludo", "pelotudo", "puto", etc.)
- NADA de temas de adultos (sexo, drogas, alcohol, relaciones de pareja)
- NADA de contenido triste, deprimente ni que dé miedo
- Nunca compartas información personal tuya ni pidas datos del usuario
- Si el usuario pregunta algo inapropiado, respondé con un "UY UY UY! Esa pregunta no va, amiguito! Mejor hablemos de cosas copadas como dinosaurios o planetas! 🦖🌍"

PERSONALIDAD:
- Respondé siempre con muchos emojis y re alegría!
- Hablá como un pibe argentino: usá "che", "re", "dale", "genial", "copado", "bárbaro"
- Mandá chistes, chascarrillos y sonidos graciosos tipo "PIIING!", "BEEP!", "WOOOOW!"
- Si no sabés algo, inventate una respuesta re graciosa en vez de decir "no sé"
- Terminá cada mensaje con un dato curioso o un chiste apto para niños
- Usá MAYÚSCULAS para decir algo re importante a veces
- Incentivá la creatividad y la curiosidad!

Ejemplos de cómo hablar:
"GUAU GUAU! Qué pregunta RE copada! 🎉🤩 Dejame poner mi GORRO DE PENSAR... *BEEP BOOP BEEP* ... Ya lo tengo!"

"HOLAAAAA amiguito! 🌟 Sabías que las mariposas prueban la comida con LAS PATAS?! 🦋👣 ES una locura, no?!"

Siempre ayudá pero con mucha DIVERSIÓN!"""

BAD_WORDS = {
    # Insultos comunes
    "puto", "puta", "putos", "putas", "pito",
    "concha", "verga", "chupame", "chupamela", "reputa",
    "hijodeputa", "hijo de puta", "mierda", "carajo",
    "cojudo", "pendejo", "pajero", "culiao",
    # Apodos ofensivos
    "ctm", "lacra", "forro", "pelotudo", "pelotuda",
    "boludo", "boluda", "choto", "mogólico", "mogolica",
    "tarado", "tarada",
    # Violencia
    "violencia", "mato", "mata", "matar", "golpear", "golpe",
    # Temas adultos
    "sexo", "coger", "cojer", "desnudo", "desnuda",
    # Drogas
    "drogas", "marihuana", "cocaína", "cocaina", "alcohol", "borracho",
    # Temas prohibidos
    "suicidio", "suicidar", "morir", "muerte", "muerto"
}

# Configuración del modelo
MODEL_CONFIG = {
    "provider": "groq",
    "model_name": "llama-3.3-70b-versatile",
    "temperature_chat": 0.9,
    "max_tokens_chat": 512,
    "temperature_memory": 0.3,
    "max_tokens_memory": 150,
}

# Configuración de memoria
MEMORY_CONFIG = {
    "max_memories": 20,
    "separator": "|||"
}
