"""
Madrid Knowledge - Sistema de conocimiento sobre Madrid
Preparado para Pinecone con datos mock actuales
"""

from typing import Dict, Any, Optional, List
import re


# Configuración para futuro Pinecone
USE_PINECONE = False  # Cambiar a True cuando esté disponible
PINECONE_INDEX = "madrid-knowledge"


# Base de conocimiento mock (será reemplazada por Pinecone)
MADRID_KNOWLEDGE = {
    "plaza_mayor": {
        "basic_info": "La Plaza Mayor es una plaza porticada de planta rectangular, situada en el centro histórico de Madrid. Sus orígenes se remontan al siglo XV cuando era conocida como 'Plaza del Arrabal'.",
        
        "history": "Construida durante el reinado de Felipe III (1598-1621), fue diseñada por Juan Gómez de Mora. Ha sufrido tres grandes incendios a lo largo de su historia (1631, 1672 y 1790), siendo reconstruida cada vez.",
        
        "architecture": "Edificio uniforme de cuatro plantas con 237 balcones que dan a la plaza y nueve puertas de acceso. El edificio más famoso es la Casa de la Panadería, con sus hermosos frescos.",
        
        "curiosities": "Bajo la plaza hay túneles que conectan con otros edificios históricos. La estatua ecuestre de Felipe III fue un regalo del Gran Duque de Florencia. Ha sido escenario de corridas de toros, ejecuciones públicas y mercados.",
        
        "stories": "Se dice que en los túneles subterráneos viven duendes que protegen los tesoros de los antiguos comerciantes. Los niños que visitan la plaza pueden escuchar sus risas si prestan mucha atención."
    },
    
    "palacio_real": {
        "basic_info": "El Palacio Real de Madrid es la residencia oficial de la Familia Real Española, aunque actualmente solo se usa para ceremonias de Estado. Es el palacio real más grande de Europa Occidental.",
        
        "history": "Construido en el siglo XVIII sobre los restos del antiguo Alcázar de Madrid, destruido por un incendio en 1734. Su construcción comenzó en 1738 bajo Felipe V y se completó durante el reinado de Carlos III.",
        
        "architecture": "Diseñado por Filippo Juvarra y posteriormente por Giovanni Battista Sacchetti. Tiene más de 3,400 habitaciones y una superficie de 135,000 metros cuadrados.",
        
        "curiosities": "Tiene más habitaciones que Buckingham Palace y Versalles juntos. Solo se utilizan unas 50 habitaciones para ceremonias oficiales. La Real Armería contiene una de las mejores colecciones de armas del mundo.",
        
        "stories": "Las hadas de la corte aún bailan en el Salón del Trono durante las noches de luna llena. Se dice que los espejos del palacio guardan reflejos de reinas y reyes del pasado."
    },
    
    "puerta_del_sol": {
        "basic_info": "La Puerta del Sol es una plaza del centro de Madrid, conocida por ser el kilómetro cero de las carreteras radiales del país y por albergar el famoso reloj de las campanadas de Año Nuevo.",
        
        "history": "Su nombre proviene de un sol que adornaba la entrada de un castillo que se encontraba en los extramuros medievales de la ciudad. Ha sido punto de encuentro y centro de actividad madrileña durante siglos.",
        
        "architecture": "La Casa de Correos, con su famoso reloj, domina la plaza. El edificio data del siglo XVIII y actualmente alberga la Presidencia de la Comunidad de Madrid.",
        
        "curiosities": "La placa del kilómetro cero está en el suelo, frente a la Casa de Correos. La estatua del Oso y el Madroño es el símbolo oficial de Madrid. Más de 500,000 personas se reúnen aquí cada Nochevieja.",
        
        "stories": "El oso y el madroño cobran vida cada medianoche para proteger la ciudad. Los deseos que se piden tocando la placa del kilómetro cero se cumplen si vienes con el corazón puro."
    },
    
    "mercado_san_miguel": {
        "basic_info": "El Mercado de San Miguel es un mercado gastronómico cubierto ubicado junto a la Plaza Mayor. Es el último mercado de abastos cubierto que se conserva en el centro de Madrid.",
        
        "history": "Construido en 1916 sobre el solar que ocupaba la iglesia de San Miguel de los Octoes, demolida en 1809. Fue diseñado por Alfonso Dubé de Luque siguiendo la arquitectura del hierro de principios del siglo XX.",
        
        "architecture": "Estructura de hierro forjado y cristal, ejemplo perfecto de la arquitectura del hierro madrileña. Su diseño permite una gran luminosidad natural y una sensación de amplitud.",
        
        "curiosities": "Fue completamente renovado en 2009, manteniendo su estructura original pero modernizando completamente su oferta gastronómica. Es uno de los mercados gourmet más visitados de Europa.",
        
        "stories": "Los fantasmas de los antiguos vendedores de pescado siguen vigilando que los productos sean frescos. Por las noches, los aromas de las mejores tapas flotan en el aire como por arte de magia."
    },
    
    "teatro_real": {
        "basic_info": "El Teatro Real de Madrid es el teatro de ópera de la capital española y uno de los más importantes de Europa. Es conocido por su acústica excepcional y su programación de alto nivel.",
        
        "history": "Inaugurado en 1850 por la reina Isabel II, se construyó sobre el solar del antiguo Teatro de los Caños del Peral. Ha sido testigo de las mejores representaciones operísticas de los siglos XIX, XX y XXI.",
        
        "architecture": "Diseñado por Antonio López Aguado y posteriormente modificado por Custodio Moreno. Combina elementos neoclásicos con toques románticos. Su cúpula es visible desde varios puntos de Madrid.",
        
        "curiosities": "Su escenario es uno de los más grandes del mundo y puede albergar decorados de hasta 18 metros de altura. Tiene capacidad para 1,746 espectadores distribuidos en seis plantas.",
        
        "stories": "Se dice que el fantasma de una soprano del siglo XIX aún canta en el teatro durante los ensayos. Los músicos aseguran que a veces escuchan melodías celestiales que no están en la partitura."
    }
}


