from fastapi import HTTPException, Depends
from functools import lru_cache
import logging
import os

logger = logging.getLogger(__name__)

def get_db():
    """
    Dependencia para obtener la conexión a la base de datos.
    
    Esta función debe retornar la instancia global de la base de datos
    que se inicializa en main.py durante el lifespan de la aplicación.
    """
    from main import db
    
    if db is None:
        logger.error("Base de datos no inicializada")
        raise HTTPException(
            status_code=500,
            detail="Error de conexión a la base de datos"
        )
    
    if not db.health_check():
        logger.error("Base de datos no disponible")
        raise HTTPException(
            status_code=503,
            detail="Base de datos no disponible"
        )
    
    return db

@lru_cache()
def get_settings():
    """
    Obtener configuración de la aplicación desde variables de entorno
    """
    return {
        "database_url": os.getenv("DATABASE_URL"),
        "groq_api_key": os.getenv("GROQ_API_KEY"),
        "debug": os.getenv("DEBUG", "False").lower() == "true",
        "max_conversation_history": int(os.getenv("MAX_CONVERSATION_HISTORY", "20")),
        "context_length": int(os.getenv("CONTEXT_LENGTH", "5")),
        "poi_proximity_threshold": float(os.getenv("POI_PROXIMITY_THRESHOLD", "50")),
        "base_points_per_interaction": int(os.getenv("BASE_POINTS_PER_INTERACTION", "5")),
        "education_question_bonus": int(os.getenv("EDUCATION_QUESTION_BONUS", "10")),
        "location_sharing_bonus": int(os.getenv("LOCATION_SHARING_BONUS", "3")),
        "completion_bonus": int(os.getenv("COMPLETION_BONUS", "50"))
    }

def get_raton_perez_agent():
    """
    Dependencia para obtener instancia del agente Ratoncito Pérez
    """
    from core.agents.raton_perez import RatonPerezAgent
    return RatonPerezAgent()

class CommonResponses:
    """Respuestas comunes para errores y situaciones típicas"""
    
    FAMILY_NOT_FOUND = "Familia no encontrada"
    ROUTE_NOT_FOUND = "Ruta no encontrada"
    NO_ACTIVE_ROUTE = "No hay una ruta activa para esta familia"
    DATABASE_ERROR = "Error de base de datos"
    AGENT_ERROR = "El Ratoncito Pérez tuvo un problemita técnico"
    
    @staticmethod
    def success_message(action: str) -> str:
        return f"{action} realizado correctamente"
    
    @staticmethod
    def points_awarded(points: int) -> str:
        return f"¡{points} puntos otorgados exitosamente!"