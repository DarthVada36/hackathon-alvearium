"""
Points System - Sistema de puntos y gamificación
Lógica clara: 100 llegada + 50 engagement + 75 pregunta = 225 máx. por POI
"""

from typing import Dict, Any
from Server.core.agents.family_context import FamilyContext
import logging

logger = logging.getLogger(__name__)

# Configuración de puntos
POINTS_CONFIG = {
    "arrival": 100,     # Por llegar la primera vez a un POI
    "engagement": 50,   # Por mostrar interés en un POI
    "question": 75      # Por responder una pregunta del agente
}

def evaluate_points(context: FamilyContext, message: str, situation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evalúa y otorga puntos según la situación detectada.
    """
    result = {"points_earned": 0, "achievements": [], "messages": []}

    logger.info(f"🔍 Evaluando puntos - Situación: {situation['type']}, POI actual: {situation.get('current_poi_id')}")

    # 1️⃣ Puntos por llegada
    if situation["type"] == "poi_arrival":
        return _evaluate_arrival_points(context, situation)

    current_poi_id = situation.get("current_poi_id")

    # 2️⃣ Engagement en el POI
    if current_poi_id and situation["type"] == "location_question":
        if not context.has_earned_poi_points(current_poi_id, "engagement"):
            context.mark_poi_points_earned(current_poi_id, "engagement")
            result["points_earned"] += POINTS_CONFIG["engagement"]
            result["achievements"].append("poi_engagement")
            result["messages"].append("¡Me encanta vuestra curiosidad sobre este lugar!")
            logger.info(f"🎯 Otorgados {POINTS_CONFIG['engagement']} puntos por engagement en {current_poi_id}")

    # 3️⃣ Responder pregunta del agente (cualquier respuesta vale)
    if current_poi_id and situation["type"] == "poi_question":
        if not context.has_earned_poi_points(current_poi_id, "question"):
            context.mark_poi_points_earned(current_poi_id, "question")
            result["points_earned"] += POINTS_CONFIG["question"]
            result["achievements"].append("poi_question_answered")
            result["messages"].append("¡Excelente respuesta! 🐭✨")
            logger.info(f"🎯 Otorgados {POINTS_CONFIG['question']} puntos por responder pregunta en {current_poi_id}")

    logger.info(f"📊 Total puntos otorgados: {result['points_earned']}")
    return result

def _evaluate_arrival_points(context: FamilyContext, situation: Dict[str, Any]) -> Dict[str, Any]:
    """Evalúa puntos por llegar a un POI (primera vez)."""
    poi_id = situation["data"].get("poi_id", "")
    poi_name = situation["data"].get("poi_name", "")

    if context.has_earned_poi_points(poi_id, "arrival"):
        logger.info(f"ℹ️ Ya se otorgaron puntos de llegada en {poi_id}")
        return {"points_earned": 0, "achievements": [], "messages": []}

    context.mark_poi_points_earned(poi_id, "arrival")

    return {
        "points_earned": POINTS_CONFIG["arrival"],
        "achievements": ["location_visit"],
        "messages": [f"¡Habéis llegado a {poi_name}! +{POINTS_CONFIG['arrival']} puntos mágicos 🐭✨"]
    }

def get_celebration_message(points_result: Dict[str, Any], language: str = "es") -> str:
    """Genera un mensaje de celebración."""
    points = points_result.get("points_earned", 0)
    messages = points_result.get("messages", [])

    if points == 0 and not messages:
        return ""

    parts = []
    if messages:
        parts.extend(messages)
    if points > 0:
        parts.append(f"✨ ¡+{points} puntos mágicos! ✨" if language == "es" else f"✨ +{points} magical points! ✨")

    return "\n".join(parts)
