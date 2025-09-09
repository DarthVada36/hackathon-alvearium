"""
Madrid Knowledge Tool - Integración con RAG/Pinecone
Herramienta para acceder a conocimiento histórico y cultural de Madrid
"""

from typing import Dict, Any, Optional, List
from langchain_core.tools import Tool
import sys
import os

# Imports para integración futura con Pinecone
# from pinecone_service import pinecone_service

# Añadir path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))


class MadridKnowledgeToolError(Exception):
    """Errores específicos de la herramienta de conocimiento"""
    pass


class MadridKnowledgeTool:
    """Herramienta para acceder a información histórica y cultural de Madrid"""
    
    def __init__(self, use_pinecone: bool = False):
        self.use_pinecone = use_pinecone
        self.mock_knowledge = self._initialize_mock_knowledge()
        # self.pinecone_client = pinecone_service if use_pinecone else None
        
    def _initialize_mock_knowledge(self) -> Dict[str, Dict[str, Any]]:
        """Base de conocimiento mock para desarrollo (será reemplazada por Pinecone)"""
        return {
            "plaza_mayor": {
                "basic_info": "La Plaza Mayor es una plaza porticada de planta rectangular, situada en el centro histórico de Madrid. Sus orígenes se remontan al siglo XV cuando en este lugar se encontraba la 'Plaza del Arrabal'.",
                "historical_details": "Construida durante el reinado de Felipe III (1598-1621), fue diseñada por Juan Gómez de Mora. Ha sufrido tres grandes incendios a lo largo de su historia (1631, 1672 y 1790).",
                "architecture": "Edificio uniforme de cuatro plantas, con 237 balcones que dan a la plaza y nueve puertas de acceso. El edificio más famoso es la Casa de la Panadería.",
                "cultural_significance": "Ha sido testigo de celebraciones, mercados, corridas de toros, ejecuciones públicas y proclamaciones reales.",
                "curiosities": "Bajo la plaza hay túneles que conectan con otros edificios históricos. La estatua ecuestre de Felipe III fue un regalo del Gran Duque de Florencia.",
                "current_use": "Hoy es un centro neurálgico de actividad turística, comercial y cultural, con cafeterías, restaurantes y tiendas de souvenirs."
            },
            
            "palacio_real": {
                "basic_info": "El Palacio Real de Madrid es la residencia oficial de la Familia Real Española, aunque actualmente solo se usa para ceremonias de Estado.",
                "historical_details": "Construido en el siglo XVIII sobre los restos del antiguo Alcázar de Madrid, que fue destruido por un incendio en 1734. Su construcción comenzó en 1738 bajo Felipe V.",
                "architecture": "Diseñado por Filippo Juvarra y posteriormente por Giovanni Battista Sacchetti. Es el palacio real más grande de Europa Occidental con más de 3,400 habitaciones.",
                "artistic_treasures": "Alberga obras de Velázquez, Goya, Rubens y Caravaggio. La Real Armería contiene una de las mejores colecciones de armas del mundo.",
                "curiosities": "Tiene más habitaciones que Buckingham Palace y Versalles. Solo se utilizan unas 50 habitaciones para ceremonias oficiales.",
                "gardens": "Los jardines de Sabatini y el Campo del Moro rodean el palacio, ofreciendo vistas espectaculares."
            },
            
            "puerta_del_sol": {
                "basic_info": "La Puerta del Sol es una plaza del centro de Madrid, conocida por ser el kilómetro cero de las carreteras radiales del país.",
                "historical_details": "Su nombre proviene de un sol que adornaba la entrada de un castillo que se encontraba en los extramuros medievales de la ciudad.",
                "landmarks": "Alberga el famoso reloj de la Casa de Correos, desde donde se retransmiten las campanadas de Año Nuevo para toda España.",
                "symbols": "La estatua del Oso y el Madroño es el símbolo de Madrid. También está la placa del kilómetro cero de España.",
                "cultural_significance": "Ha sido escenario de importantes acontecimientos históricos como la proclamación de la Segunda República en 1931.",
                "current_activity": "Es uno de los lugares más transitados de Madrid, punto de encuentro y centro comercial y turístico."
            },
            
            "mercado_san_miguel": {
                "basic_info": "El Mercado de San Miguel es un mercado gastronómico cubierto ubicado en el centro histórico de Madrid, junto a la Plaza Mayor.",
                "historical_details": "Construido en 1916, es el último mercado de abastos cubierto que se conserva en el centro de Madrid.",
                "architecture": "Estructura de hierro forjado y cristal, ejemplo de la arquitectura del hierro madrileña de principios del siglo XX.",
                "gastronomic_offer": "Ofrece productos gourmet, tapas tradicionales e innovadoras, vinos, conservas y dulces tradicionales.",
                "renovation": "Fue completamente renovado en 2009, manteniendo su estructura original pero modernizando su oferta gastronómica.",
                "cultural_role": "Se ha convertido en un referente gastronómico que combina tradición y modernidad."
            },
            
            "teatro_real": {
                "basic_info": "El Teatro Real de Madrid es el teatro de ópera de la capital española y uno de los más importantes de Europa.",
                "historical_details": "Inaugurado en 1850 por la reina Isabel II, se construyó sobre el solar del antiguo Teatro de los Caños del Peral.",
                "architecture": "Diseñado por Antonio López Aguado y posteriormente modificado por Custodio Moreno, combina elementos neoclásicos y románticos.",
                "artistic_programming": "Programación de ópera, ballet y conciertos sinfónicos de primer nivel internacional.",
                "renovations": "Ha sufrido varias renovaciones importantes, la más reciente en 1997, que lo dotó de la tecnología más avanzada.",
                "curiosities": "Su escenario es uno de los más grandes del mundo. Tiene capacidad para 1,746 espectadores distribuidos en seis plantas."
            }
        }
    
    def search_location_info(self, location: str, info_type: str = "basic_info") -> str:
        """
        Busca información específica sobre una ubicación
        
        Args:
            location: Nombre de la ubicación (ej: "plaza mayor")
            info_type: Tipo de información (basic_info, historical_details, etc.)
        
        Returns:
            Información encontrada o mensaje de no encontrado
        """
        try:
            # Normalizar nombre de ubicación
            location_key = self._normalize_location_name(location)
            
            if self.use_pinecone:
                return self._search_pinecone(location_key, info_type)
            else:
                return self._search_mock_knowledge(location_key, info_type)
                
        except Exception as e:
            return f"Error buscando información sobre {location}: {str(e)}"
    
    def search_historical_context(self, location: str, time_period: Optional[str] = None) -> str:
        """
        Busca contexto histórico específico de una ubicación
        
        Args:
            location: Nombre de la ubicación
            time_period: Período histórico específico (opcional)
        
        Returns:
            Contexto histórico detallado
        """
        try:
            location_key = self._normalize_location_name(location)
            
            if self.use_pinecone:
                # Búsqueda vectorial con contexto temporal
                query = f"historia {location} {time_period}" if time_period else f"historia {location}"
                return self._search_pinecone_contextual(query)
            else:
                return self._get_mock_historical_context(location_key, time_period)
                
        except Exception as e:
            return f"Error obteniendo contexto histórico de {location}: {str(e)}"
    
    def search_curiosities_and_legends(self, location: str) -> str:
        """
        Busca curiosidades y leyendas sobre una ubicación
        
        Args:
            location: Nombre de la ubicación
        
        Returns:
            Curiosidades y leyendas encontradas
        """
        try:
            location_key = self._normalize_location_name(location)
            
            if self.use_pinecone:
                query = f"curiosidades leyendas {location}"
                return self._search_pinecone_contextual(query)
            else:
                return self._get_mock_curiosities(location_key)
                
        except Exception as e:
            return f"Error buscando curiosidades de {location}: {str(e)}"
    
    def _normalize_location_name(self, location: str) -> str:
        """Normaliza nombres de ubicaciones para búsqueda"""
        location_mapping = {
            "plaza mayor": "plaza_mayor",
            "palacio real": "palacio_real",
            "palacio real de madrid": "palacio_real",
            "puerta del sol": "puerta_del_sol",
            "mercado san miguel": "mercado_san_miguel",
            "mercado de san miguel": "mercado_san_miguel", 
            "teatro real": "teatro_real"
        }
        
        location_lower = location.lower().strip()
        return location_mapping.get(location_lower, location_lower.replace(" ", "_"))
    
    def _search_mock_knowledge(self, location_key: str, info_type: str) -> str:
        """Búsqueda en conocimiento mock"""
        if location_key not in self.mock_knowledge:
            return f"No tengo información específica sobre '{location_key}' en mi base de conocimiento actual."
        
        location_data = self.mock_knowledge[location_key]
        
        if info_type in location_data:
            return location_data[info_type]
        
        # Si no encuentra el tipo específico, devolver información básica
        return location_data.get("basic_info", "Información no disponible.")
    
    def _get_mock_historical_context(self, location_key: str, time_period: Optional[str]) -> str:
        """Obtiene contexto histórico desde conocimiento mock"""
        if location_key not in self.mock_knowledge:
            return f"No tengo contexto histórico sobre '{location_key}'."
        
        location_data = self.mock_knowledge[location_key]
        historical_info = location_data.get("historical_details", "")
        
        if time_period:
            # Filtrar por período si se especifica
            if time_period.lower() in historical_info.lower():
                return historical_info
            else:
                return f"No tengo información específica sobre {location_key} en el período {time_period}."
        
        return historical_info
    
    def _get_mock_curiosities(self, location_key: str) -> str:
        """Obtiene curiosidades desde conocimiento mock"""
        if location_key not in self.mock_knowledge:
            return f"No tengo curiosidades sobre '{location_key}'."
        
        location_data = self.mock_knowledge[location_key]
        return location_data.get("curiosities", "No hay curiosidades registradas para este lugar.")
    
    # Métodos preparados para integración con Pinecone
    def _search_pinecone(self, location_key: str, info_type: str) -> str:
        """Búsqueda en Pinecone (implementar cuando esté disponible)"""
        # TODO: Implementar integración con Pinecone
        # query_vector = self._generate_query_embedding(f"{location_key} {info_type}")
        # results = self.pinecone_client.query(vector=query_vector, top_k=3)
        # return self._process_pinecone_results(results)
        
        return self._search_mock_knowledge(location_key, info_type)
    
    def _search_pinecone_contextual(self, query: str) -> str:
        """Búsqueda contextual en Pinecone"""
        # TODO: Implementar búsqueda semántica
        # query_vector = self._generate_query_embedding(query)
        # results = self.pinecone_client.query(vector=query_vector, top_k=5)
        # return self._process_contextual_results(results)
        
        # Fallback a mock por ahora
        return "Búsqueda contextual no disponible sin Pinecone."
    
    def get_available_locations(self) -> List[str]:
        """Obtiene lista de ubicaciones disponibles"""
        if self.use_pinecone:
            # TODO: Obtener desde metadata de Pinecone
            pass
        
        return list(self.mock_knowledge.keys())
    
    def is_location_available(self, location: str) -> bool:
        """Verifica si hay información disponible para una ubicación"""
        location_key = self._normalize_location_name(location)
        return location_key in self.mock_knowledge