def get_location_info(poi_id: str, info_type: str = "basic_info") -> str:
    """
    Obtiene información sobre una ubicación específica
    
    Args:
        poi_id: ID del POI (plaza_mayor, palacio_real, etc.)
        info_type: Tipo de info (basic_info, history, curiosities, stories)
        
    Returns:
        Información encontrada o mensaje de no disponible
    """
    
    if USE_PINECONE:
        return _search_pinecone(poi_id, info_type)
    
    # Buscar en conocimiento mock
    poi_data = MADRID_KNOWLEDGE.get(poi_id, {})
    
    if not poi_data:
        return f"Lo siento, no tengo información específica sobre '{poi_id}' en este momento."
    
    info = poi_data.get(info_type, "")
    
    if not info:
        # Fallback a información básica
        info = poi_data.get("basic_info", "Información no disponible.")
    
    return info


def search_madrid_content(query: str) -> str:
    """
    Busca contenido en toda la base de conocimiento de Madrid
    
    Args:
        query: Consulta de búsqueda
        
    Returns:
        Información relevante encontrada
    """
    
    if USE_PINECONE:
        return _search_pinecone_semantic(query)
    
    # Búsqueda simple en datos mock
    query_lower = query.lower()
    results = []
    
    # Palabras clave para identificar ubicaciones
    location_keywords = {
        "plaza mayor": "plaza_mayor",
        "palacio real": "palacio_real", 
        "palacio": "palacio_real",
        "puerta del sol": "puerta_del_sol",
        "puerta sol": "puerta_del_sol",
        "mercado san miguel": "mercado_san_miguel",
        "mercado": "mercado_san_miguel",
        "teatro real": "teatro_real",
        "teatro": "teatro_real"
    }
    
    # Buscar ubicación mencionada
    poi_id = None
    for keyword, location in location_keywords.items():
        if keyword in query_lower:
            poi_id = location
            break
    
    if poi_id:
        # Determinar qué tipo de información busca
        if any(word in query_lower for word in ["historia", "history", "histórico"]):
            return get_location_info(poi_id, "history")
        elif any(word in query_lower for word in ["arquitectura", "architecture", "edificio"]):
            return get_location_info(poi_id, "architecture")
        elif any(word in query_lower for word in ["curiosidad", "curioso", "secreto", "dato"]):
            return get_location_info(poi_id, "curiosities")
        elif any(word in query_lower for word in ["historia", "cuento", "leyenda", "story", "tale"]):
            return get_location_info(poi_id, "stories")
        else:
            return get_location_info(poi_id, "basic_info")
    
    # Búsqueda general si no se identifica ubicación específica
    return _search_general_content(query_lower)


def get_poi_stories(poi_id: str) -> str:
    """Obtiene historias específicas de un POI"""
    return get_location_info(poi_id, "stories")


def get_poi_curiosities(poi_id: str) -> str:
    """Obtiene curiosidades de un POI"""
    return get_location_info(poi_id, "curiosities")


