from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import json
import logging
import math

from core.models.database import Database
from api.dependencies import get_db

router = APIRouter(prefix="/families", tags=["families"])
logger = logging.getLogger(__name__)

# Schemas para request/response
class LocationUpdate(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitud")
    lng: float = Field(..., ge=-180, le=180, description="Longitud")
    accuracy: Optional[float] = Field(None, description="Precisión en metros")
    timestamp: Optional[str] = Field(None, description="Timestamp ISO")

class PointsUpdate(BaseModel):
    points_to_add: int = Field(..., ge=0, description="Puntos a añadir")
    reason: Optional[str] = Field(None, max_length=200, description="Razón del otorgamiento")
    location: Optional[LocationUpdate] = Field(None, description="Ubicación donde se otorgaron")

class ContextUpdate(BaseModel):
    preferences: Optional[Dict[str, Any]] = Field(None, description="Preferencias familiares")
    interests: Optional[List[str]] = Field(None, description="Intereses específicos")
    accessibility_needs: Optional[List[str]] = Field(None, description="Necesidades de accesibilidad")
    language: Optional[str] = Field(None, description="Idioma preferido")
    custom_data: Optional[Dict[str, Any]] = Field(None, description="Datos personalizados")

class FamilyMemberBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=150)
    member_type: str = Field(..., regex="^(adult|child)$")

class FamilyMemberCreate(FamilyMemberBase):
    pass

class FamilyMember(FamilyMemberBase):
    id: int
    family_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class FamilyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    preferred_language: str = Field(default='es', regex="^(es|en|fr|de|it|pt)$")

class FamilyCreate(FamilyBase):
    user_id: int

class Family(FamilyBase):
    id: int
    user_id: int
    created_at: datetime
    conversation_context: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class FamilyWithMembers(Family):
    members: List[FamilyMember] = []

class FamilyContextResponse(BaseModel):
    family_id: int
    context: Dict[str, Any]
    members: List[FamilyMember]
    current_route: Optional[Dict[str, Any]] = None
    total_points: int = 0

