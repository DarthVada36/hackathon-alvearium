"""
Gamification Tool - Sistema de logros y puntos para el Ratoncito Pérez
Integración con EvaluationManager para gamificación inteligente
"""

from typing import Dict, Any, Optional, List
from langchain_core.tools import Tool
import json
import sys
import os

# Imports locales
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from ..evaluation_manager import EvaluationManager, AchievementType, EvaluationResult
from ..context_manager import FamilyContext
from ..prompts.base_prompts import Language


class GamificationToolError(Exception):
    """Errores específicos de la herramienta de gamificación"""
    pass


class GamificationTool:
    """Herramienta para gestionar logros, puntos y celebraciones"""
    
    def __init__(self, route_config: Optional[Dict[str, Any]] = None):
        self.evaluation_manager = EvaluationManager(route_config)
        
    def update_route_config(self, route_config: Dict[str, Any]):
        """Actualiza configuración de ruta en el evaluador"""
        self.evaluation_manager.update_route_config(route_config)
    
    def evaluate_poi_visit(self, context: FamilyContext, poi_id: str, 
                          poi_index: Optional[int] = None) -> Dict[str, Any]:
        """
        Evalúa y otorga puntos por visitar un POI
        
        Args:
            context: Contexto familiar actual
            poi_id: ID del POI visitado
            poi_index: Índice del POI (opcional)
            
        Returns:
            Resultado de la evaluación con puntos y mensaje
        """
        try:
            result = self.evaluation_manager.evaluate_location_visit(
                context, poi_id, poi_index
            )
            
            if result.achievement_earned:
                # Actualizar contexto familiar con la visita
                poi_info = self.evaluation_manager.get_poi_info(poi_id)
                context.add_visited_poi({
                    "poi_id": poi_id,
                    "index": poi_index,
                    "name": poi_info.get("name", poi_id) if poi_info else poi_id,
                    "points": result.points_awarded,
                    "activities": ["location_visit"]
                })
                
                return {
                    "success": True,
                    "points_earned": result.points_awarded,
                    "achievement_type": result.achievement_type.value,
                    "message": result.celebration_message,
                    "total_points": context.total_points + result.points_awarded
                }
            else:
                return {
                    "success": False,
                    "points_earned": 0,
                    "message": "Ya habéis visitado este lugar anteriormente."
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error evaluando visita a POI: {str(e)}"
            }
    
    def evaluate_conversation_engagement(self, context: FamilyContext, 
                                       user_message: str,
                                       agent_told_story: bool = False,
                                       agent_asked_question: bool = False) -> Dict[str, Any]:
        """
        Evalúa engagement en conversación para otorgar puntos
        
        Args:
            context: Contexto familiar
            user_message: Mensaje del usuario
            agent_told_story: Si el agente acaba de contar una historia
            agent_asked_question: Si el agente hizo una pregunta
            
        Returns:
            Resultado de evaluación de engagement
        """
        try:
            results = []
            total_points = 0
            messages = []
            
            # Evaluar engagement con historia
            if agent_told_story:
                story_result = self.evaluation_manager.evaluate_story_engagement(
                    context, user_message
                )
                if story_result.achievement_earned:
                    results.append(story_result)
                    total_points += story_result.points_awarded
                    messages.append(story_result.celebration_message)
            
            # Evaluar participación en pregunta
            if agent_asked_question:
                question_result = self.evaluation_manager.evaluate_question_participation(
                    context, user_message, agent_asked_question
                )
                if question_result.achievement_earned:
                    results.append(question_result)
                    total_points += question_result.points_awarded
                    messages.append(question_result.celebration_message)
            
            if total_points > 0:
                return {
                    "success": True,
                    "points_earned": total_points,
                    "achievements": [r.achievement_type.value for r in results],
                    "message": " ".join(messages),
                    "engagement_detected": True
                }
            else:
                return {
                    "success": False,
                    "points_earned": 0,
                    "engagement_detected": False
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error evaluando engagement: {str(e)}"
            }
    
    def comprehensive_evaluation(self, context: FamilyContext, user_message: str,
                               current_poi_id: Optional[str] = None,
                               current_poi_index: Optional[int] = None,
                               agent_told_story: bool = False,
                               agent_asked_question: bool = False) -> Dict[str, Any]:
        """
        Evaluación completa que considera todos los tipos de logros
        
        Args:
            context: Contexto familiar
            user_message: Mensaje del usuario
            current_poi_id: POI actual (si aplica)
            current_poi_index: Índice del POI actual
            agent_told_story: Si se contó una historia
            agent_asked_question: Si se hizo una pregunta
            
        Returns:
            Evaluación completa con todos los logros ganados
        """
        try:
            all_results = self.evaluation_manager.comprehensive_evaluate(
                context=context,
                user_message=user_message,
                current_poi_id=current_poi_id,
                current_poi_index=current_poi_index,
                agent_asked_question=agent_asked_question,
                agent_told_story=agent_told_story
            )
            
            if not all_results:
                return {
                    "success": False,
                    "points_earned": 0,
                    "achievements": [],
                    "message": ""
                }
            
            total_points = self.evaluation_manager.calculate_total_points(all_results)
            combined_message = self.evaluation_manager.format_celebration_messages(
                all_results, context.preferred_language
            )
            
            # Actualizar contexto si hay logros de ubicación
            for result in all_results:
                if (result.achievement_earned and 
                    result.achievement_type == AchievementType.LOCATION_VISIT):
                    
                    poi_context = result.context or {}
                    poi_id = poi_context.get("poi_id", current_poi_id)
                    poi_index = poi_context.get("poi_index", current_poi_index)
                    
                    if poi_id:
                        poi_info = self.evaluation_manager.get_poi_info(poi_id)
                        context.add_visited_poi({
                            "poi_id": poi_id,
                            "index": poi_index,
                            "name": poi_info.get("name", poi_id) if poi_info else poi_id,
                            "points": result.points_awarded,
                            "activities": ["location_visit"]
                        })
            
            return {
                "success": True,
                "points_earned": total_points,
                "achievements": [r.achievement_type.value for r in all_results if r.achievement_earned],
                "message": combined_message,
                "detailed_results": [
                    {
                        "type": r.achievement_type.value,
                        "points": r.points_awarded,
                        "message": r.celebration_message
                    } for r in all_results if r.achievement_earned
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error en evaluación comprehensive: {str(e)}"
            }
    
    def get_family_progress_summary(self, context: FamilyContext) -> Dict[str, Any]:
        """
        Obtiene resumen del progreso familiar
        
        Args:
            context: Contexto familiar
            
        Returns:
            Resumen completo del progreso
        """
        try:
            route_progress = context.get_route_progress_summary()
            available_achievements = self.evaluation_manager.get_available_achievements()
            
            return {
                "family_name": context.family_name,
                "total_points": context.total_points,
                "pois_visited": len(context.visited_pois),
                "current_poi_index": context.current_poi_index,
                "route_progress": route_progress,
                "available_achievements": len(available_achievements),
                "completion_percentage": route_progress.get("completion_percentage", 0),
                "time_elapsed": route_progress.get("duration", "No iniciado"),
                "recent_achievements": self._get_recent_achievements(context)
            }
            
        except Exception as e:
            return {"error": f"Error obteniendo progreso: {str(e)}"}
    
    def should_ask_question(self, context: FamilyContext, poi_id: str) -> Dict[str, Any]:
        """
        Determina si el agente debería hacer una pregunta en el POI actual
        
        Args:
            context: Contexto familiar
            poi_id: ID del POI actual
            
        Returns:
            Recomendación sobre hacer pregunta
        """
        should_ask = self.evaluation_manager.should_ask_question_about_poi(context, poi_id)
        
        return {
            "should_ask": should_ask,
            "poi_id": poi_id,
            "reason": "Nueva ubicación, buena para engagement" if should_ask else "Ya se hizo pregunta aquí"
        }
    
    def _get_recent_achievements(self, context: FamilyContext, limit: int = 3) -> List[Dict[str, Any]]:
        """Obtiene logros recientes de la memoria conversacional"""
        recent_achievements = []
        
        # Buscar en visited_pois los más recientes
        sorted_pois = sorted(
            context.visited_pois, 
            key=lambda x: x.get("visited_at", ""), 
            reverse=True
        )
        
        for poi in sorted_pois[:limit]:
            recent_achievements.append({
                "type": "location_visit",
                "name": poi.get("name", "Ubicación"),
                "points": poi.get("points_earned", 0),
                "timestamp": poi.get("visited_at")
            })
        
        return recent_achievements
    
    def format_achievement_celebration(self, results: List[EvaluationResult], 
                                     language: Language) -> str:
        """Formatea celebración de logros para el agente"""
        return self.evaluation_manager.format_celebration_messages(results, language)


# Crear instancia global
gamification_tool_instance = GamificationTool()

# Crear herramientas de LangChain
def create_gamification_tools() -> List[Tool]:
    """Crea herramientas de LangChain para gamificación"""
    
    tools = []
    
    # Herramienta para evaluar visita a POI
    tools.append(Tool(
        name="evaluate_poi_visit",
        description="Evalúa y otorga puntos por visitar un POI. Input: poi_id del lugar visitado",
        func=lambda poi_id: _handle_poi_visit_evaluation(poi_id)
    ))
    
    # Herramienta para evaluar engagement conversacional  
    tools.append(Tool(
        name="evaluate_engagement",
        description="Evalúa engagement en conversación para otorgar puntos. Input: user_message",
        func=lambda message: _handle_engagement_evaluation(message)
    ))
    
    # Herramienta para obtener progreso familiar
    tools.append(Tool(
        name="family_progress",
        description="Obtiene resumen del progreso y logros familiares. Input: family_id o vacío",
        func=lambda family_id="": _handle_progress_summary(family_id)
    ))
    
    return tools


# Helper functions para manejo de inputs
def _handle_poi_visit_evaluation(poi_id: str) -> Dict[str, Any]:
    """Maneja evaluación de visita a POI"""
    try:
        # En implementación real, obtendríamos contexto desde family_id
        # Por ahora retornamos estructura esperada
        return {
            "success": True,
            "points_earned": 150,
            "message": f"¡Fantástico! Habéis descubierto {poi_id}. ¡Qué aventureros sois!",
            "poi_id": poi_id
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def _handle_engagement_evaluation(message: str) -> Dict[str, Any]:
    """Maneja evaluación de engagement"""
    try:
        # Análisis básico de engagement
        engagement_indicators = ["interesante", "fascinante", "increíble", "?", "!"]
        has_engagement = any(indicator in message.lower() for indicator in engagement_indicators)
        
        if has_engagement:
            return {
                "success": True,
                "points_earned": 75,
                "message": "¡Me encanta vuestra curiosidad! Sois unos exploradores natos.",
                "engagement_detected": True
            }
        else:
            return {
                "success": False,
                "points_earned": 0,
                "engagement_detected": False
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

def _handle_progress_summary(family_id: str) -> Dict[str, Any]:
    """Maneja resumen de progreso familiar"""
    try:
        # En implementación real, consultaríamos BD con family_id
        return {
            "total_points": 425,
            "pois_visited": 2,
            "completion_percentage": 40,
            "recent_achievements": ["Plaza Mayor visitada", "Historia escuchada"]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Helper function para configuración de ruta
def update_gamification_route(route_config: Dict[str, Any]):
    """Actualiza configuración de ruta en la herramienta"""
    gamification_tool_instance.update_route_config(route_config)