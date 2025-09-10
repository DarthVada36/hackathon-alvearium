"""
Ratoncito Pérez - Orquestador Principal 
ACTUALIZADO para usar base de datos real
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

# Imports de módulos simplificados
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
    get_directions,
    get_next_poi
)


class RatonPerez:
    """Orquestador principal del Ratoncito Pérez - Versión con BD real"""
    
    def __init__(self, db):
        self.settings = langchain_settings
        self.db = db
        logger.info("✅ Ratoncito Pérez inicializado (con base de datos real)")
    
    async def chat(self, family_id: int, message: str, 
                   location: Optional[Dict[str, float]] = None,
                   speaker_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Método principal de chat con BD real
        """
        try:
            # 1. Cargar contexto familiar con BD
            family_context = await load_family_context(family_id, self.db)
            
            # 2. Analizar situación actual
            situation = self._analyze_situation(message, location, family_context)
            
            # 3. Evaluar puntos
            points_result = evaluate_points(family_context, message, situation)
            
            # 4. Generar respuesta
            response = await self._generate_response(family_context, message, situation, points_result)
            
            # 5. Actualizar contexto y guardar con BD
            await self._update_and_save_context(family_context, message, response, 
                                              speaker_name, points_result, situation)
            
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
                "response": "¡Ups! El Ratoncito Pérez se ha despistado. ¿Puedes repetir? 🐭✨",
                "error": str(e)
            }
    
    def _analyze_situation(self, message: str, location: Optional[Dict], 
                          context: FamilyContext) -> Dict[str, Any]:
        """Analiza qué tipo de situación tenemos"""
        
        message_lower = message.lower()
        situation = {"type": "general_chat", "data": {}}
        
        # ¿Llegaron a un POI?
        if location:
            poi_check = check_poi_arrival(location)
            if poi_check.get("arrived"):
                situation = {
                    "type": "poi_arrival",
                    "data": {
                        "poi_id": poi_check["poi_id"],
                        "poi_name": poi_check["poi_name"],
                        "poi_index": poi_check.get("poi_index", context.current_poi_index)
                    },
                    "current_poi_id": poi_check["poi_id"]  # NUEVO: Para vincular puntos
                }
        
        # Determinar POI actual para vincular engagement/preguntas
        current_poi_id = self._get_current_poi_id(location, context)
        if current_poi_id:
            situation["current_poi_id"] = current_poi_id
        
        # ¿Pregunta sobre ubicación?
        location_keywords = ["qué es", "cuéntame sobre", "historia", "what is", "tell me about"]
        if any(keyword in message_lower for keyword in location_keywords):
            situation["type"] = "location_question"
            situation["data"] = {"query": message}
        
        # ¿Pide direcciones?
        nav_keywords = ["dónde", "cómo llegar", "where", "how to get", "dirección"]
        if any(keyword in message_lower for keyword in nav_keywords):
            situation["type"] = "navigation"
            situation["data"] = {"location": location}
        
        # ¿Pide historia/cuento?
        story_keywords = ["historia", "cuento", "leyenda", "story", "tale"]
        if any(keyword in message_lower for keyword in story_keywords):
            situation["type"] = "story_request"
            situation["data"] = {"topic": message}
        
        # ¿Es respuesta a pregunta de POI?
        if self._is_poi_question_response(context, message):
            situation["type"] = "poi_question"
            situation["data"] = {"response": message}
        
        return situation
    
    def _get_current_poi_id(self, location: Optional[Dict], context: FamilyContext) -> Optional[str]:
        """Determina el POI actual basado en ubicación o contexto"""
        if location:
            poi_check = check_poi_arrival(location)
            # CORREGIDO: check_poi_arrival solo devuelve 'arrived', no 'nearby'
            if poi_check.get("arrived"):
                return poi_check.get("poi_id")
            
            # NUEVO: También verificar distancia para POIs cercanos (dentro de 100m)
            closest_poi = poi_check.get("closest_poi")
            distance = poi_check.get("distance_to_closest", float('inf'))
            if distance <= 100:  # Consideramos "estar en POI" si está a menos de 100m
                # Mapear nombre a ID
                poi_name_to_id = {
                    "Plaza Mayor": "plaza_mayor",
                    "Palacio Real": "palacio_real", 
                    "Mercado de San Miguel": "mercado_san_miguel",
                    "Teatro Real": "teatro_real",
                    "Puerta del Sol": "puerta_del_sol"
                }
                return poi_name_to_id.get(closest_poi)
        
        # Fallback: usar POI actual del contexto
        return context.get_current_poi_id()
    
    def _is_poi_question_response(self, context: FamilyContext, message: str) -> bool:
        """Detecta si el mensaje es respuesta a una pregunta del POI"""
        recent_messages = context.get_recent_messages(2)
        for exchange in recent_messages:
            agent_response = exchange.get("agent_response", "")
            if "?" in agent_response:
                # Verificar que no sea rechazo
                rejection_words = ["no sé", "no lo sé", "paso", "siguiente"]
                if not any(word in message.lower() for word in rejection_words):
                    return True
        return False
    
    async def _generate_response(self, context: FamilyContext, message: str,
                               situation: Dict[str, Any], points_result: Dict[str, Any]) -> str:
        """Genera respuesta usando Groq con prompt contextualizado"""
        
        # Prompt base personalizado por edad
        base_prompt = self._get_personality_prompt(context)
        
        # Información adicional según situación
        additional_info = ""
        
        if situation["type"] == "poi_arrival":
            poi_data = situation["data"]
            location_info = get_location_info(poi_data["poi_id"])
            additional_info = f"\n\nINFO UBICACIÓN ACTUAL:\n{location_info}"
            
            # Agregar pregunta específica del POI si es apropiado
            if self._should_ask_question_at_poi(context, poi_data["poi_id"]):
                poi_question = self._get_poi_question(poi_data["poi_id"], context.language)
                additional_info += f"\n\nPREGUNTA PARA HACERLES:\n{poi_question}"
        
        elif situation["type"] == "location_question":
            search_info = search_madrid_content(message)
            additional_info = f"\n\nINFORMACIÓN ENCONTRADA:\n{search_info}"
        
        elif situation["type"] == "navigation":
            directions = get_directions(context.current_location, context.current_poi_index)
            additional_info = f"\n\nDIRECCIONES:\n{directions}"
        
        elif situation["type"] == "story_request":
            stories = get_location_info(context.current_poi_index, info_type="stories")
            additional_info = f"\n\nHISTORIAS DISPONIBLES:\n{stories}"
        
        # Celebraciones de puntos
        celebration = ""
        if points_result.get("points_earned", 0) > 0:
            celebration = f"\n\n{get_celebration_message(points_result, context.language)}"
        
        # Contexto familiar
        family_info = context.get_context_summary()
        
        # PROMPT MEJORADO CON CONTEXTO CONVERSACIONAL
        is_first_interaction = len(context.conversation_history) == 0
        
        if is_first_interaction:
            # Primera interacción - Presentación
            full_prompt = f"""{base_prompt}

CONTEXTO FAMILIAR:
{family_info}

SITUACIÓN: Es la primera vez que hablas con esta familia. Preséntate como el Ratoncito Pérez.
{additional_info}
{celebration}

Saluda de manera mágica y pregunta cómo puedes ayudarles en su aventura por Madrid."""
        else:
            # Conversación continuada - Sin presentación
            full_prompt = f"""{base_prompt}

CONTEXTO FAMILIAR:
{family_info}

SITUACIÓN ACTUAL: {situation['type']}
CONTINÚA LA CONVERSACIÓN como el Ratoncito Pérez (ya te conocen, no te presentes de nuevo).
{additional_info}
{celebration}

Responde de manera natural y contextual al mensaje."""
        
        # Generar respuesta con historial conversacional
        try:
            conversation_history = context.get_conversation_history()
            messages = groq_service.create_messages(full_prompt, message, conversation_history)
            response = await groq_service.generate_response(messages)
            return response
        except Exception as e:
            print(f"Error generando respuesta con LLM: {e}")
            if is_first_interaction:
                return "¡Hola! Soy el Ratoncito Pérez y estoy aquí para ayudaros en vuestra aventura por Madrid. ¿Qué os gustaría saber? 🐭✨"
            else:
                return "¡Perfecto! ¿En qué más puedo ayudaros? 🐭✨"
    
    def _get_personality_prompt(self, context: FamilyContext) -> str:
        """Obtiene prompt de personalidad adaptado CON INFORMACIÓN FAMILIAR"""
        
        # Personalidad base
        if context.language == "en":
            base = f"""You are the Tooth Fairy (Ratoncito Pérez), a magical and charming guide of Madrid.
You help families discover the city in a fun, educational way.

FAMILY INFORMATION:
- Family name: {context.family_name}
- Adults: {', '.join(context.adult_names)} 
- Children: {', '.join([f"{name} ({age})" for name, age in zip(context.child_names, context.child_ages)])}
- Address them naturally by their names when appropriate."""
        else:
            base = f"""Eres el Ratoncito Pérez, un guía mágico y encantador de Madrid.
Ayudas a familias a descubrir la ciudad de manera divertida y educativa.

INFORMACIÓN FAMILIAR:
- Familia: {context.family_name}
- Adultos: {', '.join(context.adult_names)}
- Niños: {', '.join([f"{name} ({age} años)" for name, age in zip(context.child_names, context.child_ages)])}
- Dirígete a ellos por sus nombres cuando sea apropiado."""
        
        # Adaptación por edad usando la edad más joven
        youngest_age = context.get_youngest_age()
        
        if youngest_age and youngest_age <= 7:  # Niños pequeños
            if context.language == "en":
                age_adapt = f"""Use simple language perfect for {youngest_age}-year-olds, magical elements, and short explanations. 
Be very enthusiastic and use emojis. Make everything sound like an adventure.
Address the children by name: {', '.join(context.child_names)}."""
            else:
                age_adapt = f"""Usa lenguaje simple perfecto para niños de {youngest_age} años, elementos mágicos y explicaciones cortas.
Sé muy entusiasta y usa emojis. Haz que todo suene como una aventura.
Dirígete a los niños por su nombre: {', '.join(context.child_names)}."""
                
        elif youngest_age and youngest_age <= 12:  # Niños medianos
            if context.language == "en":
                age_adapt = f"""Adapt for ages {youngest_age} to {context.get_oldest_child_age()}. Provide interesting facts and mini-challenges.
Use engaging language appropriate for {', '.join(context.child_names)} and the adults."""
            else:
                age_adapt = f"""Adapta para edades de {youngest_age} a {context.get_oldest_child_age()} años. Proporciona datos interesantes y mini-retos.
Usa lenguaje atractivo apropiado para {', '.join(context.child_names)} y los adultos."""
                
        elif youngest_age and youngest_age >= 13:  # Adolescentes
            if context.language == "en":
                age_adapt = f"""Provide detailed historical context for teenagers like {', '.join(context.child_names)}.
Use a conversational tone, less childish language. Include interesting facts."""
            else:
                age_adapt = f"""Proporciona contexto histórico detallado para adolescentes como {', '.join(context.child_names)}.
Usa un tono conversacional, menos infantil. Incluye datos interesantes."""
        else:  # Solo adultos
            if context.language == "en":
                age_adapt = f"""Tailor content for adults {', '.join(context.adult_names)}. 
Provide detailed information while maintaining the magical character."""
            else:
                age_adapt = f"""Adapta el contenido para los adultos {', '.join(context.adult_names)}.
Proporciona información detallada manteniendo el carácter mágico."""
        
        return f"{base}\n\n{age_adapt}"
    
    async def _update_and_save_context(self, context: FamilyContext, user_message: str,
                                     agent_response: str, speaker_name: Optional[str],
                                     points_result: Dict[str, Any], situation: Dict[str, Any]):
        """Actualiza contexto y lo guarda en BD real"""
        
        # Actualizar memoria conversacional
        context.add_conversation(user_message, agent_response, speaker_name)
        
        # Actualizar puntos
        points_earned = points_result.get("points_earned", 0)
        if points_earned > 0:
            context.total_points += points_earned
        
        # Actualizar progreso si llegaron a POI
        if situation["type"] == "poi_arrival":
            poi_data = situation["data"]
            context.current_poi_index = max(context.current_poi_index, 
                                          poi_data.get("poi_index", 0) + 1)
        
        # Guardar en BD real
        await save_family_context(context, self.db)
    
    def _should_ask_question_at_poi(self, context: FamilyContext, poi_id: str) -> bool:
        """Determina si debe hacer una pregunta en este POI"""
        
        # No hacer pregunta si ya respondieron una en este POI
        if context.has_earned_poi_points(poi_id, "question"):
            return False
        
        # No hacer pregunta en la primera llegada (solo celebrar)
        poi_visits = [p for p in context.visited_pois if p.get("poi_id") == poi_id]
        if not poi_visits:
            return False  # Primera vez aquí
        
        # Hacer pregunta si han mostrado engagement previo en este POI
        if context.has_earned_poi_points(poi_id, "engagement"):
            return True
        
        # O si han visitado al menos 2 POIs (están comprometidos con la ruta)
        return len(context.visited_pois) >= 2
    
    def _get_poi_question(self, poi_id: str, language: str) -> str:
        """Obtiene pregunta específica para cada POI"""
        
        questions = {
            "plaza_mayor": {
                "es": "¿Sabéis cómo se llamaba esta plaza antes de ser Plaza Mayor?",
                "en": "Do you know what this square was called before it became Plaza Mayor?"
            },
            "palacio_real": {
                "es": "¿Adiviináis cuántas habitaciones tiene este enorme palacio?",
                "en": "Can you guess how many rooms this enormous palace has?"
            },
            "puerta_del_sol": {
                "es": "¿Sabéis qué símbolo especial hay en el suelo de esta plaza?",
                "en": "Do you know what special symbol is on the floor of this square?"
            },
            "mercado_san_miguel": {
                "es": "¿De qué material especial está hecho este mercado?",
                "en": "What special material is this market made of?"
            },
            "teatro_real": {
                "es": "¿Qué tipo de espectáculos mágicos se representan aquí?",
                "en": "What kind of magical shows are performed here?"
            }
        }
        
        poi_questions = questions.get(poi_id, {})
        return poi_questions.get(language, poi_questions.get("es", "¿Qué os parece este lugar tan especial?"))
    
    # Métodos auxiliares para endpoints
    
    async def get_family_progress(self, family_id: int) -> Dict[str, Any]:
        """Obtiene progreso de una familia"""
        try:
            context = await load_family_context(family_id)
            return {
                "family_name": context.family_name,
                "total_points": context.total_points,
                "current_poi": context.current_poi_index,
                "visited_pois": len(context.visited_pois),
                "completion_percentage": (len(context.visited_pois) / 5) * 100,
                "recent_conversation": context.get_recent_messages(3)
            }
        except Exception as e:
            return {"error": f"Error obteniendo progreso: {str(e)}"}
    
    async def suggest_next_destination(self, family_id: int) -> Dict[str, Any]:
        """Sugiere próximo destino"""
        try:
            context = await load_family_context(family_id)
            suggestion = get_next_poi(context.current_poi_index, context.current_location)
            return suggestion
        except Exception as e:
            return {"error": f"Error sugiriendo destino: {str(e)}"}


# Instancia global
raton_perez = None

# Helper functions para endpoints
async def process_chat_message(family_id: int, message: str, 
                             location: Optional[Dict] = None,
                             speaker_name: Optional[str] = None,
                             db=None) -> Dict[str, Any]:
    """Procesa mensaje de chat con BD"""
    global raton_perez
    if not raton_perez:
        raton_perez = RatonPerez(db)
    return await raton_perez.chat(family_id, message, location, speaker_name)

async def get_family_status(family_id: int, db) -> Dict[str, Any]:
    """Obtiene estado familiar con BD"""
    global raton_perez
    if not raton_perez:
        raton_perez = RatonPerez(db)
    return await raton_perez.get_family_progress(family_id)

async def get_next_destination(family_id: int, db) -> Dict[str, Any]:
    """Obtiene siguiente destino con BD"""
    global raton_perez
    if not raton_perez:
        raton_perez = RatonPerez(db)
    return await raton_perez.suggest_next_destination(family_id)