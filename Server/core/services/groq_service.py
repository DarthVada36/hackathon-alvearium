"""
Servicio Groq para el Ratoncito Pérez Digital
Wrapper para LangChain + Groq con configuración optimizada
"""

from typing import Optional, Dict, Any
try:
    from langchain_groq import ChatGroq  # type: ignore
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage  # type: ignore
    from langchain_core.language_models.chat_models import BaseChatModel  # type: ignore
except Exception:  # pragma: no cover - optional dependency in local tests
    ChatGroq = None  # type: ignore
    BaseChatModel = None  # type: ignore
    class HumanMessage:  # type: ignore
        def __init__(self, content: str):
            self.content = content
    class SystemMessage(HumanMessage):
        pass
    class AIMessage(HumanMessage):
        pass
import sys
import os

# Añadir el directorio raíz al path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import langchain_settings


class GroqService:
    """Servicio para gestionar la conexión con Groq LLM"""
    
    def __init__(self):
        self.settings = langchain_settings
        self._llm = None
        self._initialize_llm()
    
    def _initialize_llm(self) -> None:
        """Inicializa el modelo LLM de Groq"""
        try:
            if not self.settings or not self.settings.validate_groq_key() or ChatGroq is None:
                raise ValueError("API key de Groq no válida")
            
            self._llm = ChatGroq(
                groq_api_key=self.settings.groq_api_key,
                model_name=self.settings.agent_model,
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens,
                # Optimizaciones para conversaciones familiares
                top_p=0.9,
                streaming=False,  # Por ahora sin streaming
            )
            
            print(f"✅ GroqService inicializado - Modelo: {self.settings.agent_model}")
            
        except Exception as e:
            print(f"❌ Error inicializando Groq: {e}")
            self._llm = None
    
    @property
    def llm(self) -> object:
        """Getter para el modelo LLM"""
        if self._llm is None:
            raise RuntimeError("GroqService no está inicializado correctamente")
        return self._llm
    
    def is_available(self) -> bool:
        """Verifica si el servicio está disponible"""
        return self._llm is not None
    
    def create_messages(self, system_prompt: str, user_message: str, 
                       conversation_history: Optional[list] = None) -> list:
        """
        Crea la lista de mensajes para LangChain
        
        Args:
            system_prompt: Prompt del sistema (personalidad del Ratoncito)
            user_message: Mensaje del usuario/familia
            conversation_history: Historial previo de la conversación
        
        Returns:
            Lista de mensajes formateados para LangChain
        """
        messages = []
        
        # Sistema: Personalidad del Ratoncito Pérez
        messages.append(SystemMessage(content=system_prompt))
        
        # Historial de conversación (si existe)
        if conversation_history:
            for msg in conversation_history:
                if msg.get("role") == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg.get("role") == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
        
        # Mensaje actual del usuario
        messages.append(HumanMessage(content=user_message))
        
        return messages
    
    def create_family_context_messages(self, system_prompt: str, user_message: str,
                                      family_data: Dict[str, Any],
                                      conversation_history: Optional[list] = None) -> list:
        """
        Crea mensajes con contexto familiar específico
        
        Args:
            system_prompt: Prompt base del sistema
            user_message: Mensaje actual
            family_data: Datos de la familia (edades, preferencias, etc.)
            conversation_history: Historial previo
        
        Returns:
            Lista de mensajes con contexto familiar
        """
        # Enriquecer el system prompt con contexto familiar
        family_context = self._build_family_context(family_data)
        enhanced_system_prompt = f"{system_prompt}\n\n{family_context}"
        
        return self.create_messages(enhanced_system_prompt, user_message, conversation_history)
    
    def _build_family_context(self, family_data: Dict[str, Any]) -> str:
        """Construye contexto familiar para el prompt"""
        context_parts = []
        
        # Información de la familia
        if family_data.get("name"):
            context_parts.append(f"Familia: {family_data['name']}")
        
        # Miembros y edades
        if family_data.get("members"):
            adults = [m for m in family_data["members"] if m["member_type"] == "adult"]
            children = [m for m in family_data["members"] if m["member_type"] == "child"]
            
            if adults:
                adult_names = [a["name"] for a in adults]
                context_parts.append(f"Adultos: {', '.join(adult_names)}")
            
            if children:
                child_info = [f"{c['name']} ({c['age']} años)" for c in children]
                context_parts.append(f"Niños: {', '.join(child_info)}")
        
        # Idioma preferido
        if family_data.get("preferred_language", "es") != "es":
            context_parts.append(f"Idioma preferido: {family_data['preferred_language']}")
        
        # Progreso actual
        if family_data.get("current_poi_index") is not None:
            context_parts.append(f"Punto de interés actual: {family_data['current_poi_index']}")
        
        if family_data.get("points_earned"):
            context_parts.append(f"Puntos acumulados: {family_data['points_earned']}")
        
        return "CONTEXTO FAMILIAR:\n" + "\n".join(context_parts) if context_parts else ""
    
    async def generate_response(self, messages: list) -> str:
        """
        Genera respuesta usando Groq
        
        Args:
            messages: Lista de mensajes formateados
            
        Returns:
            Respuesta del Ratoncito Pérez
        """
        try:
            if not self.is_available():
                return "Lo siento, el Ratoncito Pérez está descansando. Intenta de nuevo en un momento 🐭"
            
            response = await self._llm.ainvoke(messages)
            return response.content.strip()
            
        except Exception as e:
            print(f"❌ Error generando respuesta: {e}")
            return "¡Ups! El Ratoncito Pérez se ha despistado un momento. ¿Puedes repetir tu pregunta? 🐭✨"
    
    def sync_generate_response(self, messages: list) -> str:
        """
        Versión síncrona de generate_response (para testing)
        """
        try:
            if not self.is_available():
                return "Lo siento, el Ratoncito Pérez está descansando. Intenta de nuevo en un momento 🐭"
            
            response = self._llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            print(f"❌ Error generando respuesta: {e}")
            return "¡Ups! El Ratoncito Pérez se ha despistado un momento. ¿Puedes repetir tu pregunta? 🐭✨"


# Instancia global del servicio
groq_service = GroqService()


# Función helper para uso rápido
def get_groq_llm() -> object:
    """Helper para obtener el LLM configurado"""
    return groq_service.llm


def quick_chat(user_message: str, system_prompt: str = "") -> str:
    """
    Helper para chat rápido (útil para testing)
    
    Args:
        user_message: Mensaje del usuario
        system_prompt: Prompt del sistema (opcional)
    
    Returns:
        Respuesta del modelo
    """
    if not system_prompt:
        system_prompt = "Eres el Ratoncito Pérez, un guía mágico y divertido de Madrid."
    
    messages = groq_service.create_messages(system_prompt, user_message)
    return groq_service.sync_generate_response(messages)