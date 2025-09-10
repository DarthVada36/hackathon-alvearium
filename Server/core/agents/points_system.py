"""
Points System - Sistema de puntos y gamificación
Lógica clara: 100 llegada + 75 engagement + 100 pregunta = 275 max por POI
"""

from typing import Dict, Any, List
from Server.core.agents.family_context import FamilyContext
import logging

logger = logging.getLogger(__name__)

# Configuración de puntos 
POINTS_CONFIG = {
    "arrival": 100,      # Solo por llegar la primera vez a un POI
    "engagement": 50,    # Por mostrar interés en un POI
    "question": 75,      # Por responder pregunta en un POI 
    "general_chat": 25   # Chat inicial sin POI
}

REJECTION_KEYWORDS = {
    "es": ["no sé", "no lo sé", "paso", "siguiente", "no me interesa", "no quiero"],
    "en": ["don't know", "i don't know", "skip", "next", "not interested", "don't want"]
}


def evaluate_points(context: FamilyContext, message: str, situation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evalúa y otorga puntos según la situación 
    """
    result = {
        "points_earned": 0,
        "achievements": [],
        "messages": []
    }
    
    logger.info(f"🔍 Evaluando puntos - Situación: {situation['type']}, POI actual: {situation.get('current_poi_id')}")
    
    # 1. SOLO puntos por llegada si es poi_arrival
    if situation["type"] == "poi_arrival":
        arrival_points = _evaluate_arrival_points(context, situation)
        result["points_earned"] += arrival_points["points"]
        result["achievements"].extend(arrival_points["achievements"])
        result["messages"].extend(arrival_points["messages"])
        logger.info(f"✅ Puntos por llegada: {arrival_points['points']}")
        return result  # SOLO puntos de llegada, no más
    
    # 2. Puntos por engagement SOLO si estamos en un POI específico
    current_poi_id = situation.get("current_poi_id")
    if current_poi_id:
        engagement_points = _evaluate_engagement_points(context, message, current_poi_id)
        result["points_earned"] += engagement_points["points"]
        result["achievements"].extend(engagement_points["achievements"])
        result["messages"].extend(engagement_points["messages"])
        logger.info(f"✅ Puntos por engagement en {current_poi_id}: {engagement_points['points']}")
    
    # 3. Puntos por pregunta SOLO si es una situación de pregunta/respuesta
    if situation["type"] in ["location_question", "poi_question"] and current_poi_id:
        question_points = _evaluate_question_points(context, message, current_poi_id)
        result["points_earned"] += question_points["points"]
        result["achievements"].extend(question_points["achievements"])
        result["messages"].extend(question_points["messages"])
        logger.info(f"✅ Puntos por pregunta en {current_poi_id}: {question_points['points']}")
    
    # 4. Puntos mínimos por chat inicial (solo primera vez)
    elif situation["type"] == "general_chat" and not current_poi_id and len(context.conversation_history) == 0:
        initial_points = _evaluate_initial_chat(context, message)
        result["points_earned"] += initial_points["points"]
        result["achievements"].extend(initial_points["achievements"])
        result["messages"].extend(initial_points["messages"])
        logger.info(f"✅ Puntos por chat inicial: {initial_points['points']}")
    
    logger.info(f"📊 Total puntos otorgados: {result['points_earned']}")
    return result


def _evaluate_arrival_points(context: FamilyContext, situation: Dict[str, Any]) -> Dict[str, Any]:
    """Evalúa puntos por llegar a un POI - SOLO PRIMERA VEZ"""
    
    poi_id = situation["data"].get("poi_id", "")
    poi_name = situation["data"].get("poi_name", "")
    
    if not poi_id:
        logger.warning("⚠️ No POI ID en arrival")
        return {"points": 0, "achievements": [], "messages": []}
    
    # Verificar si ya ganaron puntos de llegada en este POI
    if context.has_earned_poi_points(poi_id, "arrival"):
        logger.info(f"ℹ️ Ya se otorgaron puntos de llegada en {poi_id}")
        return {"points": 0, "achievements": [], "messages": []}
    
    # Crear/obtener registro del POI
    poi_record = context.get_or_create_poi_record(poi_id, poi_name)
    
    # Marcar puntos de llegada como otorgados
    context.mark_poi_points_earned(poi_id, "arrival")
    
    points = POINTS_CONFIG["arrival"]
    achievements = ["location_visit"]
    messages = [_get_arrival_message(poi_name)]
    
    logger.info(f"🎯 Otorgados {points} puntos por llegar a {poi_name}")
    
    return {
        "points": points,
        "achievements": achievements,
        "messages": messages
    }


def _evaluate_engagement_points(context: FamilyContext, message: str, poi_id: str) -> Dict[str, Any]:
    """Evalúa puntos por engagement en POI - LÓGICA MEJORADA"""
    
    # Verificar si ya ganaron puntos de engagement en este POI
    if context.has_earned_poi_points(poi_id, "engagement"):
        logger.info(f"ℹ️ Ya se otorgaron puntos de engagement en {poi_id}")
        return {"points": 0, "achievements": [], "messages": []}
    
    message_lower = message.lower().strip()
    
    # Filtrar rechazos explícitos
    rejection_words = REJECTION_KEYWORDS.get(context.language, REJECTION_KEYWORDS["es"])
    is_rejection = any(word in message_lower for word in rejection_words)
    
    if is_rejection or len(message_lower) < 5:
        logger.info(f"ℹ️ Mensaje rechazado o muy corto: '{message_lower}'")
        return {"points": 0, "achievements": [], "messages": []}
    
    # Palabras que indican engagement genuino
    engagement_words = [
        "increíble", "fascinante", "interesante", "genial", "wow", "impresionante",
        "me gusta", "que bonito", "que bien", "amazing", "interesting", "cool"
    ]
    
    has_engagement = any(word in message_lower for word in engagement_words)
    message_length = len(message_lower.split())
    
    # Solo dar puntos si hay engagement real O mensaje largo (>8 palabras)
    if has_engagement or message_length > 8:
        # Marcar como otorgado
        context.mark_poi_points_earned(poi_id, "engagement")
        
        points = POINTS_CONFIG["engagement"]
        achievements = ["poi_engagement"]
        messages = [_get_engagement_message(poi_id)]
        
        logger.info(f"🎯 Otorgados {points} puntos por engagement en {poi_id}")
        
        return {
            "points": points,
            "achievements": achievements,
            "messages": messages
        }
    
    logger.info(f"ℹ️ No hay engagement suficiente: '{message_lower}'")
    return {"points": 0, "achievements": [], "messages": []}


def _evaluate_question_points(context: FamilyContext, message: str, poi_id: str) -> Dict[str, Any]:
    """Evalúa puntos por responder preguntas en POI"""
    
    # Verificar si ya ganaron puntos de pregunta en este POI
    if context.has_earned_poi_points(poi_id, "question"):
        logger.info(f"ℹ️ Ya se otorgaron puntos de pregunta en {poi_id}")
        return {"points": 0, "achievements": [], "messages": []}
    
    message_lower = message.lower().strip()
    
    # Filtrar rechazos
    rejection_words = REJECTION_KEYWORDS.get(context.language, REJECTION_KEYWORDS["es"])
    is_rejection = any(word in message_lower for word in rejection_words)
    
    if is_rejection or len(message_lower) < 3:
        return {"points": 0, "achievements": [], "messages": []}
    
    # Verificar que realmente hay una pregunta en el contexto reciente
    recent_agent_messages = [msg.get("agent_response", "") for msg in context.get_recent_messages(2)]
    has_question_context = any("?" in msg for msg in recent_agent_messages)
    
    if has_question_context:
        # Marcar como otorgado
        context.mark_poi_points_earned(poi_id, "question")
        
        points = POINTS_CONFIG["question"]
        achievements = ["poi_question_answered"]
        messages = [_get_question_message(poi_id)]
        
        logger.info(f"🎯 Otorgados {points} puntos por responder pregunta en {poi_id}")
        
        return {
            "points": points,
            "achievements": achievements,
            "messages": messages
        }
    
    return {"points": 0, "achievements": [], "messages": []}


def _evaluate_initial_chat(context: FamilyContext, message: str) -> Dict[str, Any]:
    """Evalúa puntos por chat inicial - SOLO PRIMERA VEZ"""
    
    message_lower = message.lower().strip()
    
    # Solo saludos básicos
    greetings = ["hola", "hello", "buenas", "hey", "saludos"]
    is_greeting = any(greeting in message_lower for greeting in greetings)
    
    if is_greeting and len(message_lower) > 3:
        points = POINTS_CONFIG["general_chat"]
        achievements = ["initial_contact"]
        messages = ["¡Bienvenidos a Madrid!"]
        
        logger.info(f"🎯 Otorgados {points} puntos por saludo inicial")
        
        return {
            "points": points,
            "achievements": achievements,
            "messages": messages
        }
    
    return {"points": 0, "achievements": [], "messages": []}


# Funciones de mensajes
def _get_arrival_message(poi_name: str) -> str:
    """Mensaje por llegar a POI"""
    messages = {
        "Plaza Mayor": "¡Fantástico! Habéis descubierto la Plaza Mayor, el corazón de Madrid.",
        "Mercado de San Miguel": "¡Increíble! El Mercado de San Miguel os espera con sus delicias.",
        "Palacio Real": "¡Magnífico! El Palacio Real se alza majestuoso ante vosotros.",
        "Teatro Real": "¡Espléndido! El Teatro Real resuena con historias mágicas.",
        "Puerta del Sol": "¡Extraordinario! Habéis llegado al kilómetro cero de España."
    }
    
    return messages.get(poi_name, f"¡Fantástico! Habéis descubierto {poi_name}.")


def _get_engagement_message(poi_id: str) -> str:
    """Mensaje por engagement"""
    return "¡Me encanta vuestra curiosidad sobre este lugar especial!"


def _get_question_message(poi_id: str) -> str:
    """Mensaje por responder pregunta"""
    return "¡Excelente participación! Conocéis bien este lugar."


def get_celebration_message(points_result: Dict[str, Any], language: str = "es") -> str:
    """Genera mensaje de celebración moderado"""
    
    points_earned = points_result.get("points_earned", 0)
    messages = points_result.get("messages", [])
    
    if points_earned == 0 and not messages:
        return ""
    
    celebration_parts = []
    
    # Mensajes específicos
    if messages:
        celebration_parts.extend(messages)
    
    # Puntos (solo si son significativos)
    if points_earned > 0:
        if language == "es":
            celebration_parts.append(f"✨ ¡+{points_earned} puntos mágicos! ✨")
        else:
            celebration_parts.append(f"✨ +{points_earned} magical points! ✨")
    
    return "\n".join(celebration_parts)


def check_milestone_achievement(context: FamilyContext) -> Dict[str, Any]:
    """Verifica hitos - MÁS CONSERVADOR"""
    
    total_points = context.total_points
    achievements = []
    messages = []
    
    # Hitos más realistas
    if total_points >= 500:
        achievements.append("madrid_expert")
        if context.language == "es":
            messages.append("¡Sois unos expertos de Madrid! ¡Más de 500 puntos!")
        else:
            messages.append("You're Madrid experts! Over 500 points!")
    
    elif total_points >= 250:
        achievements.append("madrid_explorer")
        if context.language == "es":
            messages.append("¡Grandes exploradores! ¡Habéis superado los 250 puntos!")
        else:
            messages.append("Great explorers! You've passed 250 points!")
    
    elif total_points >= 100:
        achievements.append("first_steps")
        if context.language == "es":
            messages.append("¡Buen comienzo! ¡Ya tenéis 100 puntos!")
        else:
            messages.append("Good start! You have 100 points!")
    
    return {
        "achievements": achievements,
        "messages": messages
    }