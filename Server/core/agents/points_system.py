"""
Points System - Sistema de puntos y gamificación
Lógica: 100 puntos por llegada + 75 puntos por engagement (solo una vez por POI)
"""
from typing import Dict, Any
from Server.core.agents.family_context import FamilyContext

# Configuración de puntos
POINTS_CONFIG = {
    "arrival": 100,    # Por llegar la primera vez a un POI
    "engagement": 75   # Por mostrar interés en un POI (solo primera vez)
}

def evaluate_points(context: FamilyContext, message: str, situation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evalúa y otorga puntos según la situación detectada.
    """
    result = {"points_earned": 0, "achievements": [], "messages": []}
    
    # Puntos por llegada
    if situation["type"] == "poi_arrival":
        return evaluate_arrival_points(context, situation)
    
    current_poi_id = situation.get("current_poi_id")
    
    # Engagement en el POI (solo primera interacción real del usuario)
    if current_poi_id and situation["type"] in ["location_question", "poi_question", "general_conversation"]:
        if not context.has_earned_poi_points(current_poi_id, "engagement"):
            # Verificar que NO es un mensaje automático del sistema
            if not is_system_generated_message(message, situation):
                context.mark_poi_points_earned(current_poi_id, "engagement")
                result["points_earned"] += POINTS_CONFIG["engagement"]
                result["achievements"].append("poi_engagement")
    
    return result

def evaluate_arrival_points(context: FamilyContext, situation: Dict[str, Any]) -> Dict[str, Any]:
    """Evalúa puntos por llegar a un POI (primera vez)."""
    poi_id = situation["data"].get("poi_id", "")
    poi_name = situation["data"].get("poi_name", "")
    
    if context.has_earned_poi_points(poi_id, "arrival"):
        return {"points_earned": 0, "achievements": [], "messages": []}
    
    context.mark_poi_points_earned(poi_id, "arrival")
    return {
        "points_earned": POINTS_CONFIG["arrival"],
        "achievements": ["location_visit"],
        "messages": []
    }

def is_system_generated_message(message: str, situation: Dict[str, Any]) -> bool:
    """
    Detecta si un mensaje es generado automáticamente por el sistema
    y no debería otorgar puntos de engagement.
    """
    system_indicators = [
        "bienvenid", "hola familia", "me alegra", "comenzamos",
        "estamos en", "sistema", "automático"
    ]
    
    message_lower = message.lower()
    
    # Si el mensaje contiene indicadores de sistema
    for indicator in system_indicators:
        if indicator in message_lower:
            return True
    
    # Si el mensaje es muy corto y genérico
    if len(message.strip()) < 10 and any(word in message_lower for word in ["hola", "hi", "inicio"]):
        return True
    
    return False