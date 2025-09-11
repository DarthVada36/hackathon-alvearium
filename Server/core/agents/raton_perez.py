"""
Ratoncito Pérez - Orquestador Principal
Integrado con búsquedas vectoriales y conocimiento dinámico de Madrid
Usa servicios de embeddings y Pinecone
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
from Server.core.agents.madrid_knowledge import (
    get_location_info,
    search_madrid_content,
    get_location_summary
)
from Server.core.agents.location_helper import RATON_PEREZ_ROUTE

# Importar servicios optimizados
from Server.core.services.embedding_service import embedding_service
from Server.core.services.pinecone_service import pinecone_service

class RatonPerez:
    """Orquestador principal del Ratoncito Pérez con búsquedas vectoriales optimizadas"""
    
    def __init__(self, db):
        self.settings = langchain_settings
        self.db = db
        
        # Verificar disponibilidad de servicios optimizados
        self._embedding_available = embedding_service and embedding_service.is_available()
        self._pinecone_available = pinecone_service and pinecone_service.is_available()
        
        if self._embedding_available:
            logger.info("✅ Servicio de embeddings optimizado disponible")
        else:
            logger.warning("⚠️ Servicio de embeddings no disponible - modo degradado")
            
        if self._pinecone_available:
            logger.info("✅ Servicio de Pinecone optimizado disponible")
        else:
            logger.warning("⚠️ Servicio de Pinecone no disponible - modo degradado")
        
        # NO inicializar base de conocimiento aquí - se hace en background en main.py
        logger.info("✅ Ratoncito Pérez inicializado (modo optimizado)")

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

            # Generar respuesta del agente usando búsquedas vectoriales optimizadas
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
        Detecta tipo de situación y determina si es una pregunta sobre lugares
        """
        current_poi_id = context.get_current_poi_id() or "plaza_oriente"

        # Verifica si el último mensaje del agente incluía una pregunta
        recent_msgs = context.get_recent_messages(1)
        if recent_msgs and "?" in recent_msgs[-1].get("agent_response", ""):
            return {
                "type": "poi_question",
                "current_poi_id": current_poi_id,
                "data": {"query": message}
            }

        # Detectar si es una pregunta sobre lugares (keywords típicas)
        location_keywords = [
            "dónde", "donde", "qué es", "que es", "cuéntame", "cuentame", 
            "historia", "arquitectura", "curiosidad", "interesante",
            "plaza", "calle", "museo", "palacio", "teatro", "mercado",
            "madrid", "lugar", "sitio", "edificio"
        ]
        
        is_location_question = any(keyword in message.lower() for keyword in location_keywords)
        
        if is_location_question:
            return {
                "type": "location_question",
                "current_poi_id": current_poi_id,
                "data": {"query": message}
            }

        # Por defecto → conversación general
        return {
            "type": "general_conversation",
            "current_poi_id": current_poi_id,
            "data": {"query": message}
        }

    async def _generate_contextual_response(self, context: FamilyContext, message: str,
                                            situation: Dict[str, Any],
                                            points_result: Dict[str, Any]) -> str:
        
        # Construir el prompt base
        base_prompt = self._build_family_prompt(context)
        
        # Preparar celebración de puntos
        celebration = ""
        if points_result.get("points_earned", 0) > 0:
            c = get_celebration_message(points_result, context.language)
            if c:
                celebration = f"\n\nCELEBRACIÓN DE PUNTOS:\n{c}"

        # Preparar contexto específico según situación (optimizado)
        situation_context = await self._build_situation_context(situation, message, context)

        # Prompt completo
        prompt = f"""{base_prompt}

SITUACIÓN ACTUAL:
{situation_context}
{celebration}

Responde como el Ratoncito Pérez, mágico y amigable, adaptado a la familia.
Usa la información proporcionada para dar respuestas educativas y entretenidas."""

        try:
            # Preparar historial de conversación
            conversation_history = []
            for msg in context.get_conversation_history():
                conversation_history.append({"role": "user", "content": msg.get("user_message", "")})
                conversation_history.append({"role": "assistant", "content": msg.get("agent_response", "")})

            # Generar respuesta
            messages = groq_service.create_messages(prompt, message, conversation_history)
            return await groq_service.generate_response(messages)
            
        except Exception as e:
            logger.error(f"❌ Error generando respuesta: {e}")
            return "¡Hola, exploradores! 🐭✨ Estoy aquí para contaros cosas maravillosas sobre Madrid."

    async def _build_situation_context(self, situation: Dict[str, Any], message: str, context: FamilyContext) -> str:
        """
        Construye el contexto específico según la situación detectada
        """
        situation_type = situation["type"]
        
        if situation_type == "poi_arrival":
            # Llegada a un POI
            poi = situation["data"]
            poi_id = poi["poi_id"]
            poi_name = poi["poi_name"]
            
            # Obtener información dinámica del POI 
            poi_info = ""
            if self._embedding_available and self._pinecone_available:
                try:
                    poi_info = get_location_info(poi_id, "basic_info")
                except Exception as e:
                    logger.warning(f"⚠️ Error obteniendo info de {poi_id}, usando fallback: {e}")
                    poi_info = f"Información sobre {poi_name} - un lugar especial en Madrid."
            else:
                poi_info = f"Información sobre {poi_name} - un lugar especial en Madrid."
            
            return f"""LLEGADA A: {poi_name}

INFORMACIÓN DEL LUGAR:
{poi_info}"""

        elif situation_type in ["location_question", "poi_question"]:
            # Pregunta sobre lugares
            query = situation["data"]["query"]
            current_poi_id = situation.get("current_poi_id")
            
            # Buscar información relevante usando búsquedas vectoriales optimizadas
            search_results = ""
            if self._embedding_available and self._pinecone_available:
                try:
                    search_results = search_madrid_content(query)
                except Exception as e:
                    logger.warning(f"⚠️ Error en búsqueda vectorial, usando fallback: {e}")
                    search_results = "Información general sobre Madrid disponible."
            else:
                search_results = "Madrid es una ciudad llena de historia y lugares fascinantes."
            
            # Información específica del POI actual si es relevante
            current_poi_info = ""
            if current_poi_id and self._embedding_available and self._pinecone_available:
                try:
                    poi_data = get_location_info(current_poi_id, 'basic_info')
                    current_poi_info = f"\nINFORMACIÓN DEL LUGAR ACTUAL:\n{poi_data}"
                except Exception as e:
                    logger.warning(f"⚠️ Error obteniendo info del POI actual: {e}")
            
            return f"""PREGUNTA SOBRE MADRID: {query}

INFORMACIÓN RELEVANTE:
{search_results}
{current_poi_info}"""

        elif situation_type == "general_conversation":
            # Conversación general
            current_poi_id = situation.get("current_poi_id")
            if current_poi_id and self._embedding_available and self._pinecone_available:
                try:
                    poi_summary = get_location_summary(current_poi_id)
                    return f"""CONVERSACIÓN GENERAL

CONTEXTO DEL LUGAR ACTUAL:
Estamos en: {poi_summary.get('name', 'un lugar especial')}
{poi_summary.get('basic_info', '')[:200]}...

PREGUNTA PARA MANTENER EL INTERÉS:
¿Hay algo especial de Madrid que os gustaría conocer?"""
                except Exception as e:
                    logger.warning(f"⚠️ Error obteniendo resumen del POI: {e}")
                    
            return """CONVERSACIÓN GENERAL

El Ratoncito Pérez está aquí para ayudar con cualquier pregunta sobre Madrid.

PREGUNTA PARA MANTENER EL INTERÉS:
¿Hay algo especial de Madrid que os gustaría conocer?"""

        else:
            return "El Ratoncito Pérez está aquí para ayudar con cualquier pregunta sobre Madrid."

    def _build_family_prompt(self, context: FamilyContext) -> str:
        """
        Construye el prompt base adaptado a la familia
        """
        family_info = []
        if context.family_name:
            family_info.append(f"Familia: {context.family_name}")
        if context.child_names:
            ages_info = [f"{name} ({age} años)" for name, age in zip(context.child_names, context.child_ages)]
            family_info.append(f"Niños: {', '.join(ages_info)}")
        if context.adult_names:
            family_info.append(f"Adultos: {', '.join(context.adult_names)}")
        
        family_context_str = "\n".join(family_info) if family_info else "Una familia aventurera"
        
        # Información sobre disponibilidad de servicios (para debugging)
        service_status = ""
        if not self._embedding_available or not self._pinecone_available:
            service_status = "\n[MODO DEGRADADO: Servicios de IA limitados]"
        
        return f"""Eres el Ratoncito Pérez, guía mágico y educativo de Madrid.

FAMILIA QUE VISITAS:
{family_context_str}
Puntos mágicos acumulados: {context.total_points}
POIs visitados: {len(context.visited_pois)}/10{service_status}

PERSONALIDAD:
- Mágico pero conciso
- Respuestas de 1-2 oraciones máximo
- Directo al grano pero amigable
- Una pregunta ocasional, no siempre

OBJETIVOS:
- Información útil y breve
- Mantener la magia sin rollo
- Puntos claros sobre Madrid
- Crear momentos memorables"""

    async def _update_context(self, context: FamilyContext, user_message: str, agent_response: str,
                              speaker_name: Optional[str], points_result: Dict[str, Any],
                              situation: Dict[str, Any]):
        """
        Actualiza el contexto familiar con la nueva interacción
        """
        # Agregar conversación
        context.add_conversation(user_message, agent_response, speaker_name)
        
        # Agregar puntos
        points = points_result.get("points_earned", 0)
        if points:
            context.total_points += points

        # Si es llegada a POI, actualizar progreso
        if situation["type"] == "poi_arrival":
            poi = situation["data"]
            context.add_visited_poi({
                "poi_id": poi["poi_id"],
                "poi_name": poi["poi_name"],
                "poi_index": poi["poi_index"],
                "points": points
            })
            context.current_poi_index = max(context.current_poi_index, poi["poi_index"] + 1)

        # Guardar contexto
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
    
    try:
        context = await load_family_context(family_id, db)
        return {
            "success": True,
            "family_name": context.family_name,
            "total_points": context.total_points,
            "current_poi_index": context.current_poi_index,
            "visited_pois": len(context.visited_pois),
            "total_pois": len(RATON_PEREZ_ROUTE),
            "progress_percentage": int((len(context.visited_pois) / len(RATON_PEREZ_ROUTE)) * 100)
        }
    except Exception as e:
        logger.error(f"Error obteniendo estado de familia {family_id}: {e}")
        return {"success": False, "error": str(e)}

