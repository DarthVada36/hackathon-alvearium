import logging
from typing import List, Dict, Any, Optional
import random
import re

logger = logging.getLogger(__name__)

class RatonPerezAgent:
    def __init__(self):
        self.context_length = 5  # Mantener solo las últimas 5 interacciones
        
        # Frases típicas del Ratoncito Pérez
        self.greetings = [
            "¡Hola, pequeño aventurero! 🐭",
            "¡Qué alegría verte por aquí! 🐭",
            "¡Buenos días, explorador! 🐭",
            "¡Hola! Soy el Ratoncito Pérez 🐭"
        ]
        
        self.encouragements = [
            "¡Qué emocionante!",
            "¡Muy bien!",
            "¡Excelente pregunta!",
            "¡Me encanta tu curiosidad!"
        ]
        
        self.madrid_facts = [
            "¿Sabías que Madrid tiene más de 40 museos?",
            "El Parque del Retiro tiene más de 15,000 árboles.",
            "La Puerta del Sol es el kilómetro 0 de España.",
            "El Palacio Real tiene 3,418 habitaciones."
        ]
    
    def generate_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generar una respuesta contextual del Ratoncito Pérez
        
        Args:
            message: Mensaje del usuario
            context: Contexto completo incluyendo familia, ubicación, etc.
            
        Returns:
            Dict con response, suggestions, location_actions y points_awarded
        """
        try:
            # Extraer información del contexto
            family_members = context.get('family_members', [])
            current_location = context.get('current_location')
            active_route = context.get('active_route')
            conversation_history = context.get('conversation_history', [])
            preferred_language = context.get('preferred_language', 'es')
            
            # Personalizar según miembros de la familia
            has_children = any(member.get('member_type') == 'child' for member in family_members)
            children_ages = [member.get('age', 0) for member in family_members if member.get('member_type') == 'child']
            
            # Analizar el mensaje del usuario
            message_lower = message.lower()
            
            # Generar respuesta base
            response = self._generate_contextual_response(
                message, message_lower, has_children, children_ages,
                active_route, current_location
            )
            
            # Generar sugerencias
            suggestions = self._generate_suggestions(
                message_lower, active_route, has_children
            )
            
            # Determinar acciones de ubicación
            location_actions = self._determine_location_actions(
                current_location, active_route, message_lower
            )
            
            # Calcular puntos a otorgar
            points_awarded = self._calculate_points(
                message_lower, active_route, current_location
            )
            
            return {
                "response": response,
                "suggestions": suggestions,
                "location_actions": location_actions,
                "points_awarded": points_awarded
            }
            
        except Exception as e:
            logger.error(f"Error generando respuesta del agente: {e}")
            return {
                "response": "¡Hola! Soy el Ratoncito Pérez. Estoy teniendo algunos problemitas técnicos ahora mismo. ¿Puedes intentarlo de nuevo en un momentito?",
                "suggestions": ["Intentar de nuevo", "Pedir ayuda"],
                "location_actions": None,
                "points_awarded": 0
            }
    
    def _generate_contextual_response(
        self, 
        message: str, 
        message_lower: str, 
        has_children: bool,
        children_ages: List[int],
        active_route: Optional[Dict],
        current_location: Optional[Dict]
    ) -> str:
        """Generar respuesta contextual basada en el mensaje y situación"""
        
        # Respuestas para saludos
        if any(greeting in message_lower for greeting in ['hola', 'buenos días', 'buenas tardes', 'hi', 'hello']):
            greeting = random.choice(self.greetings)
            if active_route:
                return f"{greeting} Veo que estás en la ruta '{active_route.get('route_name', 'aventura')}'. ¿Cómo va todo?"
            else:
                return f"{greeting} ¿Listo para una nueva aventura por Madrid?"
        
        # Preguntas sobre Madrid
        if any(word in message_lower for word in ['madrid', 'ciudad', 'historia', 'museo', 'parque']):
            fact = random.choice(self.madrid_facts)
            return f"¡Me encanta que preguntes sobre Madrid! {fact} ¿Te gustaría saber más sobre algún lugar en particular?"
        
        # Preguntas sobre el Ratoncito Pérez
        if any(word in message_lower for word in ['ratoncito pérez', 'ratón', 'diente', 'dientes']):
            return "¡Soy el Ratoncito Pérez! Pero aquí en Madrid no solo recojo dientes, también ayudo a las familias a descubrir los lugares más mágicos de la ciudad. ¿Sabías que tengo una casa en la Calle Arenal?"
        
        # Preguntas sobre ubicación/navegación
        if any(word in message_lower for word in ['dónde', 'cómo llegar', 'dirección', 'perdido']):
            if current_location and active_route:
                return "Veo tu ubicación actual. Te ayudo a seguir la ruta. ¿Necesitas direcciones específicas para llegar al próximo punto?"
            else:
                return "Para ayudarte mejor con direcciones, necesito que actives tu ubicación. ¿Puedes compartirla conmigo?"
        
        # Preguntas sobre puntos/juego
        if any(word in message_lower for word in ['puntos', 'juego', 'premio', 'recompensa']):
            if active_route:
                points = active_route.get('points_earned', 0)
                return f"¡Has ganado {points} puntos en esta aventura! Puedes ganar más visitando lugares especiales y completando desafíos. ¿Quieres intentar una actividad?"
            else:
                return "¡Los puntos son muy divertidos! Cuando inicies una ruta, podrás ganar puntos visitando lugares y completando actividades. ¿Comenzamos una aventura?"
        
        # Despedidas
        if any(word in message_lower for word in ['adiós', 'bye', 'hasta luego', 'nos vemos']):
            return "¡Hasta la próxima aventura! Recuerda que siempre puedes contar conmigo para explorar Madrid. ¡Que tengas un día mágico!"
        
        # Respuesta general amigable
        encouragement = random.choice(self.encouragements)
        base_responses = [
            "¡Qué interesante! Cuéntame más sobre lo que te gustaría hacer en Madrid.",
            "Madrid está lleno de sorpresas. ¿Te gustaría que te recomiende algunos lugares especiales?",
            "Como buen ratoncito explorador, conozco muchos rincones mágicos de Madrid. ¿Qué tipo de aventura buscas?"
        ]
        
        return f"{encouragement} {random.choice(base_responses)}"
    
    def _generate_suggestions(
        self, 
        message_lower: str, 
        active_route: Optional[Dict], 
        has_children: bool
    ) -> List[str]:
        """Generar sugerencias de seguimiento"""
        
        suggestions = []
        
        if active_route:
            suggestions.extend([
                "¿Cómo sigo la ruta?",
                "Mostrar puntos cercanos",
                "¿Cuántos puntos llevo?"
            ])
        else:
            suggestions.extend([
                "Comenzar una nueva ruta",
                "¿Qué puedo visitar en Madrid?",
                "Lugares para niños"
            ])
        
        # Sugerencias específicas según el mensaje
        if "museo" in message_lower:
            suggestions.append("Museos recomendados")
        elif "parque" in message_lower:
            suggestions.append("Parques para visitar")
        elif "comida" in message_lower or "comer" in message_lower:
            suggestions.append("Lugares para comer")
        
        if has_children:
            suggestions.append("Actividades para niños")
        
        return suggestions[:4]  # Limitar a 4 sugerencias
    
    def _determine_location_actions(
        self, 
        current_location: Optional[Dict], 
        active_route: Optional[Dict], 
        message_lower: str
    ) -> Optional[Dict[str, Any]]:
        """Determinar acciones relacionadas con la ubicación"""
        
        if not current_location:
            return None
        
        actions = {}
        
        # Si hay una ruta activa, verificar progreso
        if active_route:
            actions["check_proximity"] = True
            actions["route_guidance"] = True
        
        # Si pide direcciones
        if any(word in message_lower for word in ['cómo llegar', 'direcciones', 'navegar']):
            actions["provide_directions"] = True
        
        # Si menciona estar perdido
        if any(word in message_lower for word in ['perdido', 'no sé dónde', 'ayuda ubicación']):
            actions["emergency_help"] = True
            actions["nearby_landmarks"] = True
        
        return actions if actions else None
    
    def _calculate_points(
        self, 
        message_lower: str, 
        active_route: Optional[Dict], 
        current_location: Optional[Dict]
    ) -> int:
        """Calcular puntos a otorgar por la interacción"""
        
        points = 0
        
        # Puntos por primera interacción del día
        # (En implementación real, verificar con timestamp)
        if any(greeting in message_lower for greeting in ['hola', 'buenos días']):
            points += 5
        
        # Puntos por hacer preguntas educativas
        if any(word in message_lower for word in ['historia', 'museo', 'cultura', 'arte']):
            points += 10
        
        # Puntos por compartir ubicación
        if current_location and active_route:
            points += 3
        
        # Puntos por completar interacciones específicas
        if "ratoncito pérez" in message_lower:
            points += 8
        
        return points