# ==================== FUNCIONES AUXILIARES ====================

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calcular distancia entre dos puntos usando fórmula de Haversine"""
    R = 6371000  # Radio de la Tierra en metros
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lng/2) * math.sin(delta_lng/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# ==================== ENDPOINTS PRINCIPALES ====================

@router.get("/{family_id}/context", response_model=FamilyContextResponse)
async def get_family_context(family_id: int, db: Database = Depends(get_db)):
    """
    ENDPOINT REQUERIDO: Obtener datos familiares completos
    
    Proporciona toda la información contextual necesaria para el agente:
    - Información básica de la familia
    - Miembros y sus características
    - Contexto conversacional
    - Ruta activa y progreso
    - Puntos acumulados
    """
    try:
        # Obtener información básica de la familia
        family_result = db.execute_query(
            "SELECT * FROM families WHERE id = %s",
            (family_id,)
        )
        
        if not family_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Familia no encontrada"
            )
        
        family_data = family_result[0]
        
        # Obtener miembros de la familia
        members_result = db.execute_query(
            "SELECT * FROM family_members WHERE family_id = %s ORDER BY age DESC",
            (family_id,)
        )
        
        members = [FamilyMember(**member) for member in members_result] if members_result else []
        
        # Obtener ruta activa
        route_result = db.execute_query("""
            SELECT 
                frp.*,
                r.name as route_name,
                r.description as route_description,
                r.pois,
                r.total_distance,
                r.estimated_time
            FROM family_route_progress frp
            JOIN routes r ON frp.route_id = r.id
            WHERE frp.family_id = %s AND frp.completed_at IS NULL
            ORDER BY frp.started_at DESC
            LIMIT 1
        """, (family_id,))
        
        current_route = route_result[0] if route_result else None
        
        # Calcular puntos totales
        total_points = 0
        if current_route:
            total_points = current_route.get('points_earned', 0)
        
        # Preparar contexto
        conversation_context = family_data.get('conversation_context', {})
        
        return FamilyContextResponse(
            family_id=family_id,
            context={
                "family_info": {
                    "name": family_data['name'],
                    "preferred_language": family_data['preferred_language'],
                    "created_at": family_data['created_at'].isoformat() if family_data['created_at'] else None
                },
                "conversation_context": conversation_context,
                "preferences": conversation_context.get('preferences', {}),
                "interests": conversation_context.get('interests', []),
                "accessibility_needs": conversation_context.get('accessibility_needs', [])
            },
            members=members,
            current_route=current_route,
            total_points=total_points
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo contexto de familia {family_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el contexto familiar"
        )

@router.put("/{family_id}/context")
async def update_family_context(
    family_id: int, 
    context_update: ContextUpdate,
    db: Database = Depends(get_db)
):
    """
    ENDPOINT REQUERIDO: Actualizar contexto familiar
    
    Permite actualizar:
    - Preferencias de la familia
    - Intereses específicos
    - Necesidades de accesibilidad
    - Configuración de idioma
    - Datos personalizados adicionales
    """
    try:
        # Verificar que la familia existe
        family_result = db.execute_query(
            "SELECT conversation_context FROM families WHERE id = %s",
            (family_id,)
        )
        
        if not family_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Familia no encontrada"
            )
        
        # Obtener contexto actual
        current_context = family_result[0].get('conversation_context', {})
        
        # Actualizar campos específicos
        if context_update.preferences is not None:
            current_context['preferences'] = context_update.preferences
            
        if context_update.interests is not None:
            current_context['interests'] = context_update.interests
            
        if context_update.accessibility_needs is not None:
            current_context['accessibility_needs'] = context_update.accessibility_needs
            
        if context_update.custom_data is not None:
            if 'custom_data' not in current_context:
                current_context['custom_data'] = {}
            current_context['custom_data'].update(context_update.custom_data)
        
        # Agregar timestamp de última actualización
        current_context['last_updated'] = datetime.now().isoformat()
        
        # Preparar query de actualización
        update_fields = []
        params = []
        
        # Actualizar contexto
        update_fields.append("conversation_context = %s")
        params.append(json.dumps(current_context))
        
        # Actualizar idioma si se especifica
        if context_update.language:
            update_fields.append("preferred_language = %s")
            params.append(context_update.language)
        
        params.append(family_id)
        
        # Ejecutar actualización
        query = f"UPDATE families SET {', '.join(update_fields)} WHERE id = %s"
        result = db.execute_query(query, params)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo actualizar el contexto"
            )
        
        return {
            "message": "Contexto familiar actualizado correctamente",
            "updated_fields": list(context_update.dict(exclude_unset=True).keys()),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando contexto de familia {family_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el contexto familiar"
        )

@router.put("/{family_id}/points")
async def update_family_points(
    family_id: int,
    points_update: PointsUpdate,
    db: Database = Depends(get_db)
):
    """
    ENDPOINT REQUERIDO: Actualizar puntos familiares
    
    Permite otorgar puntos por:
    - Completar actividades
    - Visitar lugares de interés
    - Participar en juegos educativos
    - Logros especiales
    """
    try:
        # Verificar que la familia tiene una ruta activa
        route_result = db.execute_query("""
            SELECT id, points_earned, route_id
            FROM family_route_progress 
            WHERE family_id = %s AND completed_at IS NULL
            ORDER BY started_at DESC
            LIMIT 1
        """, (family_id,))
        
        if not route_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay una ruta activa para esta familia"
            )
        
        progress_id = route_result[0]['id']
        current_points = route_result[0]['points_earned'] or 0
        new_total = current_points + points_update.points_to_add
        
        # Actualizar puntos
        db.execute_query(
            "UPDATE family_route_progress SET points_earned = %s WHERE id = %s",
            (new_total, progress_id)
        )
        
        # Registrar la transacción de puntos en el contexto
        family_result = db.execute_query(
            "SELECT conversation_context FROM families WHERE id = %s",
            (family_id,)
        )
        
        if family_result:
            context = family_result[0].get('conversation_context', {})
            
            if 'points_history' not in context:
                context['points_history'] = []
            
            # Mantener solo los últimos 50 registros
            context['points_history'] = context['points_history'][-49:] + [{
                "points_added": points_update.points_to_add,
                "reason": points_update.reason,
                "location": points_update.location.dict() if points_update.location else None,
                "timestamp": datetime.now().isoformat(),
                "total_after": new_total
            }]
            
            db.execute_query(
                "UPDATE families SET conversation_context = %s WHERE id = %s",
                (json.dumps(context), family_id)
            )
        
        # Si se proporcionó ubicación, actualizar también la posición actual
        if points_update.location:
            db.execute_query(
                "UPDATE family_route_progress SET current_location = %s WHERE id = %s",
                (json.dumps(points_update.location.dict()), progress_id)
            )
            
            # Agregar registro de ubicación
            db.execute_query(
                "INSERT INTO location_updates (family_route_progress_id, location) VALUES (%s, %s)",
                (progress_id, json.dumps(points_update.location.dict()))
            )
        
        return {
            "message": f"¡{points_update.points_to_add} puntos otorgados exitosamente!",
            "points_added": points_update.points_to_add,
            "previous_total": current_points,
            "new_total": new_total,
            "reason": points_update.reason,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando puntos de familia {family_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar los puntos familiares"
        )

@router.put("/{family_id}/location")
async def update_family_location(
    family_id: int,
    location_update: LocationUpdate,
    db: Database = Depends(get_db)
):
    """
    ENDPOINT REQUERIDO: Actualizar ubicación familiar
    
    Rastrea la ubicación en tiempo real para:
    - Navegación de rutas
    - Recomendaciones contextuales
    - Detección de llegada a puntos de interés
    - Optimización de experiencia basada en posición
    """
    try:
        # Verificar que la familia tiene una ruta activa
        route_result = db.execute_query("""
            SELECT frp.id, frp.current_poi_index, r.pois
            FROM family_route_progress frp
            JOIN routes r ON frp.route_id = r.id
            WHERE frp.family_id = %s AND frp.completed_at IS NULL
            ORDER BY frp.started_at DESC
            LIMIT 1
        """, (family_id,))
        
        if not route_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay una ruta activa para esta familia"
            )
        
        progress_id = route_result[0]['id']
        current_poi_index = route_result[0]['current_poi_index'] or 0
        route_pois = route_result[0]['pois'] or []
        
        # Actualizar ubicación actual
        location_data = location_update.dict()
        if not location_data.get('timestamp'):
            location_data['timestamp'] = datetime.now().isoformat()
        
        db.execute_query(
            "UPDATE family_route_progress SET current_location = %s WHERE id = %s",
            (json.dumps(location_data), progress_id)
        )
        
        # Agregar registro histórico de ubicación
        db.execute_query(
            "INSERT INTO location_updates (family_route_progress_id, location) VALUES (%s, %s)",
            (progress_id, json.dumps(location_data))
        )
        
        # Verificar proximidad a puntos de interés
        proximity_alerts = []
        if route_pois and current_poi_index < len(route_pois):
            next_poi = route_pois[current_poi_index]
            
            if isinstance(next_poi, dict) and 'lat' in next_poi and 'lng' in next_poi:
                distance = calculate_distance(
                    location_update.lat, location_update.lng,
                    next_poi['lat'], next_poi['lng']
                )
                
                # Verificar si está cerca del POI (50 metros por defecto)
                proximity_threshold = next_poi.get('proximity_threshold', 50)
                
                if distance <= proximity_threshold:
                    proximity_alerts.append({
                        "poi_index": current_poi_index,
                        "poi_name": next_poi.get('name', f'Punto {current_poi_index + 1}'),
                        "distance": round(distance, 2),
                        "message": f"¡Has llegado a {next_poi.get('name', 'tu destino')}!",
                        "points_available": next_poi.get('points_reward', 10),
                        "can_advance": True
                    })
        
        # Verificar proximidad a POIs futuros (para dar pistas)
        upcoming_pois = []
        if route_pois:
            for i in range(current_poi_index + 1, min(current_poi_index + 3, len(route_pois))):
                poi = route_pois[i]
                if isinstance(poi, dict) and 'lat' in poi and 'lng' in poi:
                    distance = calculate_distance(
                        location_update.lat, location_update.lng,
                        poi['lat'], poi['lng']
                    )
                    
                    if distance <= 200:  # 200 metros para POIs cercanos
                        upcoming_pois.append({
                            "poi_index": i,
                            "poi_name": poi.get('name', f'Punto {i + 1}'),
                            "distance": round(distance, 2),
                            "estimated_walk_time": max(1, int(distance / 83))  # ~5 km/h walking speed
                        })
        
        return {
            "message": "Ubicación actualizada correctamente",
            "location": location_data,
            "proximity_alerts": proximity_alerts,
            "upcoming_pois": upcoming_pois,
            "current_poi_index": current_poi_index,
            "total_pois": len(route_pois),
            "route_progress": {
                "completed_pois": current_poi_index,
                "remaining_pois": max(0, len(route_pois) - current_poi_index),
                "progress_percentage": (current_poi_index / len(route_pois)) * 100 if route_pois else 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando ubicación de familia {family_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar la ubicación familiar"
        )

# ==================== ENDPOINTS ADICIONALES ====================

@router.post("/", response_model=Family, status_code=status.HTTP_201_CREATED)
async def create_family(family: FamilyCreate, db: Database = Depends(get_db)):
    """Crear una nueva familia"""
    try:
        result = db.execute_query(
            """
            INSERT INTO families (user_id, name, preferred_language) 
            VALUES (%s, %s, %s) 
            RETURNING id, user_id, name, preferred_language, created_at, conversation_context
            """,
            (family.user_id, family.name, family.preferred_language)
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo crear la familia"
            )
            
        return result[0]
    except Exception as e:
        logger.error(f"Error creando familia: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear la familia"
        )

@router.get("/user/{user_id}", response_model=Family)
async def get_family_by_user_id(user_id: int, db: Database = Depends(get_db)):
    """Obtener familia por ID de usuario"""
    try:
        result = db.execute_query(
            "SELECT * FROM families WHERE user_id = %s",
            (user_id,)
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Familia no encontrada"
            )
            
        return result[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo familia por usuario {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la familia"
        )

@router.get("/{family_id}/complete", response_model=FamilyWithMembers)
async def get_family_with_members(family_id: int, db: Database = Depends(get_db)):
    """Obtener familia completa con sus miembros"""
    try:
        # Obtener información de la familia
        family_result = db.execute_query(
            "SELECT * FROM families WHERE id = %s",
            (family_id,)
        )
        
        if not family_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Familia no encontrada"
            )
        
        # Obtener miembros de la familia
        members_result = db.execute_query(
            "SELECT * FROM family_members WHERE family_id = %s ORDER BY created_at",
            (family_id,)
        )
        
        family_data = family_result[0]
        family_data["members"] = [FamilyMember(**member) for member in members_result] if members_result else []
        
        return family_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo familia completa {family_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la familia"
        )

@router.post("/{family_id}/members", response_model=FamilyMember, status_code=status.HTTP_201_CREATED)
async def add_family_member(
    family_id: int, 
    member: FamilyMemberCreate, 
    db: Database = Depends(get_db)
):
    """Añadir un miembro a la familia"""
    try:
        result = db.execute_query(
            """
            INSERT INTO family_members (family_id, name, age, member_type) 
            VALUES (%s, %s, %s, %s) 
            RETURNING id, family_id, name, age, member_type, created_at
            """,
            (family_id, member.name, member.age, member.member_type)
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo añadir el miembro a la familia"
            )
            
        return result[0]
    except Exception as e:
        logger.error(f"Error añadiendo miembro a familia {family_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al añadir miembro"
        )

@router.get("/{family_id}/stats")
async def get_family_stats(family_id: int, db: Database = Depends(get_db)):
    """Obtener estadísticas de la familia"""
    try:
        # Estadísticas básicas
        stats_result = db.execute_query("""
            SELECT 
                COUNT(DISTINCT CASE WHEN frp.completed_at IS NOT NULL THEN frp.id END) as routes_completed,
                COUNT(DISTINCT CASE WHEN frp.completed_at IS NULL THEN frp.id END) as routes_active,
                COALESCE(SUM(frp.points_earned), 0) as total_points_earned,
                COUNT(DISTINCT lu.id) as total_locations_tracked
            FROM families f
            LEFT JOIN family_route_progress frp ON f.id = frp.family_id
            LEFT JOIN location_updates lu ON frp.id = lu.family_route_progress_id
            WHERE f.id = %s
            GROUP BY f.id
        """, (family_id,))
        
        if not stats_result:
            return {
                "family_id": family_id,
                "routes_completed": 0,
                "routes_active": 0,
                "total_points_earned": 0,
                "total_locations_tracked": 0,
                "members_count": 0
            }
        
        stats = stats_result[0]
        
        # Contar miembros
        members_result = db.execute_query(
            "SELECT COUNT(*) as count FROM family_members WHERE family_id = %s",
            (family_id,)
        )
        
        members_count = members_result[0]['count'] if members_result else 0
        
        return {
            "family_id": family_id,
            "routes_completed": stats['routes_completed'] or 0,
            "routes_active": stats['routes_active'] or 0,
            "total_points_earned": stats['total_points_earned'] or 0,
            "total_locations_tracked": stats['total_locations_tracked'] or 0,
            "members_count": members_count
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de familia {family_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estadísticas familiares"
        )