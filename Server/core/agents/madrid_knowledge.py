"""
Madrid Knowledge - Sistema de conocimiento sobre Madrid
Preparado para Pinecone con datos mock actuales
Incluye POIs de la ruta del Ratoncito Pérez (10 puntos) + ubicaciones clásicas
"""

from typing import Dict, Any, List

# ============================
# Configuración para futuro Pinecone
# ============================
USE_PINECONE = False  # Cambiar a True cuando esté disponible
PINECONE_INDEX = "madrid-knowledge"

# ============================
# Base de conocimiento mock
# ============================
# Estructura por POI:
#   { poi_id: { "basic_info": str, "history": str, "architecture": str, "curiosities": str, "stories": str } }
MADRID_KNOWLEDGE: Dict[str, Dict[str, str]] = {
    # ---------- Ruta Ratoncito Pérez ----------
    "plaza_oriente": {
        "basic_info": "La Plaza de Oriente es un espacio ajardinado entre el Palacio Real y el Teatro Real. Es conocida por sus estatuas de reyes y su trazado elíptico.",
        "history": "Proyectada en el siglo XIX durante el reinado de Isabel II, su configuración actual se debe a las reformas urbanas que despejaron el entorno del Palacio.",
        "architecture": "Jardines historicistas con parterres geométricos y alineaciones de estatuas. La plaza actúa como foyer urbano entre el palacio (barroco tardío/neo-clásico) y el teatro (neoclásico).",
        "curiosities": "Las estatuas de reyes que ves son copias: las originales están repartidas por distintas ciudades. Antaño se pensó colocarlas en la cornisa del Palacio Real, pero pesaban demasiado.",
        "stories": "Al caer la tarde, los reyes de piedra susurran anécdotas del pasado. El Ratoncito Pérez dice que, si te quedas muy quieto, puedes oír cómo cuentan chistes de corte."
    },
    "plaza_ramales": {
        "basic_info": "La Plaza de Ramales es una plaza tranquila junto al Palacio Real y la Plaza de Oriente, con terrazas y restos arqueológicos visibles bajo cristal.",
        "history": "Se sitúa sobre el antiguo convento de San Juan, derribado en el siglo XIX. El área conserva memoria del Madrid conventual y palaciego.",
        "architecture": "Espacio abierto con pavimento contemporáneo y lucernarios que dejan ver restos arqueológicos. Fachadas residenciales del XIX y XX enmarcan la plaza.",
        "curiosities": "Bajo el suelo se han hallado restos de estructuras históricas. Es un buen alto en el camino entre el Palacio y la zona de Ópera.",
        "stories": "Cuentan que un ratón guardián hace ronda por los lucernarios para que ningún tesoro olvide su historia. Si lo saludas, te guiña un ojo."
    },
    "calle_vergara": {
        "basic_info": "La Calle de Vergara conecta el entorno del Palacio Real con la Plaza de Isabel II (Ópera). Es una vía histórica del centro.",
        "history": "Su trazado actual se consolidó entre los siglos XVIII y XIX, articulando el barrio entre palacios y teatros.",
        "architecture": "Edificios residenciales de varias alturas, con balcones de hierro y locales tradicionales en planta baja.",
        "curiosities": "En pocos metros puedes pasar del ambiente palaciego a la atmósfera de cafés y música de Ópera.",
        "stories": "El Ratoncito Pérez dice que, de balcón en balcón, los gatos del barrio practican ópera maullada al anochecer."
    },
    "plaza_isabel_ii": {
        "basic_info": "La Plaza de Isabel II, conocida como Ópera, se abre frente al Teatro Real. Es punto de encuentro habitual y zona peatonal.",
        "history": "Nació con las reformas del entorno del Teatro Real en el siglo XIX y ha sido remodelada varias veces para priorizar al peatón.",
        "architecture": "Plaza dura con fuentes, arbolado y vistas al Teatro Real. Conecta con calles comerciales y culturales.",
        "curiosities": "El nombre popular 'Ópera' viene del Teatro Real, protagonista indiscutible del entorno.",
        "stories": "Hay noches en que una nota musical se queda flotando en la plaza. Dicen que los ratones la guardan en un bolsillo por si falta un do en los ensayos."
    },
    "calle_arenal_1": {
        "basic_info": "La Calle del Arenal une la zona de Ópera con Puerta del Sol. Este primer tramo conserva comercios tradicionales y mucha vida peatonal.",
        "history": "Vía histórica que comunicaba el entorno del Alcázar/Palacio con el corazón comercial de Madrid.",
        "architecture": "Soportales puntuales, portales de madera, escaparates clásicos y edificios residenciales con balcones.",
        "curiosities": "Antiguamente fue paso de carruajes; hoy es una arteria peatonal con músicos y chocolate con churros muy cerca.",
        "stories": "Si caminas despacio, oirás el rumor de cuentos que los aparadores cuentan a quien mira con atención."
    },
    "calle_bordadores": {
        "basic_info": "La Calle de Bordadores atraviesa el casco histórico entre Arenal y Mayor. Debe su nombre a los gremios de artesanos.",
        "history": "Tradicionalmente vinculada a oficios textiles y comercio, conserva el trazado de la villa medieval.",
        "architecture": "Calle estrecha, con fachadas de diferentes épocas y locales clásicos. Mantiene el sabor de barrio.",
        "curiosities": "Su nombre alude a los antiguos talleres de bordado que surtían a iglesias y corte.",
        "stories": "Los hilos invisibles de los bordadores aún cosen historias entre faroles. El Ratoncito Pérez colecciona retales de memoria por aquí."
    },
    "plazuela_san_gines": {
        "basic_info": "La Plazuela de San Ginés es un rincón con sabor a Madrid castizo, junto a la iglesia homónima y célebre por su chocolatería.",
        "history": "El entorno se formó alrededor de la iglesia de San Ginés, una de las parroquias más antiguas de la ciudad.",
        "architecture": "Espacio íntimo con pavimento tradicional, faroles y fachadas históricas; muy fotogénico.",
        "curiosities": "Aquí se encuentra una de las chocolaterías más famosas para tomar churros con chocolate.",
        "stories": "Al amanecer, el aroma a chocolate despierta a los cuentos. Los niños dicen que un ratón muy dulce vigila que no falte azúcar."
    },
    "pasadizo_san_gines": {
        "basic_info": "El Pasadizo de San Ginés es un angosto corredor que conecta Arenal con la plazuela. Es un clásico del centro histórico.",
        "history": "Viejo atajo urbano que facilitaba el paso entre zonas de mucho tránsito comercial.",
        "architecture": "Pasaje estrecho, con paredes cercanas y rótulos tradicionales que crean un ambiente muy castizo.",
        "curiosities": "A menudo verás colas para el chocolate. El pasadizo es escenario de mil fotos y canciones callejeras.",
        "stories": "Dicen que aquí los cuentos corren más deprisa porque el pasadizo les hace cosquillas en las palabras."
    },
    "calle_arenal_2": {
        "basic_info": "La Calle del Arenal, en su tramo final, desemboca en la Puerta del Sol. Es una de las vías peatonales más transitadas.",
        "history": "El crecimiento de Madrid la convirtió en eje comercial clave entre Sol y el entorno palaciego.",
        "architecture": "Edificios comerciales y residenciales, con carteles históricos y esquinas icónicas.",
        "curiosities": "En pocos minutos puedes ir de la ópera al kilómetro cero, con música callejera casi a cualquier hora.",
        "stories": "Los pasos de los viajeros dejan chispas de curiosidad. El Ratoncito Pérez las usa para encender lamparitas de historias."
    },
    "museo_raton_perez": {
        "basic_info": "El Museo del Ratoncito Pérez, cerca de la Puerta del Sol, está dedicado al popular personaje infantil y su leyenda.",
        "history": "Inspirado en el cuento de 1894 de Luis Coloma, el museo narra la evolución del mito y su arraigo en Madrid.",
        "architecture": "Espacio expositivo íntimo con vitrinas, dioramas y objetos relacionados con la tradición del diente.",
        "curiosities": "Aquí se conservan cartas, dientes simbólicos y recuerdos de niños de todo el mundo.",
        "stories": "En el museo, los dientes brillan como estrellas. Si susurras un deseo, un ratoncito mensajero lo lleva volando por la noche."
    },

    # ---------- Ubicaciones clásicas (ya existentes) ----------
    "plaza_mayor": {
        "basic_info": "La Plaza Mayor es una plaza porticada de planta rectangular en el centro histórico de Madrid. Sus orígenes se remontan al siglo XV, cuando era la 'Plaza del Arrabal'.",
        "history": "Construida en época de Felipe III, diseñada por Juan Gómez de Mora. Sufrió incendios en 1631, 1672 y 1790, y fue reconstruida.",
        "architecture": "Conjunto uniforme de cuatro plantas con 237 balcones y nueve accesos. La Casa de la Panadería luce frescos en su fachada.",
        "curiosities": "La estatua ecuestre de Felipe III preside la plaza. Ha sido escenario de mercados y actos públicos durante siglos.",
        "stories": "Cuentan que bajo los soportales viven duendecillos que esconden risas y rumores de antaño."
    },
    "palacio_real": {
        "basic_info": "El Palacio Real de Madrid es la residencia oficial de la Familia Real (uso ceremonial). Es uno de los palacios más grandes de Europa occidental.",
        "history": "Se levantó en el siglo XVIII sobre el Alcázar, destruido por un incendio en 1734. Iniciado bajo Felipe V y culminado en tiempos de Carlos III.",
        "architecture": "Trazas de Juvarra y Sacchetti; más de 3.000 estancias y una gran plaza de armas.",
        "curiosities": "La Real Armería alberga piezas destacadas. Solo una parte del palacio se usa en actos oficiales.",
        "stories": "Dicen que en noches de luna llena los espejos susurran pasos de corte."
    },
    "puerta_del_sol": {
        "basic_info": "La Puerta del Sol es una plaza céntrica de Madrid, famosa por el Kilómetro Cero y el reloj de las campanadas.",
        "history": "Tomó su nombre de un sol en la antigua muralla. Ha sido nodo urbano y social durante siglos.",
        "architecture": "La Casa de Correos, del siglo XVIII, domina la plaza.",
        "curiosities": "La placa del Kilómetro Cero marca el inicio de las carreteras radiales.",
        "stories": "El Oso y el Madroño cobran vida a medianoche para vigilar la ciudad, según dicen."
    },
    "mercado_san_miguel": {
        "basic_info": "El Mercado de San Miguel es un mercado gastronómico cubierto junto a la Plaza Mayor.",
        "history": "Construido en 1916 sobre el solar de una antigua iglesia; reformado en 2009.",
        "architecture": "Estructura de hierro y vidrio, característica de la arquitectura del hierro madrileña.",
        "curiosities": "Es uno de los mercados gourmet más populares de la ciudad.",
        "stories": "Los fantasmas de tenderos exigen que el pescado siempre sea fresquísimo."
    },
    "teatro_real": {
        "basic_info": "El Teatro Real es el gran teatro de ópera de Madrid, reconocido por su acústica y programación.",
        "history": "Inaugurado en 1850 por Isabel II; ha vivido reformas y reaperturas a lo largo de su historia.",
        "architecture": "Edificio de inspiración neoclásica con modificaciones posteriores; gran caja escénica.",
        "curiosities": "El escenario puede albergar decorados muy altos y complejos.",
        "stories": "Algunos músicos juran oír notas misteriosas durante los ensayos silenciosos."
    },
}

