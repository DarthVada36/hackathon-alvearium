"""
Evaluation Manager para el Ratoncito Pérez
Sistema dinámico de evaluación de logros basado en configuración de ruta
"""

from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from .context_manager import FamilyContext, RouteStage
from .prompts.base_prompts import Language


class AchievementType(Enum):
    """Tipos de logros"""
    LOCATION_VISIT = "location_visit"           # Visitar POI (GPS/índice)
    STORY_ENGAGEMENT = "story_engagement"       # Interactuar con historia
    QUESTION_PARTICIPATION = "question_participation"  # Participar en pregunta


@dataclass
class Achievement:
    """Definición dinámica de logro"""
    id: str
    type: AchievementType
    points: int
    message: Dict[Language, str]  # Mensaje de celebración por idioma


@dataclass
class EvaluationResult:
    """Resultado de evaluación"""
    achievement_earned: bool
    achievement_type: Optional[AchievementType] = None
    points_awarded: int = 0
    celebration_message: str = ""
    context: Dict[str, Any] = None


class EvaluationManager:
    """Sistema dinámico de evaluación basado en configuración de ruta"""
    
    def __init__(self, route_config: Optional[Dict[str, Any]] = None):
        self.route_config = route_config or {}
        self.poi_achievements = self._initialize_poi_achievements()
        self.interaction_patterns = self._initialize_interaction_patterns()
        
    def update_route_config(self, route_config: Dict[str, Any]):
        """Actualiza configuración de ruta y regenera achievements"""
        self.route_config = route_config
        self.poi_achievements = self._initialize_poi_achievements()
        
    def _initialize_poi_achievements(self) -> Dict[str, Achievement]:
        """Define logros basados en configuración dinámica de ruta"""
        achievements = {}
        
        # Obtener POIs desde configuración de ruta
        pois = self.route_config.get("pois", [])
        
        if not pois:
            # Fallback para desarrollo/testing
            pois = [
                {"id": "poi_1", "name": "Primer POI", "points": 150},
                {"id": "poi_2", "name": "Segundo POI", "points": 200},
                {"id": "poi_3", "name": "Tercer POI", "points": 120},
                {"id": "poi_4", "name": "Cuarto POI", "points": 100},
                {"id": "poi_5", "name": "Quinto POI", "points": 130}
            ]
        
        for poi in pois:
            poi_id = poi.get("id", f"poi_{len(achievements)}")
            poi_name = poi.get("name", "Ubicación misteriosa")
            poi_points = poi.get("points", 100)
            
            achievements[poi_id] = Achievement(
                id=f"{poi_id}_visit",
                type=AchievementType.LOCATION_VISIT,
                points=poi_points,
                message=self._generate_location_celebration_message(poi_name)
            )
        
        return achievements
    
    def _generate_location_celebration_message(self, location_name: str) -> Dict[Language, str]:
        """Genera mensaje de celebración dinámico para ubicación"""
        return {
            Language.SPANISH: f"¡Fantástico! Habéis descubierto {location_name}. ¡Qué aventureros sois!",
            Language.ENGLISH: f"Fantastic! You've discovered {location_name}. What adventurers you are!"
        }
    
    def _initialize_interaction_patterns(self) -> Dict[str, Dict]:
        """Patrones universales para detectar engagement"""
        return {
            "story_engagement": {
                "keywords_spanish": [
                    "interesante", "fascinante", "increíble", "guau", "wow", 
                    "cuéntame más", "qué pasó", "y luego", "me gusta",
                    "¿en serio?", "no sabía", "qué curioso", "impresionante"
                ],
                "keywords_english": [
                    "interesting", "fascinating", "incredible", "wow", "amazing",
                    "tell me more", "what happened", "and then", "i like",
                    "really?", "didn't know", "how curious", "impressive"
                ],
                "points": 75,
                "message": {
                    Language.SPANISH: "¡Me encanta vuestra curiosidad! Sois unos exploradores natos.",
                    Language.ENGLISH: "I love your curiosity! You're natural explorers."
                }
            },
            
            "question_participation": {
                "points": 100,
                "message": {
                    Language.SPANISH: "¡Excelente participación! Cada respuesta os acerca más a completar vuestra aventura.",
                    Language.ENGLISH: "Excellent participation! Each answer brings you closer to completing your adventure."
                }
            }
        }
    
    def evaluate_location_visit(self, context: FamilyContext, 
                              poi_id: Optional[str] = None,
                              poi_index: Optional[int] = None) -> EvaluationResult:
        """Evalúa visita a POI por ID o índice"""
        
        # Determinar POI ID
        if poi_id:
            target_poi_id = poi_id
        elif poi_index is not None:
            # Convertir índice a ID desde configuración
            pois = self.route_config.get("pois", [])
            if 0 <= poi_index < len(pois):
                target_poi_id = pois[poi_index].get("id", f"poi_{poi_index}")
            else:
                return EvaluationResult(achievement_earned=False)
        else:
            return EvaluationResult(achievement_earned=False)
        
        # Verificar si existe achievement para este POI
        if target_poi_id not in self.poi_achievements:
            return EvaluationResult(achievement_earned=False)
        
        # Verificar si ya visitaron este POI
        if self._already_visited_poi(context, target_poi_id):
            return EvaluationResult(achievement_earned=False)
        
        # Otorgar achievement
        achievement = self.poi_achievements[target_poi_id]
        celebration_msg = achievement.message[context.preferred_language]
        
        return EvaluationResult(
            achievement_earned=True,
            achievement_type=AchievementType.LOCATION_VISIT,
            points_awarded=achievement.points,
            celebration_message=celebration_msg,
            context={"poi_id": target_poi_id, "poi_index": poi_index}
        )
    
    def evaluate_story_engagement(self, context: FamilyContext, 
                                user_message: str) -> EvaluationResult:
        """Evalúa engagement con historias contadas"""
        
        patterns = self.interaction_patterns["story_engagement"]
        keywords = (patterns["keywords_spanish"] if context.preferred_language == Language.SPANISH 
                   else patterns["keywords_english"])
        
        # Detectar palabras clave de engagement
        message_lower = user_message.lower()
        engagement_detected = any(keyword in message_lower for keyword in keywords)
        
        # Detectar signos de interés (preguntas, exclamaciones)
        has_questions = "?" in user_message
        has_excitement = "!" in user_message or "¡" in user_message
        
        if engagement_detected or has_questions or has_excitement:
            celebration_msg = patterns["message"][context.preferred_language]
            return EvaluationResult(
                achievement_earned=True,
                achievement_type=AchievementType.STORY_ENGAGEMENT,
                points_awarded=patterns["points"],
                celebration_message=celebration_msg,
                context={"user_message": user_message, "engagement_type": "story_interest"}
            )
        
        return EvaluationResult(achievement_earned=False)
    
    def evaluate_question_participation(self, context: FamilyContext,
                                      user_message: str,
                                      agent_asked_question: bool = False) -> EvaluationResult:
        """Evalúa participación en preguntas del agente"""
        
        if not agent_asked_question:
            return EvaluationResult(achievement_earned=False)
        
        message_lower = user_message.lower()
        
        # Palabras de rechazo directo (universales)
        rejection_words_es = ["no sé", "no lo sé", "paso", "siguiente", "no me interesa"]
        rejection_words_en = ["don't know", "i don't know", "skip", "next", "not interested"]
        
        rejection_words = (rejection_words_es if context.preferred_language == Language.SPANISH 
                          else rejection_words_en)
        
        is_rejection = any(rejection in message_lower for rejection in rejection_words)
        
        # Si no es rechazo directo y tiene contenido, considerar participación
        if not is_rejection and len(user_message.strip()) > 2:
            patterns = self.interaction_patterns["question_participation"]
            celebration_msg = patterns["message"][context.preferred_language]
            
            return EvaluationResult(
                achievement_earned=True,
                achievement_type=AchievementType.QUESTION_PARTICIPATION,
                points_awarded=patterns["points"],
                celebration_message=celebration_msg,
                context={"user_message": user_message, "participation_type": "question_response"}
            )
        
        return EvaluationResult(achievement_earned=False)
    
    def comprehensive_evaluate(self, context: FamilyContext,
                             user_message: str,
                             current_poi_id: Optional[str] = None,
                             current_poi_index: Optional[int] = None,
                             agent_asked_question: bool = False,
                             agent_told_story: bool = False) -> List[EvaluationResult]:
        """Evaluación comprehensive de múltiples tipos de logros"""
        
        results = []
        
        # Evaluar visita a POI
        if current_poi_id or current_poi_index is not None:
            location_result = self.evaluate_location_visit(
                context, current_poi_id, current_poi_index
            )
            if location_result.achievement_earned:
                results.append(location_result)
        
        # Evaluar engagement con historia
        if agent_told_story:
            story_result = self.evaluate_story_engagement(context, user_message)
            if story_result.achievement_earned:
                results.append(story_result)
        
        # Evaluar participación en pregunta
        question_result = self.evaluate_question_participation(
            context, user_message, agent_asked_question
        )
        if question_result.achievement_earned:
            results.append(question_result)
        
        return results
    
    def _already_visited_poi(self, context: FamilyContext, poi_id: str) -> bool:
        """Verifica si ya visitaron este POI (evitar duplicados)"""
        for poi in context.visited_pois:
            if poi.get("poi_id") == poi_id:
                return True
        return False
    
    def calculate_total_points(self, evaluation_results: List[EvaluationResult]) -> int:
        """Calcula puntos totales de una lista de resultados"""
        return sum(result.points_awarded for result in evaluation_results if result.achievement_earned)
    
    def format_celebration_messages(self, results: List[EvaluationResult], 
                                  language: Language) -> str:
        """Formatea mensajes de celebración combinados"""
        if not results:
            return ""
        
        messages = [result.celebration_message for result in results if result.achievement_earned]
        total_points = self.calculate_total_points(results)
        
        if language == Language.SPANISH:
            combined = " ".join(messages)
            if total_points > 0:
                combined += f"\n\n¡Habéis ganado {total_points} puntos mágicos en total!"
        else:
            combined = " ".join(messages)  
            if total_points > 0:
                combined += f"\n\nYou've earned {total_points} magical points in total!"
        
        return combined
    
    def should_ask_question_about_poi(self, context: FamilyContext, 
                                    poi_id: str) -> bool:
        """Determina si debería hacer una pregunta sobre el POI actual"""
        return not self._already_asked_question_at_poi(context, poi_id)
    
    def _already_asked_question_at_poi(self, context: FamilyContext, poi_id: str) -> bool:
        """Verifica si ya hizo pregunta en este POI"""
        for exchange in context.conversation_memory:
            if ("?" in exchange.get("agent_response", "") and 
                poi_id in str(exchange.get("context", {}))):
                return True
        return False
    
    def get_poi_info(self, poi_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de un POI específico desde configuración"""
        pois = self.route_config.get("pois", [])
        for poi in pois:
            if poi.get("id") == poi_id:
                return poi
        return None
    
    def get_available_achievements(self) -> Dict[str, Achievement]:
        """Obtiene todos los achievements disponibles para la ruta actual"""
        return self.poi_achievements.copy()


# Factory function para crear evaluator con configuración
def create_evaluation_manager(route_config: Optional[Dict[str, Any]] = None) -> EvaluationManager:
    """Crea un EvaluationManager con configuración de ruta específica"""
    return EvaluationManager(route_config)