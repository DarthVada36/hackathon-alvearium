"""
Points System - Sistema de puntos y gamificación
275 puntos máximo por POI: 100 llegada + 75 engagement + 100 pregunta
"""

from typing import Dict, Any, List
from family_context import FamilyContext


# Configuración de puntos
POINTS_CONFIG = {
    "arrival": 100,      # Puntos por llegar a cualquier POI
    "engagement": 75,    # Puntos por engagement en cualquier POI
    "question": 100      # Puntos por responder pregunta en cualquier POI
}

REJECTION_KEYWORDS = {
    "es": ["no sé", "no lo sé", "paso", "siguiente", "no me interesa"],
    "en": ["don't know", "i don't know", "skip", "next", "not interested"]
}


def evaluate_points(context: FamilyContext, message: str, situation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evalúa y otorga puntos según la situación
    Máximo 275 puntos por POI: 100 + 75 + 100
    
    Returns:
        Dict con puntos ganados, achievements y mensajes
    """
    result = {
        "points_earned": 0,
        "achievements": [],
        "messages": []
    }
    
    # Puntos por llegada a POI
    if situation["type"] == "poi_arrival":
        poi_points = _evaluate_poi_arrival(context, situation["data"])
        result["points_earned"] += poi_points["points"]
        result["achievements"].extend(poi_points["achievements"])
        result["messages"].extend(poi_points["messages"])
    
    # Puntos por engagement en POI específico
    current_poi_id = situation.get("current_poi_id")
    if current_poi_id:
        engagement_points = _evaluate_poi_specific_engagement(context, message, current_poi_id)
        result["points_earned"] += engagement_points["points"]
        result["achievements"].extend(engagement_points["achievements"])
        result["messages"].extend(engagement_points["messages"])
        
        # Puntos por pregunta específica del POI
        question_points = _evaluate_poi_specific_question(context, message, current_poi_id, situation)
        result["points_earned"] += question_points["points"]
        result["achievements"].extend(question_points["achievements"])
        result["messages"].extend(question_points["messages"])
    else:
        # Solo en conversación inicial sin POI
        if situation["type"] == "general_chat" and len(context.conversation_history) == 0:
            engagement_points = _evaluate_general_engagement(context, message)
            result["points_earned"] += engagement_points["points"]
            result["achievements"].extend(engagement_points["achievements"])
            result["messages"].extend(engagement_points["messages"])
    
    return result


def _evaluate_poi_arrival(context: FamilyContext, poi_data: Dict[str, Any]) -> Dict[str, Any]:
    """Evalúa puntos por llegar a un POI - SOLO PRIMERA VEZ"""
    
    poi_id = poi_data.get("poi_id", "")
    poi_name = poi_data.get("poi_name", "")
    poi_index = poi_data.get("poi_index", 0)
    
    # Crear o obtener registro del POI ANTES de verificar puntos
    poi_record = context.get_or_create_poi_record(poi_id, poi_name, poi_index)
    
    # Verificar si ya ganaron puntos de llegada
    if poi_record["points_awarded"]["arrival"]:
        return {"points": 0, "achievements": [], "messages": []}
    
    # Marcar puntos de llegada como otorgados
    poi_record["points_awarded"]["arrival"] = True
    
    # Puntos fijos por llegada a cualquier POI
    poi_points = POINTS_CONFIG["arrival"]
    
    achievements = ["location_visit"]
    messages = [_get_poi_message(poi_id, context.language)]
    
    return {
        "points": poi_points,
        "achievements": achievements,
        "messages": messages
    }


def _evaluate_poi_specific_engagement(context: FamilyContext, message: str, poi_id: str) -> Dict[str, Any]:
    """Evalúa engagement específico en un POI - SOLO PRIMERA VEZ POR POI"""
    
    # Asegurar que el POI existe antes de verificar
    poi_record = context.get_or_create_poi_record(poi_id)
    
    # Verificar si ya ganaron puntos de engagement en este POI
    if poi_record["points_awarded"]["engagement"]:
        return {"points": 0, "achievements": [], "messages": []}
    
    message_lower = message.lower()
    language_key = "es" if context.language == "es" else "en"
    
    result = {"points": 0, "achievements": [], "messages": []}
    
    # Detectar rechazo directo
    rejection_words = REJECTION_KEYWORDS[language_key]
    is_rejection = any(word in message_lower for word in rejection_words)
    
    # CUALQUIER mensaje no vacío y no rechazo = engagement EN ESTE POI
    if len(message.strip()) > 2 and not is_rejection:
        result["points"] += POINTS_CONFIG["engagement"]
        result["achievements"].append("poi_engagement")
        result["messages"].append(_get_poi_engagement_message(poi_id, context.language))
        
        # Marcar como otorgado DIRECTAMENTE en el registro
        poi_record["points_awarded"]["engagement"] = True
    
    return result


def _evaluate_poi_specific_question(context: FamilyContext, message: str, poi_id: str, situation: Dict[str, Any]) -> Dict[str, Any]:
    """Evalúa respuesta a pregunta específica del POI - SOLO PRIMERA VEZ POR POI"""
    
    # Asegurar que el POI existe antes de verificar
    poi_record = context.get_or_create_poi_record(poi_id)
    
    # Verificar si ya ganaron puntos de pregunta en este POI
    if poi_record["points_awarded"]["question"]:
        return {"points": 0, "achievements": [], "messages": []}
    
    # Solo evaluar si es una situación de pregunta/respuesta
    if situation["type"] not in ["location_question", "story_request", "poi_question"]:
        return {"points": 0, "achievements": [], "messages": []}
    
    message_lower = message.lower()
    language_key = "es" if context.language == "es" else "en"
    
    # Detectar rechazo directo
    rejection_words = REJECTION_KEYWORDS[language_key]
    is_rejection = any(word in message_lower for word in rejection_words)
    
    result = {"points": 0, "achievements": [], "messages": []}
    
    # Si hay participación genuina (no rechazo) y hay "?" en el contexto
    if not is_rejection and len(message.strip()) > 2:
        # Verificar si es realmente una respuesta a pregunta del POI
        if "?" in message or _is_poi_question_context(context, poi_id):
            result["points"] += POINTS_CONFIG["question"]
            result["achievements"].append("poi_question_answered")
            result["messages"].append(_get_poi_question_message(poi_id, context.language))
            
            # Marcar como otorgado DIRECTAMENTE en el registro
            poi_record["points_awarded"]["question"] = True
    
    return result


def _evaluate_general_engagement(context: FamilyContext, message: str) -> Dict[str, Any]:
    """Evalúa engagement general para conversaciones iniciales sin POI"""
    
    message_lower = message.lower()
    language_key = "es" if context.language == "es" else "en"
    
    result = {"points": 0, "achievements": [], "messages": []}
    
    # Detectar rechazo directo
    rejection_words = REJECTION_KEYWORDS[language_key]
    is_rejection = any(word in message_lower for word in rejection_words)
    
    # Solo en primera interacción y si hay engagement
    if len(message.strip()) > 10 and not is_rejection:
        # Puntos mínimos por engagement inicial
        result["points"] += 25
        result["achievements"].append("initial_engagement")
        result["messages"].append(_get_initial_engagement_message(context.language))
    
    return result


def _is_poi_question_context(context: FamilyContext, poi_id: str) -> bool:
    """Verifica si el contexto reciente incluye una pregunta sobre este POI"""
    recent_messages = context.get_recent_messages(2)
    for exchange in recent_messages:
        agent_response = exchange.get("agent_response", "")
        if "?" in agent_response and poi_id in str(exchange):
            return True
    return False


def get_celebration_message(points_result: Dict[str, Any], language: str = "es") -> str:
    """Genera mensaje de celebración simplificado"""
    
    messages = points_result.get("messages", [])
    points_earned = points_result.get("points_earned", 0)
    
    if not messages and points_earned == 0:
        return ""
    
    # Combinar mensajes existentes
    celebration = " ".join(messages)
    
    # Añadir puntos ganados en esta interacción
    if points_earned > 0:
        if language == "es":
            celebration += f"\n\n✨ ¡Habéis ganado {points_earned} puntos mágicos! ✨"
        else:
            celebration += f"\n\n✨ You've earned {points_earned} magical points! ✨"
    
    return celebration


# Funciones de mensajes
def _get_poi_message(poi_id: str, language: str) -> str:
    """Mensaje específico por POI"""
    messages = {
        "plaza_mayor": {
            "es": "¡Fantástico! Habéis descubierto la Plaza Mayor, el corazón de Madrid.",
            "en": "Fantastic! You've discovered Plaza Mayor, the heart of Madrid."
        },
        "mercado_san_miguel": {
            "es": "¡Increíble! El Mercado de San Miguel guarda secretos deliciosos.",
            "en": "Incredible! San Miguel Market holds delicious secrets."
        },
        "palacio_real": {
            "es": "¡Magnífico! El Palacio Real es una joya arquitectónica.",
            "en": "Magnificent! The Royal Palace is an architectural jewel."
        },
        "teatro_real": {
            "es": "¡Espléndido! El Teatro Real resuena con historias mágicas.",
            "en": "Splendid! The Royal Theatre resonates with magical stories."
        },
        "puerta_del_sol": {
            "es": "¡Extraordinario! La Puerta del Sol es el kilómetro cero de España.",
            "en": "Extraordinary! Puerta del Sol is Spain's kilometer zero."
        }
    }
    
    default = {
        "es": "¡Fantástico! Habéis descubierto una ubicación especial.",
        "en": "Fantastic! You've discovered a special location."
    }
    
    return messages.get(poi_id, default)[language]


def _get_poi_engagement_message(poi_id: str, language: str) -> str:
    """Mensaje por engagement específico en POI"""
    if language == "es":
        return "¡Me encanta vuestra curiosidad sobre este lugar especial!"
    else:
        return "I love your curiosity about this special place!"


def _get_poi_question_message(poi_id: str, language: str) -> str:
    """Mensaje por responder pregunta específica del POI"""
    if language == "es":
        return "¡Excelente respuesta! Conocéis bien los secretos de este lugar."
    else:
        return "Excellent answer! You know the secrets of this place well."


def _get_initial_engagement_message(language: str) -> str:
    """Mensaje por engagement inicial sin POI"""
    if language == "es":
        return "¡Bienvenidos aventureros! Me alegra conoceros."
    else:
        return "Welcome adventurers! I'm happy to meet you."


def check_milestone_achievement(context: FamilyContext) -> Dict[str, Any]:
    """Verifica si han alcanzado algún hito especial"""
    
    total_points = context.total_points
    achievements = []
    messages = []
    
    # Hitos por puntos totales simplificados
    if total_points >= 1000:
        achievements.append("point_master")
        if context.language == "es":
            messages.append("¡Sois maestros de los puntos! ¡Más de 1000 puntos mágicos!")
        else:
            messages.append("You're point masters! Over 1000 magical points!")
    
    elif total_points >= 500:
        achievements.append("point_explorer")
        if context.language == "es":
            messages.append("¡Grandes exploradores! ¡Habéis superado los 500 puntos!")
        else:
            messages.append("Great explorers! You've passed 500 points!")
    
    return {
        "achievements": achievements,
        "messages": messages
    }