async def get_next_destination(family_id: int, db) -> Dict[str, Any]:
    """Obtiene el siguiente destino según el índice actual usando RATON_PEREZ_ROUTE."""
    global raton_perez
    if not raton_perez:
        raton_perez = RatonPerez(db)
    
    try:
        context = await load_family_context(family_id, db)
        next_index = context.current_poi_index
        
        if next_index < len(RATON_PEREZ_ROUTE):
            next_poi = RATON_PEREZ_ROUTE[next_index]
            
            # Enriquecer con información dinámica si los servicios están disponibles
            dynamic_info = {}
            if raton_perez._embedding_available and raton_perez._pinecone_available:
                try:
                    dynamic_info = get_location_summary(next_poi["id"])
                except Exception as e:
                    logger.warning(f"⚠️ Error obteniendo info dinámica para {next_poi['id']}: {e}")
                    dynamic_info = {"basic_info": "Información no disponible temporalmente"}
            
            return {
                **next_poi,
                "dynamic_info": dynamic_info,
                "progress": f"{next_index + 1}/{len(RATON_PEREZ_ROUTE)}"
            }
        else:
            return {
                "completed": True, 
                "message": "¡Habéis completado toda la ruta del Ratoncito Pérez! 🎉",
                "total_points": context.total_points
            }
    except Exception as e:
        logger.error(f"Error obteniendo siguiente destino: {e}")
        return {"error": str(e)}