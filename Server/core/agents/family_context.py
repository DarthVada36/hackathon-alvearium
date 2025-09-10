"""
Family Context - Gestión simple del contexto familiar
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
import logging
import json

logger = logging.getLogger(__name__)

@dataclass
class FamilyMember:
    name: str
    age: int
    member_type: str  # "adult" o "child"


class FamilyContext:
    """Contexto familiar simplificado con información completa"""
    
    def __init__(self, family_data: Dict[str, Any]):
        # Básicos
        self.family_id = family_data.get("id")
        self.family_name = family_data.get("name", "")
        self.language = family_data.get("preferred_language", "es")
        
        # Miembros - procesado con más detalle
        self.members = self._process_members(family_data.get("members", []))
        self.adults = [m for m in self.members if m.member_type == "adult"]
        self.children = [m for m in self.members if m.member_type == "child"]
        
        # Listas de nombres para uso directo
        self.adult_names = [adult.name for adult in self.adults if adult.name]
        self.child_names = [child.name for child in self.children if child.name]
        self.child_ages = [child.age for child in self.children]
        self.all_names = self.adult_names + self.child_names
        
        # Progreso
        progress = family_data.get("route_progress", {})
        self.current_poi_index = progress.get("current_poi_index", 0)
        self.total_points = progress.get("points_earned", 0)
        self.current_location = progress.get("current_location", {})
        
        # POIs visitados
        self.visited_pois = family_data.get("visited_pois", [])
        
        # Conversación
        conv_data = family_data.get("conversation_context", {})
        self.conversation_history = conv_data.get("memory", [])
        self.current_speaker = conv_data.get("current_speaker")
    
    def _process_members(self, members_data: List[Dict]) -> List[FamilyMember]:
        """Procesa miembros familiares"""
        return [
            FamilyMember(
                name=m.get("name", ""),
                age=m.get("age", 0),
                member_type=m.get("member_type", "adult")
            )
            for m in members_data
        ]

    def has_young_children(self) -> bool:
        """¿Hay niños pequeños (3-7 años)?"""
        return any(child.age <= 7 for child in self.children)
    
    def has_teenagers(self) -> bool:
        """¿Hay adolescentes (13+ años)?"""
        return any(child.age >= 13 for child in self.children)
    
    def get_youngest_age(self) -> Optional[int]:
        """Edad del niño más pequeño"""
        if not self.child_ages:
            return None
        return min(self.child_ages)
    
    def get_oldest_child_age(self) -> Optional[int]:
        """Edad del niño mayor"""
        if not self.child_ages:
            return None
        return max(self.child_ages)
    
    def get_personalized_greeting(self) -> str:
        """Genera saludo personalizado con nombres"""
        if not self.all_names:
            return f"familia {self.family_name}" if self.family_name else "familia"
        
        if len(self.all_names) == 1:
            return self.all_names[0]
        elif len(self.all_names) == 2:
            return f"{self.all_names[0]} y {self.all_names[1]}"
        else:
            return f"{', '.join(self.all_names[:-1])} y {self.all_names[-1]}"
    
    def get_child_appropriate_address(self) -> str:
        """Forma de dirigirse apropiada según edades"""
        if not self.children:
            return "exploradores"
        
        youngest = self.get_youngest_age()
        if youngest and youngest <= 7:
            return "pequeños aventureros"
        elif youngest and youngest <= 12:
            return "jóvenes exploradores"
        else:
            return "aventureros"
    
    def add_conversation(self, user_message: str, agent_response: str, 
                        speaker_name: Optional[str] = None):
        """Añade intercambio conversacional"""
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "agent_response": agent_response,
            "speaker": speaker_name
        }
        
        self.conversation_history.append(exchange)
        
        # Mantener solo últimos 10
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        if speaker_name:
            self.current_speaker = speaker_name
    
    def add_visited_poi(self, poi_data: Dict[str, Any]):
        """Marca POI como visitado con campos de seguimiento de puntuaciones"""
        visit_record = {
            "poi_id": poi_data.get("poi_id"),
            "poi_name": poi_data.get("poi_name", "Ubicación"),
            "poi_index": poi_data.get("poi_index", self.current_poi_index),
            "visited_at": datetime.now().isoformat(),
            "points_earned": poi_data.get("points", 0),
            # NUEVA ESTRUCTURA: tracking granular de puntos por tipo
            "points_awarded": {
                "arrival": True,  # Se marca True al crear el registro
                "engagement": False,
                "question": False
            }
        }
        
        # Evitar duplicados
        if not any(p.get("poi_id") == poi_data.get("poi_id") for p in self.visited_pois):
            self.visited_pois.append(visit_record)
    
    def has_earned_poi_points(self, poi_id: str, point_type: str) -> bool:
        """Verifica si ya se otorgaron puntos específicos en un POI"""
        for poi in self.visited_pois:
            if poi.get("poi_id") == poi_id:
                points_awarded = poi.get("points_awarded", {})
                return points_awarded.get(point_type, False)
        return False
    
    def get_or_create_poi_record(self, poi_id: str, poi_name: str = "", poi_index: int = 0) -> Dict[str, Any]:
        """Obtiene o crea un registro de POI si no existe"""
        # Buscar POI existente
        for poi in self.visited_pois:
            if poi.get("poi_id") == poi_id:
                return poi
        
        # Crear nuevo registro si no existe
        new_poi_record = {
            "poi_id": poi_id,
            "poi_name": poi_name or f"POI {poi_id}",
            "poi_index": poi_index,
            "visited_at": datetime.now().isoformat(),
            "points_earned": 0,
            "points_awarded": {
                "arrival": False,
                "engagement": False,
                "question": False
            }
        }
        
        self.visited_pois.append(new_poi_record)
        return new_poi_record
    
    def mark_poi_points_earned(self, poi_id: str, point_type: str):
        """Marca puntos como otorgados para un POI específico"""
        for poi in self.visited_pois:
            if poi.get("poi_id") == poi_id:
                if "points_awarded" not in poi:
                    poi["points_awarded"] = {"arrival": False, "engagement": False, "question": False}
                poi["points_awarded"][point_type] = True
                break
    
    def get_current_poi_id(self) -> Optional[str]:
        """Obtiene el ID del POI actual basado en el índice"""
        # Mapeo de índices a POI IDs
        poi_map = {
            0: "plaza_mayor",
            1: "mercado_san_miguel", 
            2: "palacio_real",
            3: "teatro_real",
            4: "puerta_del_sol"
        }
        return poi_map.get(self.current_poi_index)
    
    def get_poi_by_id(self, poi_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene datos de un POI visitado por su ID"""
        for poi in self.visited_pois:
            if poi.get("poi_id") == poi_id:
                return poi
        return None
    
    def get_context_summary(self) -> str:
        """Resumen del contexto para prompts - MÁS PERSONAL"""
        parts = []
        
        # Información familiar personalizada
        if self.family_name:
            parts.append(f"Familia: {self.family_name}")
        
        # Adultos con nombres
        if self.adult_names:
            parts.append(f"Adultos: {', '.join(self.adult_names)}")
        
        # Niños con nombres y edades específicas
        if self.children:
            child_details = []
            for child in self.children:
                if child.name and child.age:
                    child_details.append(f"{child.name} ({child.age} años)")
                elif child.name:
                    child_details.append(child.name)
            
            if child_details:
                parts.append(f"Niños: {', '.join(child_details)}")
        
        # Progreso
        if self.total_points > 0:
            parts.append(f"Puntos mágicos: {self.total_points}")
        
        if self.visited_pois:
            parts.append(f"POIs visitados: {len(self.visited_pois)}/5")
        
        # Último hablante
        if self.current_speaker:
            parts.append(f"Último en hablar: {self.current_speaker}")
        
        return "\n".join(parts)
    
    def get_conversation_history(self) -> List[Dict]:
        """Historial para LLM"""
        return self.conversation_history[-5:]  # Últimos 5 intercambios
    
    def get_recent_messages(self, limit: int = 3) -> List[Dict]:
        """Mensajes recientes"""
        return self.conversation_history[-limit:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para BD"""
        return {
            "route_progress": {
                "current_poi_index": self.current_poi_index,
                "points_earned": self.total_points,
                "current_location": self.current_location
            },
            "visited_pois": self.visited_pois,
            "conversation_context": {
                "memory": self.conversation_history,
                "current_speaker": self.current_speaker,
                "updated_at": datetime.now().isoformat()
            }
        }


# Cache en memoria para contextos activos
_context_cache: Dict[int, FamilyContext] = {}


async def load_family_context(family_id: int, db) -> FamilyContext:
    """Carga contexto familiar desde BD real"""
    
    # Buscar en cache primero
    if family_id in _context_cache:
        return _context_cache[family_id]
    
    # Cargar desde BD real
    family_data = await _load_from_database(family_id, db)
    if not family_data:
        raise ValueError(f"Familia {family_id} no encontrada")
    
    # Crear contexto y cachear
    context = FamilyContext(family_data)
    _context_cache[family_id] = context
    
    return context


async def save_family_context(context: FamilyContext, db):
    """Guarda contexto en BD real"""
    context_data = context.to_dict()
    await _save_to_database(context.family_id, context_data, db)


async def _load_from_database(family_id: int, db) -> Optional[Dict[str, Any]]:
    """
    Carga datos desde BD real - CORREGIDO para manejar tipos JSON
    """
    try:
        # Cargar datos de la familia
        family_query = """
            SELECT id, name, preferred_language 
            FROM families 
            WHERE id = %s
        """
        family_result = db.execute_query(family_query, (family_id,))
        
        if not family_result:
            return None
        
        family_data = {
            "id": family_result[0]['id'],
            "name": family_result[0]['name'],
            "preferred_language": family_result[0]['preferred_language'] or 'es'
        }
        
        # Cargar miembros de la familia
        members_query = """
            SELECT name, age, member_type 
            FROM family_members 
            WHERE family_id = %s
        """
        members_result = db.execute_query(members_query, (family_id,))
        
        family_data["members"] = [
            {
                "name": m['name'],
                "age": m['age'],
                "member_type": m['member_type']
            }
            for m in members_result
        ] if members_result else []
        
        # Cargar progreso de la ruta
        progress_query = """
            SELECT current_poi_index, points_earned, current_location
            FROM family_route_progress 
            WHERE family_id = %s
        """
        progress_result = db.execute_query(progress_query, (family_id,))
        
        if progress_result:
            # Parsear current_location si es un string JSON
            current_location = progress_result[0]['current_location']
            if isinstance(current_location, str):
                try:
                    current_location = json.loads(current_location)
                except (json.JSONDecodeError, TypeError):
                    current_location = {}
            elif current_location is None:
                current_location = {}
                
            family_data["route_progress"] = {
                "current_poi_index": progress_result[0]['current_poi_index'],
                "points_earned": progress_result[0]['points_earned'],
                "current_location": current_location
            }
        else:
            family_data["route_progress"] = {
                "current_poi_index": 0,
                "points_earned": 0,
                "current_location": {}
            }
        
        # Cargar contexto de conversación
        conv_query = """
            SELECT conversation_context 
            FROM families 
            WHERE id = %s
        """
        conv_result = db.execute_query(conv_query, (family_id,))
        
        if conv_result and conv_result[0]['conversation_context']:
            conversation_context = conv_result[0]['conversation_context']
            # Parsear si es un string JSON
            if isinstance(conversation_context, str):
                try:
                    conversation_context = json.loads(conversation_context)
                except (json.JSONDecodeError, TypeError):
                    conversation_context = {"memory": [], "current_speaker": None}
            family_data["conversation_context"] = conversation_context
        else:
            family_data["conversation_context"] = {
                "memory": [],
                "current_speaker": None
            }
        
        # Cargar POIs visitados (esto sería de otra tabla si la tuvieras)
        # Por ahora usar lista vacía
        family_data["visited_pois"] = []
        
        return family_data
        
    except Exception as e:
        logger.error(f"Error cargando familia {family_id}: {e}")
        return None


async def _save_to_database(family_id: int, context_data: Dict[str, Any], db):
    """
    Guarda en BD real - CORREGIDO para manejar tipos JSON
    """
    try:
        # Actualizar progreso de ruta
        progress_data = context_data["route_progress"]
        
        # Verificar si existe registro de progreso
        check_query = "SELECT id FROM family_route_progress WHERE family_id = %s"
        exists = db.execute_query(check_query, (family_id,))
        
        # Convertir current_location a JSON string si es un dict
        current_location = progress_data["current_location"]
        if isinstance(current_location, dict):
            current_location_json = json.dumps(current_location)
        else:
            current_location_json = current_location
        
        if exists:
            # Actualizar
            update_query = """
                UPDATE family_route_progress 
                SET current_poi_index = %s, points_earned = %s, current_location = %s
                WHERE family_id = %s
            """
            db.execute_query(update_query, (
                progress_data["current_poi_index"],
                progress_data["points_earned"],
                current_location_json,  # Usar la versión JSON
                family_id
            ))
        else:
            # Insertar
            insert_query = """
                INSERT INTO family_route_progress 
                (family_id, current_poi_index, points_earned, current_location)
                VALUES (%s, %s, %s, %s)
            """
            db.execute_query(insert_query, (
                family_id,
                progress_data["current_poi_index"],
                progress_data["points_earned"],
                current_location_json  # Usar la versión JSON
            ))
        
        # Actualizar contexto de conversación - CONVERTIR A JSON STRING
        conversation_context = context_data["conversation_context"]
        if isinstance(conversation_context, dict):
            conversation_context_json = json.dumps(conversation_context)
        else:
            conversation_context_json = conversation_context
            
        conv_query = """
            UPDATE families 
            SET conversation_context = %s
            WHERE id = %s
        """
        db.execute_query(conv_query, (conversation_context_json, family_id))
        
        logger.info(f"💾 Contexto de familia {family_id} guardado correctamente")
        
    except Exception as e:
        logger.error(f"Error guardando contexto de familia {family_id}: {e}")
        raise e