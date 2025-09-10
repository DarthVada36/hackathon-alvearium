"""
Ratoncito Pérez - Orquestador Principal
"""

from typing import Dict, Any, Optional
import sys, os, logging

logger = logging.getLogger(__name__)

# Ajustar rutas de importación
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import langchain_settings
from core.services.groq_service import groq_service

from Server.core.agents.family_context import (
    FamilyContext,
    load_family_context,
    save_family_context
)
from Server.core.agents.points_system import (
    evaluate_points,
    get_celebration_message
)
from Server.core.agents.madrid_knowledge import get_location_info
from Server.core.agents.location_helper import RATON_PEREZ_ROUTE

class RatonPerez:
    """Orquestador principal del Ratoncito Pérez """
    
    def __init__(self, db):
        self.settings = langchain_settings
        self.db = db
        logger.info("✅ Ratoncito Pérez inicializado")

    async def chat(self, family_id: int, message: str,
                   location: Optional[Dict[str, float]] = None,
                   speaker_name: Optional[str] = None) -> Dict[str, Any]:
        try:
            family_context = await load_family_context(family_id, self.db)

            # Detectar situación
            situation = await self._analyze_situation(message, location, family_context)

            # Evaluar puntos según la situación detectada
            points_result = evaluate_points(family_context, message, situation)

            # Fallback para engagement básico
            if situation["type"] in ["location_question", "poi_question"] and points_result.get("points_earned", 0) == 0:
                points_result["points_earned"] = 5
                points_result.setdefault("achievements", []).append("Engagement con el lugar")

            # Generar respuesta del agente
            response = await self._generate_contextual_response(
                family_context, message, situation, points_result
            )

            # Actualizar contexto
            await self._update_context(family_context, message, response, speaker_name, points_result, situation)

            return {
                "success": True,
                "response": response,
                "points_earned": points_result.get("points_earned", 0),
                "total_points": family_context.total_points,
                "situation": situation["type"],
                "achievements": points_result.get("achievements", [])
            }
        except Exception as e:
            logger.error(f"❌ Error en chat: {e}")
            return {
                "success": False,
                "response": "¡Ups! El Ratoncito Pérez se ha despistado un momento. 🐭✨",
                "points_earned": 0,
                "total_points": 0,
                "situation": "error",
                "achievements": [],
                "error": str(e)
            }

    async def _analyze_situation(self, message: str, location: Optional[Dict], context: FamilyContext) -> Dict[str, Any]:
        """
        Detecta tipo de situación: llegada, engagement o respuesta a pregunta.
        """
        # Primera vez → llegada al primer POI
        if not context.visited_pois:
            return {
                "type": "poi_arrival",
                "data": {"poi_id": "plaza_oriente", "poi_name": "Plaza de Oriente", "poi_index": 0},
                "current_poi_id": "plaza_oriente"
            }

        current_poi_id = context.get_current_poi_id() or "plaza_oriente"

        # Verifica si el último mensaje del agente incluía una pregunta
        recent_msgs = context.get_recent_messages(1)
        if recent_msgs and "?" in recent_msgs[-1].get("agent_response", ""):
            return {
                "type": "poi_question",
                "current_poi_id": current_poi_id,
                "data": {"query": message}
            }

        # Por defecto → engagement normal
        return {
            "type": "location_question",
            "current_poi_id": current_poi_id,
            "data": {"query": message}
        }

    def _generate_poi_question(self, poi_id: str) -> str:
        curiosities = get_location_info(poi_id, "curiosities")
        fact = curiosities.split(".")[0] if curiosities else "¿Os ha gustado este lugar mágico?"
        return f"Por cierto, {fact}. ¿Qué os parece?"

    async def _generate_contextual_response(self, context: FamilyContext, message: str,
                                            situation: Dict[str, Any],
                                            points_result: Dict[str, Any]) -> str:
        base_prompt = self._build_family_prompt(context)
        celebration = ""
        if points_result.get("points_earned", 0) > 0:
            c = get_celebration_message(points_result, context.language)
            if c:
                celebration = f"\n\nCELEBRACIÓN DE PUNTOS:\n{c}"

        situation_context = ""
        if situation["type"] == "poi_arrival":
            poi = situation["data"]
            info = get_location_info(poi["poi_id"], "basic_info")
            question = self._generate_poi_question(poi["poi_id"])
            situation_context = f"LLEGADA A {poi['poi_name']}:\n{info}\n\n{question}"
        elif situation["type"] in ["location_question", "poi_question"]:
            poi_id = situation.get("current_poi_id", "plaza_oriente")
            info = get_location_info(poi_id, "basic_info")
            question = self._generate_poi_question(poi_id)
            situation_context = f"MÁS INFORMACIÓN DEL LUGAR:\n{info}\n\n{question}"

        prompt = f"""{base_prompt}

SITUACIÓN:
{situation_context}
{celebration}

Responde como el Ratoncito Pérez, mágico y amigable, adaptado a la familia."""

        try:
            conversation_history = []
            for msg in context.get_conversation_history():
                conversation_history.append({"role": "user", "content": msg.get("user_message", "")})
                conversation_history.append({"role": "assistant", "content": msg.get("agent_response", "")})

            messages = groq_service.create_messages(prompt, message, conversation_history)
            return await groq_service.generate_response(messages)
        except Exception as e:
            logger.error(f"❌ Error generando respuesta: {e}")
            return "¡Hola, exploradores! 🐭✨ Hablemos más de este lugar mágico."

    def _build_family_prompt(self, context: FamilyContext) -> str:
        return f"""Eres el Ratoncito Pérez, guía mágico de Madrid.
Familia: {context.family_name}, Puntos: {context.total_points}.
Habla con tono cercano, alegre y mágico."""

    async def _update_context(self, context: FamilyContext, user_message: str, agent_response: str,
                              speaker_name: Optional[str], points_result: Dict[str, Any],
                              situation: Dict[str, Any]):
        context.add_conversation(user_message, agent_response, speaker_name)
        points = points_result.get("points_earned", 0)
        if points:
            context.total_points += points

        if situation["type"] == "poi_arrival":
            poi = situation["data"]
            context.add_visited_poi({
                "poi_id": poi["poi_id"],
                "poi_name": poi["poi_name"],
                "poi_index": poi["poi_index"],
                "points": points
            })
            context.current_poi_index = max(context.current_poi_index, poi["poi_index"] + 1)

        await save_family_context(context, self.db)

# Instancia global
raton_perez = None

# Helper functions
async def process_chat_message(family_id: int, message: str,
                               location: Optional[Dict] = None,
                               speaker_name: Optional[str] = None,
                               db=None) -> Dict[str, Any]:
    global raton_perez
    if not raton_perez:
        raton_perez = RatonPerez(db)
    return await raton_perez.chat(family_id, message, location, speaker_name)

async def get_family_status(family_id: int, db) -> Dict[str, Any]:
    global raton_perez
    if not raton_perez:
        raton_perez = RatonPerez(db)
    return await raton_perez.chat(family_id, "status")

async def get_next_destination(family_id: int, db) -> Dict[str, Any]:
    """Obtiene el siguiente destino según el índice actual usando RATON_PEREZ_ROUTE."""
    global raton_perez
    if not raton_perez:
        raton_perez = RatonPerez(db)
    context = await load_family_context(family_id, db)
    next_index = context.current_poi_index
    if next_index < len(RATON_PEREZ_ROUTE):
        return RATON_PEREZ_ROUTE[next_index]
    return {"completed": True, "message": "¡Habéis completado la ruta!"}