# ============================
# Búsqueda y consulta
# ============================

def get_location_info(poi_id: str, info_type: str = "basic_info") -> str:
    """
    Obtiene información sobre una ubicación específica.
    Si el POI o el tipo de información no existen, devuelve un mensaje seguro (sin inventar).
    """
    if USE_PINECONE:
        return _search_pinecone(poi_id, info_type)

    poi_data = MADRID_KNOWLEDGE.get(poi_id)
    if not poi_data:
        return f"Lo siento, no tengo información específica sobre '{poi_id}' en este momento."

    info = poi_data.get(info_type)
    if not info:
        # Fallback controlado a información básica si existe
        info = poi_data.get("basic_info")
        if not info:
            return "Información no disponible por ahora."
    return info


def search_madrid_content(query: str) -> str:
    """
    Busca contenido en toda la base de conocimiento (mock o Pinecone).
    Intenta reconocer el lugar y el tipo de información pedido.
    """
    if USE_PINECONE:
        return _search_pinecone_semantic(query)

    query_lower = query.lower().strip()

    # Palabras clave → POI
    location_keywords = {
        # Ruta RP
        "plaza de oriente": "plaza_oriente", "oriente": "plaza_oriente",
        "plaza de ramales": "plaza_ramales", "ramales": "plaza_ramales",
        "calle vergara": "calle_vergara", "vergara": "calle_vergara",
        "plaza isabel ii": "plaza_isabel_ii", "ópera": "plaza_isabel_ii", "opera": "plaza_isabel_ii",
        "calle del arenal": "calle_arenal_1", "calle arenal": "calle_arenal_1", "arenal": "calle_arenal_1",
        "calle de bordadores": "calle_bordadores", "bordadores": "calle_bordadores",
        "plazuela de san ginés": "plazuela_san_gines", "san ginés": "plazuela_san_gines", "san gines": "plazuela_san_gines",
        "pasadizo de san ginés": "pasadizo_san_gines", "pasadizo san ginés": "pasadizo_san_gines",
        "museo ratoncito pérez": "museo_raton_perez", "museo raton perez": "museo_raton_perez", "museo ratoncito perez": "museo_raton_perez",

        # Clásicos
        "plaza mayor": "plaza_mayor",
        "palacio real": "palacio_real", "palacio": "palacio_real",
        "puerta del sol": "puerta_del_sol", "puerta sol": "puerta_del_sol",
        "mercado san miguel": "mercado_san_miguel", "mercado de san miguel": "mercado_san_miguel",
        "teatro real": "teatro_real", "teatro": "teatro_real",
    }

    matched_poi: str = ""
    for keyword, location in location_keywords.items():
        if keyword in query_lower:
            matched_poi = location
            break

    if matched_poi:
        # Tipo de información solicitado
        if any(word in query_lower for word in ["historia", "history", "histórico"]):
            return get_location_info(matched_poi, "history")
        if any(word in query_lower for word in ["arquitectura", "architecture", "edificio", "fachada", "estilo"]):
            return get_location_info(matched_poi, "architecture")
        if any(word in query_lower for word in ["curiosidad", "curioso", "secreto", "dato"]):
            return get_location_info(matched_poi, "curiosities")
        if any(word in query_lower for word in ["leyenda", "cuento", "story", "tale", "historia mágica"]):
            return get_location_info(matched_poi, "stories")
        return get_location_info(matched_poi, "basic_info")

    # Búsqueda general si no se identifica lugar
    return _search_general_content(query_lower)