def search_by_topic(topic: str) -> List[Dict[str, str]]:
    """
    Busca información por tema específico
    
    Args:
        topic: Tema a buscar (historia, arquitectura, etc.)
        
    Returns:
        Lista de resultados relevantes
    """
    
    results = []
    topic_lower = topic.lower()
    
    for poi_id, poi_data in MADRID_KNOWLEDGE.items():
        for info_type, content in poi_data.items():
            if topic_lower in content.lower():
                results.append({
                    "poi_id": poi_id,
                    "info_type": info_type,
                    "content": content[:200] + "..." if len(content) > 200 else content
                })
    
    return results


def _search_general_content(query: str) -> str:
    """Búsqueda general cuando no se identifica ubicación específica"""
    
    # Temas generales de Madrid
    if any(word in query for word in ["madrid", "ciudad", "capital"]):
        return """Madrid es la capital de España y una ciudad llena de historia, arte y cultura. 
Sus calles guardan siglos de historias fascinantes, desde palacios reales hasta mercados tradicionales. 
El Ratoncito Pérez conoce todos sus secretos y estará encantado de compartirlos contigo."""
    
    if any(word in query for word in ["felipe", "rey", "real", "monarquía"]):
        return """Los reyes de España han dejado su huella por toda Madrid. Felipe III creó la Plaza Mayor, 
Felipe V construyó el Palacio Real actual, y muchos otros monarcas han embellecido la ciudad a lo largo de los siglos."""
    
    if any(word in query for word in ["comida", "gastronomía", "tapas"]):
        return """Madrid es famosa por su gastronomía. El Mercado de San Miguel es perfecto para probar tapas gourmet, 
y por toda la ciudad encontrarás tabernas tradicionales y restaurantes modernos. ¡El Ratoncito Pérez conoce los mejores lugares!"""
    
    return "¡Qué pregunta tan interesante! El Ratoncito Pérez tiene muchas historias sobre Madrid. ¿Te gustaría que te cuente algo específico sobre algún lugar que estés visitando?"


# Funciones preparadas para Pinecone (implementar cuando esté disponible)
def _search_pinecone(poi_id: str, info_type: str) -> str:
    """Búsqueda en Pinecone por POI específico"""
    # TODO: Implementar con Pinecone cuando esté disponible
    # query_vector = generate_embedding(f"{poi_id} {info_type}")
    # results = pinecone_index.query(vector=query_vector, top_k=3)
    # return process_pinecone_results(results)
    
    # Fallback a mock por ahora
    return get_location_info(poi_id, info_type)


def _search_pinecone_semantic(query: str) -> str:
    """Búsqueda semántica en Pinecone"""
    # TODO: Implementar búsqueda semántica con Pinecone
    # query_vector = generate_embedding(query)
    # results = pinecone_index.query(vector=query_vector, top_k=5)
    # return process_semantic_results(results)
    
    # Fallback a búsqueda simple
    return search_madrid_content(query)


def update_knowledge_base(new_data: Dict[str, Any]):
    """Actualiza la base de conocimiento (para futuro uso con Pinecone)"""
    if USE_PINECONE:
        # TODO: Actualizar índice de Pinecone
        pass
    else:
        # Actualizar datos mock
        MADRID_KNOWLEDGE.update(new_data)


def get_available_locations() -> List[str]:
    """Obtiene lista de ubicaciones disponibles"""
    return list(MADRID_KNOWLEDGE.keys())


def get_location_summary(poi_id: str) -> Dict[str, str]:
    """Obtiene resumen completo de una ubicación"""
    
    if poi_id not in MADRID_KNOWLEDGE:
        return {"error": f"Ubicación '{poi_id}' no encontrada"}
    
    poi_data = MADRID_KNOWLEDGE[poi_id]
    
    return {
        "name": _get_location_display_name(poi_id),
        "basic_info": poi_data.get("basic_info", ""),
        "main_curiosity": poi_data.get("curiosities", "").split(".")[0] + "." if poi_data.get("curiosities") else "",
        "magical_story": poi_data.get("stories", "").split(".")[0] + "." if poi_data.get("stories") else ""
    }


def _get_location_display_name(poi_id: str) -> str:
    """Convierte POI ID a nombre display"""
    names = {
        "plaza_mayor": "Plaza Mayor",
        "palacio_real": "Palacio Real",
        "puerta_del_sol": "Puerta del Sol",
        "mercado_san_miguel": "Mercado de San Miguel",
        "teatro_real": "Teatro Real"
    }
    return names.get(poi_id, poi_id.replace("_", " ").title())