# Crear instancia de la herramienta
madrid_knowledge_tool_instance = MadridKnowledgeTool(use_pinecone=False)

# Crear herramientas de LangChain
def create_madrid_knowledge_tools() -> List[Tool]:
    """Crea herramientas de LangChain para el agente"""
    
    tools = []
    
    # Herramienta principal de información
    tools.append(Tool(
        name="madrid_location_info",
        description="Obtiene información básica sobre ubicaciones de Madrid. Input: nombre del lugar",
        func=lambda location: madrid_knowledge_tool_instance.search_location_info(location, "basic_info")
    ))
    
    # Herramienta de contexto histórico
    tools.append(Tool(
        name="madrid_historical_context", 
        description="Obtiene contexto histórico detallado sobre lugares de Madrid. Input: nombre del lugar",
        func=lambda location: madrid_knowledge_tool_instance.search_historical_context(location)
    ))
    
    # Herramienta de curiosidades
    tools.append(Tool(
        name="madrid_curiosities",
        description="Obtiene curiosidades y leyendas sobre lugares de Madrid. Input: nombre del lugar", 
        func=lambda location: madrid_knowledge_tool_instance.search_curiosities_and_legends(location)
    ))
    
    return tools


# Helper function para uso directo
def search_madrid_info(location: str, info_type: str = "basic_info") -> str:
    """Helper function para búsqueda rápida"""
    return madrid_knowledge_tool_instance.search_location_info(location, info_type)