def get_poi_stories(poi_id: str) -> str:
    """Obtiene historias específicas de un POI"""
    return get_location_info(poi_id, "stories")


def get_poi_curiosities(poi_id: str) -> str:
    """Obtiene curiosidades de un POI"""
    return get_location_info(poi_id, "curiosities")


def search_by_topic(topic: str) -> List[Dict[str, str]]:
    """
    Busca información por tema (historia, arquitectura, etc.) en todos los POIs.
    Devuelve fragmentos cortos y seguros.
    """
    results: List[Dict[str, str]] = []
    topic_lower = topic.lower()
    for poi_id, poi_data in MADRID_KNOWLEDGE.items():
        for info_type, content in poi_data.items():
            if content and topic_lower in content.lower():
                snippet = content[:200] + "..." if len(content) > 200 else content
                results.append({"poi_id": poi_id, "info_type": info_type, "content": snippet})
    return results


def _search_general_content(query: str) -> str:
    """
    Respuesta general cuando no se identifica una ubicación concreta.
    Mantiene un tono seguro y sin inventar.
    """
    if any(word in query for word in ["madrid", "ciudad", "capital"]):
        return ("Madrid es la capital de España y una ciudad con abundante patrimonio, arte y gastronomía. "
                "Podemos hablar de sus plazas históricas, sus mercados y sus teatros; dime qué te interesa.")

    if any(word in query for word in ["felipe", "rey", "real", "monarquía"]):
        return ("La monarquía ha dejado huella en Madrid, desde la Plaza Mayor en tiempos de Felipe III "
                "hasta el Palacio Real del siglo XVIII. ¿Quieres un lugar concreto?")

    if any(word in query for word in ["comida", "gastronomía", "tapas", "chocolate", "churros"]):
        return ("La zona de San Ginés y el Mercado de San Miguel son referencias clásicas para probar dulces y tapas. "
                "¿Prefieres recomendaciones por barrio o cerca de tu ruta?")

    return ("¡Qué buena pregunta! Si me dices un lugar (por ejemplo, Plaza de Oriente o Calle del Arenal), "
            "te doy datos concretos, curiosidades o una micro-historia.")

