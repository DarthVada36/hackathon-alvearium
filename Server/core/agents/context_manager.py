"""
Context Manager para el Ratoncito Pérez
Gestión inteligente de contexto familiar y progreso en ruta
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json

from .prompts.base_prompts import Language, AgeGroup, prompt_template


class RouteStage(Enum):
    """Etapas de la ruta del Ratoncito Pérez"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    AT_POI = "at_poi"
    COMPLETED = "completed"
    PAUSED = "paused"


class InteractionType(Enum):
    """Tipos de interacción conversacional"""
    GREETING = "greeting"
    LOCATION_QUESTION = "location_question"
    STORY_REQUEST = "story_request"
    NAVIGATION_HELP = "navigation_help"
    FAMILY_CHAT = "family_chat"
    ACHIEVEMENT_CHECK = "achievement_check"


class FamilyContext:
    """Gestiona el contexto completo de una familia"""
    
    def __init__(self, family_data: Dict[str, Any]):
        self.family_id = family_data.get("id")
        self.family_name = family_data.get("name", "")
        self.preferred_language = Language(family_data.get("preferred_language", "es"))
        
        # Procesar miembros familiares
        self.adults = self._extract_adults(family_data.get("members", []))
        self.children = self._extract_children(family_data.get("members", []))
        
        # Contexto de ruta
        self.current_poi_index = family_data.get("current_poi_index", 0)
        self.total_points = family_data.get("points_earned", 0)
        self.route_stage = RouteStage(family_data.get("route_stage", "not_started"))
        
        # Ubicación y progreso
        self.current_location = family_data.get("current_location", {})
        self.visited_pois = family_data.get("visited_pois", [])
        self.route_started_at = family_data.get("started_at")
        
        # Contexto conversacional
        conversation_ctx = family_data.get("conversation_context", {})
        self.conversation_memory = conversation_ctx.get("memory", [])
        self.last_interaction_type = conversation_ctx.get("last_interaction")
        self.speaking_member = conversation_ctx.get("current_speaker")
        
        # Determinar grupo de edad predominante
        self.age_group = self._determine_age_group()
    
    def _extract_adults(self, members: List[Dict]) -> List[Dict]:
        """Extrae adultos de la lista de miembros"""
        return [m for m in members if m.get("member_type") == "adult"]
    
    def _extract_children(self, members: List[Dict]) -> List[Dict]:
        """Extrae niños de la lista de miembros"""
        return [m for m in members if m.get("member_type") == "child"]
    
    def _determine_age_group(self) -> AgeGroup:
        """Determina el grupo de edad para adaptación de contenido"""
        if not self.children:
            return AgeGroup.ADULTS
        
        children_ages = [child.get("age", 10) for child in self.children]
        return prompt_template.determine_age_group(children_ages)
    
    def get_contextual_prompt(self, base_prompt: str = "") -> str:
        """Genera prompt contextualizado con información familiar"""
        context_parts = []
        
        # Información básica de familia
        if self.family_name:
            context_parts.append(f"Familia: {self.family_name}")
        
        # Miembros adultos
        if self.adults:
            adult_names = [adult.get("name", "") for adult in self.adults if adult.get("name")]
            if adult_names:
                context_parts.append(f"Adultos: {', '.join(adult_names)}")
        
        # Miembros niños con edades
        if self.children:
            child_info = []
            for child in self.children:
                name = child.get("name", "")
                age = child.get("age")
                if name and age:
                    child_info.append(f"{name} ({age} años)")
                elif name:
                    child_info.append(name)
            
            if child_info:
                context_parts.append(f"Niños: {', '.join(child_info)}")
        
        # Progreso en ruta
        if self.route_stage != RouteStage.NOT_STARTED:
            context_parts.append(f"Etapa de ruta: {self.route_stage.value}")
            context_parts.append(f"POI actual: {self.current_poi_index}")
            
        if self.total_points > 0:
            context_parts.append(f"Puntos mágicos: {self.total_points}")
        
        # Ubicación actual
        if self.current_location:
            location_name = self.current_location.get("name", "ubicación actual")
            context_parts.append(f"Ubicación: {location_name}")
        
        # Idioma si no es español
        if self.preferred_language != Language.SPANISH:
            context_parts.append(f"Idioma: {self.preferred_language.value}")
        
        # Hablante actual
        if self.speaking_member:
            context_parts.append(f"Hablando: {self.speaking_member}")
        
        context_string = "\n".join(context_parts) if context_parts else "Primera interacción"
        
        # Combinar con prompt base si se proporciona
        if base_prompt:
            return f"{base_prompt}\n\nCONTEXTO FAMILIAR:\n{context_string}"
        
        return context_string
    
    def update_conversation_memory(self, user_message: str, agent_response: str, 
                                 speaker_name: Optional[str] = None, 
                                 interaction_type: Optional[InteractionType] = None):
        """Actualiza la memoria conversacional"""
        timestamp = datetime.now().isoformat()
        
        # Añadir nuevo intercambio
        new_exchange = {
            "timestamp": timestamp,
            "user_message": user_message,
            "agent_response": agent_response,
            "speaker": speaker_name or self.speaking_member,
            "interaction_type": interaction_type.value if interaction_type else None
        }
        
        self.conversation_memory.append(new_exchange)
        
        # Mantener solo los últimos 10 intercambios
        if len(self.conversation_memory) > 10:
            self.conversation_memory = self.conversation_memory[-10:]
        
        # Actualizar contexto
        self.last_interaction_type = interaction_type
        if speaker_name:
            self.speaking_member = speaker_name
    
    def get_conversation_history_for_llm(self, limit: int = 5) -> List[Dict]:
        """Obtiene historial formateado para LLM"""
        recent_memory = self.conversation_memory[-limit:] if self.conversation_memory else []
        
        formatted_history = []
        for exchange in recent_memory:
            formatted_history.append({
                "role": "user",
                "content": exchange["user_message"],
                "speaker": exchange.get("speaker")
            })
            formatted_history.append({
                "role": "assistant", 
                "content": exchange["agent_response"]
            })
        
        return formatted_history
    
    def update_route_progress(self, poi_index: Optional[int] = None, 
                            location: Optional[Dict] = None,
                            points_earned: Optional[int] = None,
                            stage: Optional[RouteStage] = None):
        """Actualiza el progreso en la ruta"""
        if poi_index is not None:
            self.current_poi_index = poi_index
            
        if location:
            self.current_location = location
            
        if points_earned is not None:
            self.total_points += points_earned
            
        if stage:
            self.route_stage = stage
    
    def add_visited_poi(self, poi_info: Dict[str, Any]):
        """Marca un POI como visitado"""
        poi_entry = {
            "poi_index": poi_info.get("index", self.current_poi_index),
            "name": poi_info.get("name", ""),
            "visited_at": datetime.now().isoformat(),
            "points_earned": poi_info.get("points", 0),
            "completed_activities": poi_info.get("activities", [])
        }
        
        self.visited_pois.append(poi_entry)
    
    def get_appropriate_member_address(self, member_name: Optional[str] = None) -> str:
        """Obtiene la forma apropiada de dirigirse a un miembro específico"""
        if not member_name:
            # Dirección general a la familia
            if self.children and self.adults:
                return "familia" if self.preferred_language == Language.SPANISH else "family"
            elif self.children:
                return "pequeños aventureros" if self.preferred_language == Language.SPANISH else "little adventurers"
            else:
                return "exploradores" if self.preferred_language == Language.SPANISH else "explorers"
        
        # Buscar miembro específico
        all_members = self.adults + self.children
        for member in all_members:
            if member.get("name", "").lower() == member_name.lower():
                return member.get("name", member_name)
        
        return member_name
    
    def is_child_speaking(self, speaker_name: str) -> bool:
        """Determina si quien habla es un niño"""
        for child in self.children:
            if child.get("name", "").lower() == speaker_name.lower():
                return True
        return False
    
    def get_child_age(self, child_name: str) -> Optional[int]:
        """Obtiene la edad de un niño específico"""
        for child in self.children:
            if child.get("name", "").lower() == child_name.lower():
                return child.get("age")
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el contexto a diccionario para persistencia"""
        return {
            "conversation_context": {
                "memory": self.conversation_memory,
                "last_interaction": self.last_interaction_type.value if self.last_interaction_type else None,
                "current_speaker": self.speaking_member,
                "age_group": self.age_group.value,
                "route_stage": self.route_stage.value,
                "visited_pois": self.visited_pois,
                "updated_at": datetime.now().isoformat()
            }
        }
    
    def should_suggest_next_poi(self) -> bool:
        """Determina si debería sugerir el siguiente POI"""
        return (
            self.route_stage == RouteStage.AT_POI and
            len(self.visited_pois) > self.current_poi_index
        )
    
    def get_route_progress_summary(self) -> Dict[str, Any]:
        """Obtiene resumen del progreso en la ruta"""
        return {
            "current_poi": self.current_poi_index,
            "total_visited": len(self.visited_pois),
            "total_points": self.total_points,
            "route_stage": self.route_stage.value,
            "duration": self._calculate_route_duration(),
            "completion_percentage": self._calculate_completion_percentage()
        }
    
    def _calculate_route_duration(self) -> Optional[str]:
        """Calcula duración de la ruta actual"""
        if not self.route_started_at:
            return None
        
        try:
            start_time = datetime.fromisoformat(self.route_started_at.replace('Z', '+00:00'))
            duration = datetime.now() - start_time
            
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except:
            return None
    
    def _calculate_completion_percentage(self) -> float:
        """Calcula porcentaje de completitud (asumiendo 5 POIs en ruta)"""
        total_pois = 5  # Número de POIs en la ruta del Ratoncito Pérez
        return min((len(self.visited_pois) / total_pois) * 100, 100)


class ContextManager:
    """Manager principal para contexto familiar"""
    
    def __init__(self):
        self._active_contexts: Dict[int, FamilyContext] = {}
    
    def create_or_update_context(self, family_data: Dict[str, Any]) -> FamilyContext:
        """Crea o actualiza contexto familiar"""
        family_id = family_data.get("id")
        if not family_id:
            raise ValueError("family_id es requerido para crear contexto")
        
        context = FamilyContext(family_data)
        self._active_contexts[family_id] = context
        return context
    
    def get_context(self, family_id: int) -> Optional[FamilyContext]:
        """Obtiene contexto existente"""
        return self._active_contexts.get(family_id)
    
    def remove_context(self, family_id: int):
        """Elimina contexto de memoria (cuando familia termina sesión)"""
        self._active_contexts.pop(family_id, None)
    
    def get_active_families_count(self) -> int:
        """Número de familias activas"""
        return len(self._active_contexts)


# Instancia global
context_manager = ContextManager()