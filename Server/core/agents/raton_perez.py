"""
Ratoncito Pérez - Orquestador Principal 
"""

from typing import Dict, Any, Optional
from datetime import datetime
import sys
import os
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Imports locales
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import langchain_settings
from core.services.groq_service import groq_service

# Imports de módulos corregidos
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
    search_madrid_content
)
from Server.core.agents.location_helper import (
    check_poi_arrival,
    get_directions_osm,
    get_next_poi,
    find_nearest_poi,
    is_valid_location
)


class RatonPerez:
    """Orquestador principal del Ratoncito Pérez"""
    
    def __init__(self, db):
        self.settings = langchain_settings
        self.db = db
        logger.info("✅ Ratoncito Pérez inicializado")

    async def chat(self, family_id: int, message: str, 
                   location: Optional[Dict[str, float]] = None,
                   speaker_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Método principal de chat 
        """
        try:
            logger.info(f"🎭 Procesando chat - Familia: {family_id}, Mensaje: '{message[:50]}...'")
            
            # 1. Cargar contexto familiar
            family_context = await load_family_context(family_id, self.db)
            logger.info(f"👨‍👩‍👧‍👦 Contexto cargado - Puntos: {family_context.total_points}")
            
            # 2. Analizar situación 
            situation = await self._analyze_situation_final(message, location, family_context)
            logger.info(f"📋 Situación detectada: {situation['type']}, POI: {situation.get('current_poi_id', 'ninguno')}")
            
            # 3. Evaluar puntos 
            points_result = evaluate_points(family_context, message, situation)
            logger.info(f"🎯 Puntos evaluados: {points_result.get('points_earned', 0)}")
            
            # 4. Generar respuesta con contexto
            response = await self._generate_contextual_response(
                family_context, message, situation, points_result
            )
            
            # 5. Actualizar y guardar contexto
            await self._update_context_improved(
                family_context, message, response, speaker_name, 
                points_result, situation
            )
            
            # 6. Preparar respuesta final
            final_response = {
                "success": True,
                "response": response,
                "points_earned": points_result.get("points_earned", 0),
                "total_points": family_context.total_points,
                "situation": situation["type"],
                "achievements": points_result.get("achievements", [])
            }
            
            logger.info(f"✅ Chat procesado exitosamente - Total puntos: {family_context.total_points}")
            return final_response
            
        except Exception as e:
            logger.error(f"❌ Error en chat: {e}")
            return {
                "success": False,
                "response": "¡Ups! El Ratoncito Pérez se ha despistado un momento. ¿Puedes repetir? 🐭✨",
                "points_earned": 0,
                "total_points": 0,
                "situation": "error",
                "achievements": [],
                "error": str(e)
            }
    
    async def _analyze_situation_final(self, message: str, location: Optional[Dict], 
                                      context: FamilyContext) -> Dict[str, Any]:
        """
        Análisis de situación
        """
        message_lower = message.lower().strip()
        situation = {"type": "general_chat", "data": {}}
        
        # 1. VERIFICAR SI SUGIERE MOVIMIENTO/LLEGADA antes de check_poi_arrival
        movement_keywords = [
            "hemos llegado", "llegamos", "estamos en", "aquí estamos", "ya estamos",
            "hemos venido", "we arrived", "we're here", "here we are"
        ]
        
        suggests_arrival = any(keyword in message_lower for keyword in movement_keywords)
        
        # 2. SOLO verificar POI arrival si el mensaje sugiere llegada Y hay ubicación válida
        if suggests_arrival and location and is_valid_location(location):
            logger.info(f"🚶 Mensaje sugiere llegada: '{message_lower}'")
            # FIX CRÍTICO: AWAIT añadido aquí
            poi_check = await check_poi_arrival(location)
            
            if poi_check.get("arrived"):
                logger.info(f"🎯 LLEGADA CONFIRMADA: {poi_check['poi_name']}")
                situation = {
                    "type": "poi_arrival",
                    "data": {
                        "poi_id": poi_check["poi_id"],
                        "poi_name": poi_check["poi_name"],
                        "poi_index": poi_check.get("poi_index", 0),
                        "distance": poi_check.get("distance_meters", 0)
                    },
                    "current_poi_id": poi_check["poi_id"]
                }
                return situation
        
        # 3. Determinar POI actual para contexto 
        current_poi_id = self._determine_current_poi(location, context)
        if current_poi_id:
            situation["current_poi_id"] = current_poi_id
            logger.info(f"📍 POI actual para contexto: {current_poi_id}")
        
        # 4. PRIORIDAD: Tipo de interacción basado en contenido del mensaje
        
        # ¿Pregunta sobre ubicación/lugar?
        location_question_keywords = [
            "qué es", "cuéntame", "dime sobre", "historia de", "información",
            "what is", "tell me about", "history of"
        ]
        if any(keyword in message_lower for keyword in location_question_keywords):
            situation["type"] = "location_question"
            situation["data"] = {"query": message}
            logger.info("❓ Pregunta sobre ubicación detectada")
            return situation
        
        # ¿Pregunta de navegación?
        navigation_keywords = [
            "cómo llegar", "dónde está", "dirección", "siguiente lugar",
            "how to get", "where is", "directions", "next place"
        ]
        if any(keyword in message_lower for keyword in navigation_keywords):
            situation["type"] = "navigation"
            situation["data"] = {"location": location}
            logger.info("🧭 Pregunta de navegación detectada")
            return situation
        
        # ¿Solicitud de historia/cuento?
        story_keywords = [
            "historia", "cuento", "leyenda", "cuenta", "story", "tale", "legend"
        ]
        if any(keyword in message_lower for keyword in story_keywords):
            situation["type"] = "story_request"
            situation["data"] = {"topic": message}
            logger.info("📚 Solicitud de historia detectada")
            return situation
        
        # ¿Es respuesta a pregunta del agente?
        if self._is_response_to_agent_question(context, message):
            situation["type"] = "poi_question"
            situation["data"] = {"response": message}
            logger.info("💬 Respuesta a pregunta detectada")
            return situation
        
        # 5. DEFAULT: Chat general
        situation["type"] = "general_chat"
        situation["data"] = {"message": message}
        logger.info("💬 Chat general detectado")
        
        return situation
    
    def _determine_current_poi(self, location: Optional[Dict], context: FamilyContext) -> Optional[str]:
        """
        Determina el POI actual basado en ubicación o contexto
        """
        # Método 1: Por ubicación (prioritario)
        if location and is_valid_location(location):
            nearest = find_nearest_poi(location)
            if nearest and not nearest.get("error"):
                distance = nearest.get("distance_meters", float('inf'))
                # Si está cerca (dentro de 150m), consideramos que está en ese POI
                if distance <= 150:
                    logger.info(f"📍 POI por proximidad: {nearest['poi_id']} ({distance}m)")
                    return nearest["poi_id"]
        
        # Método 2: Por contexto - último POI visitado
        if context.visited_pois:
            last_poi = context.visited_pois[-1]
            logger.info(f"📍 POI por contexto: {last_poi.get('poi_id')}")
            return last_poi.get("poi_id")
        
        # Método 3: Por índice actual
        current_poi_id = context.get_current_poi_id()
        if current_poi_id:
            logger.info(f"📍 POI por índice: {current_poi_id}")
            return current_poi_id
        
        logger.info("📍 No se pudo determinar POI actual")
        return None
    
    def _is_response_to_agent_question(self, context: FamilyContext, message: str) -> bool:
        """
        Detecta si el mensaje es respuesta a una pregunta del agente
        """
        if len(message.strip()) < 3:
            return False
        
        # Verificar mensajes recientes del agente
        recent_messages = context.get_recent_messages(2)
        for exchange in recent_messages:
            agent_response = exchange.get("agent_response", "")
            # Si el agente hizo una pregunta reciente
            if "?" in agent_response and len(agent_response) > 20:
                # Y el usuario no está rechazando
                rejection_words = ["no sé", "paso", "siguiente", "no quiero"]
                if not any(word in message.lower() for word in rejection_words):
                    logger.info("💭 Detectada respuesta a pregunta del agente")
                    return True
        
        return False
    
    async def _generate_contextual_response(self, context: FamilyContext, message: str,
                                          situation: Dict[str, Any], 
                                          points_result: Dict[str, Any]) -> str:
        """
        Genera respuesta con contexto 
        """
        # Prompt base adaptado a la familia
        base_prompt = self._build_family_prompt(context)
        
        # Información adicional según situación
        situation_context = await self._build_situation_context(situation, context)
        
        # Información de celebración de puntos
        celebration_context = ""
        if points_result.get("points_earned", 0) > 0:
            celebration = get_celebration_message(points_result, context.language)
            if celebration:
                celebration_context = f"\n\nCELEBRACIÓN DE PUNTOS:\n{celebration}"
        
        # Contexto conversacional
        conversation_context = self._build_conversation_context(context)
        
        # Construir prompt final
        is_first_interaction = len(context.conversation_history) == 0
        
        if is_first_interaction:
            # Primera interacción - Presentación personalizada
            full_prompt = f"""{base_prompt}

SITUACIÓN: Primera vez que hablas con esta familia. Preséntate como el Ratoncito Pérez.

{situation_context}
{celebration_context}
{conversation_context}

Haz una presentación mágica y personalizada. Pregunta qué les interesa de Madrid."""
        else:
            # Conversación continuada
            full_prompt = f"""{base_prompt}

SITUACIÓN: Continúa la conversación como el Ratoncito Pérez (ya te conocen).
TIPO DE SITUACIÓN: {situation['type']}

{situation_context}
{celebration_context}
{conversation_context}

Responde de manera contextual y natural al mensaje."""
        
        # Generar con Groq
        try:
            # Preparar historial para LangChain
            conversation_history = []
            for msg in context.get_conversation_history():
                conversation_history.append({
                    "role": "user", 
                    "content": msg.get("user_message", "")
                })
                conversation_history.append({
                    "role": "assistant", 
                    "content": msg.get("agent_response", "")
                })
            
            messages = groq_service.create_messages(full_prompt, message, conversation_history)
            response = await groq_service.generate_response(messages)
            
            logger.info(f"🐭 Respuesta generada: {len(response)} caracteres")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error generando respuesta: {e}")
            return self._get_fallback_response(context, situation)
    
    def _build_family_prompt(self, context: FamilyContext) -> str:
        """
        Construye prompt personalizado por familia
        """
        base = f"""Eres el Ratoncito Pérez, guía mágico de Madrid. 

INFORMACIÓN FAMILIAR:
- Familia: {context.family_name}
- Adultos: {', '.join(context.adult_names) if context.adult_names else 'Ninguno'}
- Niños: {', '.join([f"{name} ({age} años)" for name, age in zip(context.child_names, context.child_ages)]) if context.child_names else 'Ninguno'}
- Idioma: {context.language}
- Puntos actuales: {context.total_points}"""
        
        # Adaptación por edad del niño más pequeño
        youngest_age = context.get_youngest_age()
        
        if youngest_age and youngest_age <= 7:
            age_prompt = f"""
ESTILO DE COMUNICACIÓN:
- Usa lenguaje muy simple para niños de {youngest_age} años
- Incluye elementos mágicos y emojis
- Haz que todo suene como una aventura
- Explica las cosas de forma muy básica"""
        
        elif youngest_age and youngest_age <= 12:
            age_prompt = f"""
ESTILO DE COMUNICACIÓN:
- Usa lenguaje apropiado para niños de {youngest_age}-{context.get_oldest_child_age() or youngest_age} años
- Incluye datos interesantes y mini-retos
- Balance entre diversión y educación"""
        
        elif youngest_age and youngest_age >= 13:
            age_prompt = f"""
ESTILO DE COMUNICACIÓN:
- Usa lenguaje para adolescentes
- Proporciona contexto histórico detallado
- Menos infantil, más conversacional"""
        
        else:  # Solo adultos
            age_prompt = f"""
ESTILO DE COMUNICACIÓN:
- Contenido para adultos con interés turístico
- Información cultural y histórica detallada
- Mantén el carácter mágico del Ratoncito Pérez"""
        
        return base + age_prompt
    
    async def _build_situation_context(self, situation: Dict[str, Any], context: FamilyContext) -> str:
        """
        Construye contexto específico de la situación 
        """
        situation_type = situation["type"]
        situation_context = ""
        
        if situation_type == "poi_arrival":
            poi_data = situation["data"]
            location_info = get_location_info(poi_data["poi_id"], "basic_info")
            situation_context = f"""
LLEGADA A POI:
- Ubicación: {poi_data['poi_name']}
- Es la primera vez que llegan aquí
- Celebra su llegada y comparte información básica

INFORMACIÓN DEL LUGAR:
{location_info}"""
        
        elif situation_type == "location_question":
            query = situation["data"]["query"]
            search_info = search_madrid_content(query)
            situation_context = f"""
PREGUNTA SOBRE UBICACIÓN:
- Consulta: {query}
- Proporciona información educativa e interesante

INFORMACIÓN DISPONIBLE:
{search_info}"""
        
        elif situation_type == "navigation":
            current_location = situation["data"].get("location")
            next_poi_info = get_next_poi(context.current_poi_index, current_location)
            if not next_poi_info.get("completed"):
                # FIX CRÍTICO: AWAIT añadido aquí
                directions = await get_directions_osm(current_location, context.current_poi_index)
                situation_context = f"""
NAVEGACIÓN SOLICITADA:
- Siguiente destino: {next_poi_info.get('poi_name', 'Siguiente POI')}
- Proporciona direcciones claras y motivadoras

DIRECCIONES:
{directions}"""
        
        elif situation_type == "story_request":
            current_poi_id = situation.get("current_poi_id")
            if current_poi_id:
                stories = get_location_info(current_poi_id, "stories")
                situation_context = f"""
HISTORIA SOLICITADA:
- Ubicación actual: {current_poi_id}
- Cuenta una historia mágica y apropiada para la edad

HISTORIAS DISPONIBLES:
{stories}"""
        
        return situation_context
    
    def _build_conversation_context(self, context: FamilyContext) -> str:
        """
        Construye contexto conversacional
        """
        if not context.conversation_history:
            return ""
        
        # Resumen de la conversación reciente
        recent = context.get_recent_messages(2)
        if not recent:
            return ""
        
        context_parts = ["CONTEXTO CONVERSACIONAL RECIENTE:"]
        
        for i, exchange in enumerate(recent, 1):
            user_msg = exchange.get("user_message", "")[:100]
            agent_msg = exchange.get("agent_response", "")[:100]
            speaker = exchange.get("speaker", "Familia")
            
            context_parts.append(f"{i}. {speaker}: {user_msg}")
            context_parts.append(f"   Tú respondiste: {agent_msg}...")
        
        # POIs visitados
        if context.visited_pois:
            visited_names = [poi.get("poi_name", "POI") for poi in context.visited_pois[-3:]]
            context_parts.append(f"POIs visitados recientemente: {', '.join(visited_names)}")
        
        return "\n".join(context_parts)
    
    def _get_fallback_response(self, context: FamilyContext, situation: Dict[str, Any]) -> str:
        """
        Respuesta de emergencia si falla el LLM
        """
        if situation["type"] == "poi_arrival":
            poi_name = situation["data"].get("poi_name", "este lugar")
            return f"¡Fantástico, {context.get_personalized_greeting()}! Habéis llegado a {poi_name}. ¡Qué emocionante! 🐭✨"
        
        elif situation["type"] == "navigation":
            return f"¡Por supuesto! Os ayudo a llegar al siguiente lugar mágico de Madrid. 🗺️✨"
        
        else:
            return f"¡Hola, {context.get_personalized_greeting()}! ¿En qué puedo ayudaros en vuestra aventura por Madrid? 🐭✨"
    
    async def _update_context_improved(self, context: FamilyContext, user_message: str,
                                     agent_response: str, speaker_name: Optional[str],
                                     points_result: Dict[str, Any], situation: Dict[str, Any]):
        """
        Actualiza contexto con lógica mejorada
        """
        # 1. Actualizar memoria conversacional
        context.add_conversation(user_message, agent_response, speaker_name)
        
        # 2. Actualizar puntos SOLO si se otorgaron
        points_earned = points_result.get("points_earned", 0)
        if points_earned > 0:
            context.total_points += points_earned
            logger.info(f"💰 Puntos actualizados: +{points_earned} = {context.total_points} total")
        
        # 3. Actualizar progreso de ruta si llegaron a POI
        if situation["type"] == "poi_arrival":
            poi_data = situation["data"]
            poi_id = poi_data.get("poi_id")
            poi_name = poi_data.get("poi_name")
            poi_index = poi_data.get("poi_index", 0)
            
            # Agregar POI como visitado
            context.add_visited_poi({
                "poi_id": poi_id,
                "poi_name": poi_name,
                "poi_index": poi_index,
                "points": points_earned
            })
            
            # Actualizar índice de POI actual
            context.current_poi_index = max(context.current_poi_index, poi_index + 1)
            logger.info(f"🗺️ Progreso actualizado: POI {poi_index} visitado, siguiente: {context.current_poi_index}")
        
        # 4. Guardar en BD
        try:
            await save_family_context(context, self.db)
            logger.info("💾 Contexto guardado en BD exitosamente")
        except Exception as e:
            logger.error(f"❌ Error guardando contexto: {e}")
            # No fallar por esto, continuar
    
    # Métodos auxiliares para endpoints
    async def get_family_progress(self, family_id: int) -> Dict[str, Any]:
        """Obtiene progreso detallado de una familia"""
        try:
            context = await load_family_context(family_id, self.db)
            return {
                "family_name": context.family_name,
                "total_points": context.total_points,
                "current_poi": context.current_poi_index,
                "visited_pois": len(context.visited_pois),
                "completion_percentage": (len(context.visited_pois) / 10) * 100,  # Actualizado a 10 POIs
                "recent_conversation": context.get_recent_messages(3)
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo progreso: {e}")
            return {"error": f"Error obteniendo progreso: {str(e)}"}
    
    async def suggest_next_destination(self, family_id: int) -> Dict[str, Any]:
        """Sugiere próximo destino con información completa"""
        try:
            context = await load_family_context(family_id, self.db)
            suggestion = get_next_poi(context.current_poi_index, context.current_location)
            return suggestion
        except Exception as e:
            logger.error(f"❌ Error sugiriendo destino: {e}")
            return {"error": f"Error sugiriendo destino: {str(e)}"}


# Instancia global
raton_perez = None

# Helper functions para endpoints
async def process_chat_message(family_id: int, message: str, 
                             location: Optional[Dict] = None,
                             speaker_name: Optional[str] = None,
                             db=None) -> Dict[str, Any]:
    """Procesa mensaje de chat - versión final corregida"""
    global raton_perez
    if not raton_perez:
        raton_perez = RatonPerez(db)
    return await raton_perez.chat(family_id, message, location, speaker_name)

async def get_family_status(family_id: int, db) -> Dict[str, Any]:
    """Obtiene estado familiar completo"""
    global raton_perez
    if not raton_perez:
        raton_perez = RatonPerez(db)
    return await raton_perez.get_family_progress(family_id)

async def get_next_destination(family_id: int, db) -> Dict[str, Any]:
    """Obtiene siguiente destino recomendado"""
    global raton_perez
    if not raton_perez:
        raton_perez = RatonPerez(db)
    return await raton_perez.suggest_next_destination(family_id)