# ============================
# Pinecone (placeholders)
# ============================

def _search_pinecone(poi_id: str, info_type: str) -> str:
    """(Placeholder) Búsqueda en Pinecone por POI específico"""
    # TODO: Implementar con Pinecone cuando esté disponible
    return MADRID_KNOWLEDGE.get(poi_id, {}).get(info_type, "") or "Información no disponible por ahora."


def _search_pinecone_semantic(query: str) -> str:
    """(Placeholder) Búsqueda semántica en Pinecone"""
    # TODO: Implementar búsqueda semántica con Pinecone
    return search_madrid_content(query)

# ============================
# Utilidades
# ============================

def update_knowledge_base(new_data: Dict[str, Any]):
    """Actualiza la base de conocimiento (mock o Pinecone)"""
    if USE_PINECONE:
        # TODO: Actualizar índice de Pinecone
        return
    MADRID_KNOWLEDGE.update(new_data)


def get_available_locations() -> List[str]:
    """Devuelve lista de POIs disponibles (ids)"""
    return list(MADRID_KNOWLEDGE.keys())


def get_location_summary(poi_id: str) -> Dict[str, str]:
    """Obtiene un pequeño resumen seguro de una ubicación"""
    if poi_id not in MADRID_KNOWLEDGE:
        return {"error": f"Ubicación '{poi_id}' no encontrada"}
    poi_data = MADRID_KNOWLEDGE[poi_id]
    def first_sentence(text: str) -> str:
        if not text:
            return ""
        # Corta por punto si existe
        p = text.find(".")
        return (text[:p+1] if p != -1 else text).strip()

    return {
        "name": _get_location_display_name(poi_id),
        "basic_info": poi_data.get("basic_info", ""),
        "main_curiosity": first_sentence(poi_data.get("curiosities", "")),
        "magical_story": first_sentence(poi_data.get("stories", "")),
    }


def _get_location_display_name(poi_id: str) -> str:
    """Convierte el id del POI en nombre legible"""
    names = {
        # Ruta RP
        "plaza_oriente": "Plaza de Oriente",
        "plaza_ramales": "Plaza de Ramales",
        "calle_vergara": "Calle de Vergara",
        "plaza_isabel_ii": "Plaza de Isabel II (Ópera)",
        "calle_arenal_1": "Calle del Arenal (Ópera)",
        "calle_bordadores": "Calle de Bordadores",
        "plazuela_san_gines": "Plazuela de San Ginés",
        "pasadizo_san_gines": "Pasadizo de San Ginés",
        "calle_arenal_2": "Calle del Arenal (Sol)",
        "museo_raton_perez": "Museo del Ratoncito Pérez",
        # Clásicos
        "plaza_mayor": "Plaza Mayor",
        "palacio_real": "Palacio Real",
        "puerta_del_sol": "Puerta del Sol",
        "mercado_san_miguel": "Mercado de San Miguel",
        "teatro_real": "Teatro Real",
    }
    return names.get(poi_id, poi_id.replace("_", " ").title())
