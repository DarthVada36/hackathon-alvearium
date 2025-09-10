from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import json
import logging

from core.models.database import Database
from api.dependencies import get_db

router = APIRouter(prefix="/routes", tags=["routes"])
logger = logging.getLogger(__name__)

# Schemas para request/response
class POI(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    lat: float = Field(..., ge=-90, le=90, description="Latitud")
    lng: float = Field(..., ge=-180, le=180, description="Longitud")
    category: Optional[str] = Field(None, description="Categoría del POI")
    estimated_time: Optional[int] = Field(None, ge=1, description="Tiempo estimado en minutos")
    points_reward: Optional[int] = Field(10, ge=0, description="Puntos por visitar este POI")
    proximity_threshold: Optional[float] = Field(50, ge=5, le=200, description="Metros para detectar llegada")
    image_url: Optional[str] = Field(None, description="URL de imagen del POI")
    tips: Optional[List[str]] = Field(None, description="Consejos para visitar")

class RouteBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    difficulty: Optional[str] = Field("easy", regex="^(easy|medium|hard)$")
    suitable_for_children: bool = Field(True, description="Si es adecuada para niños")
    min_age: Optional[int] = Field(0, ge=0, le=18, description="Edad mínima recomendada")
    accessibility: Optional[List[str]] = Field(None, description="Características de accesibilidad")
    tags: Optional[List[str]] = Field(None, description="Etiquetas de la ruta")

class RouteCreate(RouteBase):
    pois: List[POI] = Field(..., min_items=2, description="Puntos de interés de la ruta")
    start_location: Dict[str, float] = Field(..., description="Ubicación de inicio (lat, lng)")
    end_location: Optional[Dict[str, float]] = Field(None, description="Ubicación de fin")
    total_distance: Optional[float] = Field(None, ge=0, description="Distancia total en metros")
    estimated_time: Optional[int] = Field(None, ge=10, description="Tiempo estimado total en minutos")

class Route(RouteBase):
    id: int
    pois: List[Dict[str, Any]]
    start_location: Optional[Dict[str, Any]] = None
    end_location: Optional[Dict[str, Any]] = None
    total_distance: Optional[float] = None
    estimated_time: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RouteSearchFilters(BaseModel):
    category: Optional[str] = None
    difficulty: Optional[str] = None
    max_distance: Optional[float] = None
    max_time: Optional[int] = None
    suitable_for_children: Optional[bool] = None
    min_age: Optional[int] = None
    tags: Optional[List[str]] = None

class StartRouteRequest(BaseModel):
    starting_location: Optional[Dict[str, float]] = Field(None, description="Ubicación actual al iniciar")

class RouteProgressSummary(BaseModel):
    progress_id: int
    route_id: int
    route_name: str
    current_poi_index: int
    total_pois: int
    points_earned: int
    progress_percentage: float
    started_at: str
    current_poi: Optional[Dict[str, Any]] = None
    next_poi: Optional[Dict[str, Any]] = None

# ==================== ENDPOINTS PRINCIPALES ====================

@router.get("/", response_model=List[Route])
async def get_all_routes(
    limit: int = Field(default=10, ge=1, le=100),
    offset: int = Field(default=0, ge=0),
    filters: RouteSearchFilters = Depends(),
    db: Database = Depends(get_db)
):
    """
    Obtener todas las rutas disponibles con filtros opcionales
    
    Permite filtrar por:
    - Categoría de POIs
    - Dificultad
    - Distancia máxima
    - Tiempo máximo
    - Adecuación para niños
    - Edad mínima
    - Etiquetas específicas
    """
    try:
        query_parts = ["SELECT * FROM routes WHERE 1=1"]
        params = []
        
        # Aplicar filtros
        if filters.category:
            query_parts.append("AND pois::text ILIKE %s")
            params.append(f'%"category":"{filters.category}"%')
        
        if filters.difficulty:
            query_parts.append("AND (pois::text ILIKE %s OR name ILIKE %s)")
            params.extend([f'%{filters.difficulty}%', f'%{filters.difficulty}%'])
        
        if filters.max_distance is not None:
            query_parts.append("AND (total_distance IS NULL OR total_distance <= %s)")
            params.append(filters.max_distance)
        
        if filters.max_time is not None:
            query_parts.append("AND (estimated_time IS NULL OR estimated_time <= %s)")
            params.append(filters.max_time)
        
        if filters.suitable_for_children is not None:
            suitable_text = "niños" if filters.suitable_for_children else "adultos"
            query_parts.append("AND (description ILIKE %s OR pois::text ILIKE %s)")
            params.extend([f'%{suitable_text}%', f'%{suitable_text}%'])
        
        if filters.tags:
            for tag in filters.tags:
                query_parts.append("AND (description ILIKE %s OR name ILIKE %s)")
                params.extend([f'%{tag}%', f'%{tag}%'])
        
        # Ordenar y paginar
        query_parts.append("ORDER BY created_at DESC LIMIT %s OFFSET %s")
        params.extend([limit, offset])
        
        final_query = " ".join(query_parts)
        result = db.execute_query(final_query, params)
        
        return result if result else []
        
    except Exception as e:
        logger.error(f"Error obteniendo rutas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener las rutas"
        )

@router.get("/{route_id}", response_model=Route)
async def get_route(route_id: int, db: Database = Depends(get_db)):
    """Obtener una ruta específica por ID"""
    try:
        result = db.execute_query(
            "SELECT * FROM routes WHERE id = %s",
            (route_id,)
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ruta no encontrada"
            )
        
        return result[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo ruta {route_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la ruta"
        )

@router.post("/", response_model=Route, status_code=status.HTTP_201_CREATED)
async def create_route(route: RouteCreate, db: Database = Depends(get_db)):
    """Crear una nueva ruta turística"""
    try:
        # Convertir POIs a formato JSON
        pois_json = [poi.dict() for poi in route.pois]
        
        # Calcular distancia total si no se proporciona
        total_distance = route.total_distance
        if not total_distance and len(route.pois) >= 2:
            # Estimación simple basada en distancia entre POIs
            total_distance = 0
            for i in range(len(route.pois) - 1):
                poi1, poi2 = route.pois[i], route.pois[i + 1]
                # Distancia euclidiana aproximada en metros
                lat_diff = abs(poi1.lat - poi2.lat)
                lng_diff = abs(poi1.lng - poi2.lng)
                distance = ((lat_diff ** 2 + lng_diff ** 2) ** 0.5) * 111000
                total_distance += distance
        
        # Calcular tiempo estimado si no se proporciona
        estimated_time = route.estimated_time
        if not estimated_time:
            poi_times = sum(poi.estimated_time or 20 for poi in route.pois)
            walking_time = (total_distance / 83) if total_distance else 0  # ~5km/h
            estimated_time = int(poi_times + walking_time)
        
        result = db.execute_query(
            """
            INSERT INTO routes (
                name, description, difficulty, suitable_for_children, min_age,
                accessibility, tags, pois, start_location, end_location,
                total_distance, estimated_time
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            RETURNING *
            """,
            (
                route.name,
                route.description,
                route.difficulty,
                route.suitable_for_children,
                route.min_age,
                json.dumps(route.accessibility or []),
                json.dumps(route.tags or []),
                json.dumps(pois_json),
                json.dumps(route.start_location),
                json.dumps(route.end_location) if route.end_location else None,
                total_distance,
                estimated_time
            )
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo crear la ruta"
            )
            
        return result[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando ruta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear la ruta"
        )

# ==================== ENDPOINTS PARA FAMILIAS Y RUTAS ====================

@router.post("/{route_id}/start/{family_id}")
async def start_route_for_family(
    route_id: int,
    family_id: int,
    start_request: StartRouteRequest,
    db: Database = Depends(get_db)
):
    """
    ENDPOINT REQUERIDO: Iniciar una ruta para una familia específica
    
    Crea el progreso de ruta y establece el estado inicial para el seguimiento
    """
    try:
        # Verificar que la ruta existe
        route_result = db.execute_query(
            "SELECT * FROM routes WHERE id = %s",
            (route_id,)
        )
        
        if not route_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ruta no encontrada"
            )
        
        # Verificar que la familia existe
        family_result = db.execute_query(
            "SELECT id FROM families WHERE id = %s",
            (family_id,)
        )
        
        if not family_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Familia no encontrada"
            )
        
        # Verificar si ya hay una ruta activa
        active_route = db.execute_query(
            """
            SELECT id FROM family_route_progress 
            WHERE family_id = %s AND completed_at IS NULL
            """,
            (family_id,)
        )
        
        if active_route:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La familia ya tiene una ruta activa. Debe completarla o cancelarla primero."
            )
        
        # Crear progreso de ruta
        location_json = json.dumps(start_request.starting_location) if start_request.starting_location else None
        
        progress_result = db.execute_query(
            """
            INSERT INTO family_route_progress (
                family_id, route_id, current_poi_index, 
                points_earned, current_location
            )
            VALUES (%s, %s, 0, 0, %s)
            RETURNING *
            """,
            (family_id, route_id, location_json)
        )
        
        if not progress_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo iniciar la ruta"
            )
        
        progress = progress_result[0]
        route = route_result[0]
        route_pois = route.get('pois', [])
        
        return {
            "message": f"¡Ruta '{route['name']}' iniciada exitosamente!",
            "progress_id": progress['id'],
            "route": {
                "id": route['id'],
                "name": route['name'],
                "description": route['description'],
                "total_pois": len(route_pois),
                "estimated_time": route.get('estimated_time'),
                "difficulty": route.get('difficulty', 'easy')
            },
            "current_status": {
                "current_poi_index": 0,
                "points_earned": 0,
                "started_at": progress['started_at'].isoformat(),
                "next_poi": route_pois[0] if route_pois else None
            },
            "tips": [
                "¡Recuerda activar tu ubicación para obtener la mejor experiencia!",
                "Puedes ganar puntos visitando cada punto de interés",
                "El Ratoncito Pérez te dará pistas y datos curiosos en el camino"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error iniciando ruta {route_id} para familia {family_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al iniciar la ruta"
        )

@router.get("/family/{family_id}/current", response_model=RouteProgressSummary)
async def get_current_family_route(family_id: int, db: Database = Depends(get_db)):
    """
    ENDPOINT REQUERIDO: Obtener el estado actual de la ruta de una familia
    """
    try:
        result = db.execute_query(
            """
            SELECT 
                frp.*,
                r.name as route_name,
                r.description as route_description,
                r.pois,
                r.total_distance,
                r.estimated_time,
                r.difficulty,
                r.suitable_for_children
            FROM family_route_progress frp
            JOIN routes r ON frp.route_id = r.id
            WHERE frp.family_id = %s AND frp.completed_at IS NULL
            ORDER BY frp.started_at DESC
            LIMIT 1
            """,
            (family_id,)
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay ruta activa para esta familia"
            )
        
        route_data = result[0]
        pois = route_data.get('pois', [])
        current_poi_index = route_data.get('current_poi_index', 0)
        
        return RouteProgressSummary(
            progress_id=route_data['id'],
            route_id=route_data['route_id'],
            route_name=route_data['route_name'],
            current_poi_index=current_poi_index,
            total_pois=len(pois),
            points_earned=route_data.get('points_earned', 0),
            progress_percentage=(current_poi_index / len(pois)) * 100 if pois else 0,
            started_at=route_data['started_at'].isoformat(),
            current_poi=pois[current_poi_index] if current_poi_index < len(pois) else None,
            next_poi=pois[current_poi_index + 1] if current_poi_index + 1 < len(pois) else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo ruta actual de familia {family_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la ruta actual"
        )

@router.put("/family/{family_id}/advance")
async def advance_route_progress(
    family_id: int,
    points_earned: int = Field(default=0, ge=0, description="Puntos ganados por completar el POI"),
    db: Database = Depends(get_db)
):
    """
    ENDPOINT REQUERIDO: Avanzar al siguiente POI en la ruta activa
    
    Actualiza el progreso y otorga puntos por completar el POI actual
    """
    try:
        # Obtener ruta activa
        route_result = db.execute_query(
            """
            SELECT frp.*, r.pois, r.name as route_name
            FROM family_route_progress frp
            JOIN routes r ON frp.route_id = r.id
            WHERE frp.family_id = %s AND frp.completed_at IS NULL
            ORDER BY frp.started_at DESC
            LIMIT 1
            """,
            (family_id,)
        )
        
        if not route_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay ruta activa para esta familia"
            )
        
        progress_data = route_result[0]
        current_poi_index = progress_data['current_poi_index'] or 0
        total_points = (progress_data['points_earned'] or 0) + points_earned
        pois = progress_data.get('pois', [])
        new_poi_index = current_poi_index + 1
        
        # Verificar si la ruta se ha completado
        route_completed = new_poi_index >= len(pois)
        completed_at = datetime.now() if route_completed else None
        
        # Calcular puntos bonus por completar POI
        poi_bonus = 0
        if current_poi_index < len(pois):
            current_poi = pois[current_poi_index]
            if isinstance(current_poi, dict):
                poi_bonus = current_poi.get('points_reward', 10)
                total_points += poi_bonus
        
        # Puntos bonus por completar toda la ruta
        completion_bonus = 50 if route_completed else 0
        if completion_bonus:
            total_points += completion_bonus
        
        # Actualizar progreso
        update_result = db.execute_query(
            """
            UPDATE family_route_progress 
            SET current_poi_index = %s, points_earned = %s, completed_at = %s
            WHERE id = %s
            RETURNING *
            """,
            (new_poi_index, total_points, completed_at, progress_data['id'])
        )
        
        if not update_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo actualizar el progreso"
            )
        
        response_data = {
            "message": "¡POI completado exitosamente!" if not route_completed else f"¡Felicidades! Has completado la ruta '{progress_data['route_name']}'",
            "previous_poi_index": current_poi_index,
            "current_poi_index": new_poi_index,
            "points_breakdown": {
                "interaction_points": points_earned,
                "poi_bonus": poi_bonus,
                "completion_bonus": completion_bonus,
                "total_added": points_earned + poi_bonus + completion_bonus
            },
            "total_points": total_points,
            "route_completed": route_completed,
            "progress_percentage": (new_poi_index / len(pois)) * 100 if pois else 100
        }
        
        # Información del siguiente POI si no se completó la ruta
        if not route_completed and new_poi_index < len(pois):
            response_data["next_poi"] = pois[new_poi_index]
            response_data["remaining_pois"] = len(pois) - new_poi_index
        
        # Mensaje de celebración si se completó
        if route_completed:
            response_data["celebration"] = {
                "title": "¡Ruta Completada!",
                "message": f"Has visitado todos los {len(pois)} puntos de interés. ¡El Ratoncito Pérez está muy orgulloso!",
                "suggestions": [
                    "Ver estadísticas de la ruta",
                    "Comenzar una nueva ruta",
                    "Compartir logros"
                ]
            }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error avanzando progreso de familia {family_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al avanzar en la ruta"
        )

@router.delete("/family/{family_id}/current")
async def cancel_family_route(family_id: int, db: Database = Depends(get_db)):
    """Cancelar la ruta actual de una familia"""
    try:
        # Obtener información de la ruta antes de cancelar
        route_info = db.execute_query(
            """
            SELECT frp.*, r.name as route_name
            FROM family_route_progress frp
            JOIN routes r ON frp.route_id = r.id
            WHERE frp.family_id = %s AND frp.completed_at IS NULL
            """,
            (family_id,)
        )
        
        if not route_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay ruta activa para cancelar"
            )
        
        # Marcar ruta como completada (cancelada)
        result = db.execute_query(
            """
            UPDATE family_route_progress 
            SET completed_at = CURRENT_TIMESTAMP
            WHERE family_id = %s AND completed_at IS NULL
            RETURNING id, route_id, points_earned
            """,
            (family_id,)
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se pudo cancelar la ruta"
            )
        
        return {
            "message": f"Ruta '{route_info[0]['route_name']}' cancelada exitosamente",
            "progress_id": result[0]['id'],
            "points_retained": result[0]['points_earned'],
            "cancelled_at": datetime.now().isoformat(),
            "note": "Los puntos ganados hasta ahora se mantienen en tu historial"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelando ruta de familia {family_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cancelar la ruta"
        )

# ==================== ENDPOINTS ADICIONALES ====================

@router.get("/search")
async def search_routes(
    query: str = Field(..., min_length=2, description="Término de búsqueda"),
    filters: RouteSearchFilters = Depends(),
    limit: int = Field(default=10, ge=1, le=50),
    db: Database = Depends(get_db)
):
    """Buscar rutas por nombre, descripción o características"""
    try:
        base_query = """
            SELECT * FROM routes 
            WHERE (name ILIKE %s OR description ILIKE %s OR pois::text ILIKE %s)
        """
        params = [f'%{query}%', f'%{query}%', f'%{query}%']
        
        # Aplicar filtros adicionales
        if filters.category:
            base_query += " AND pois::text ILIKE %s"
            params.append(f'%"category":"{filters.category}"%')
        
        if filters.difficulty:
            base_query += " AND difficulty = %s"
            params.append(filters.difficulty)
        
        if filters.suitable_for_children is not None:
            base_query += " AND suitable_for_children = %s"
            params.append(filters.suitable_for_children)
        
        if filters.max_distance:
            base_query += " AND (total_distance IS NULL OR total_distance <= %s)"
            params.append(filters.max_distance)
        
        if filters.max_time:
            base_query += " AND (estimated_time IS NULL OR estimated_time <= %s)"
            params.append(filters.max_time)
        
        base_query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        result = db.execute_query(base_query, params)
        
        return {
            "query": query,
            "filters_applied": filters.dict(exclude_unset=True),
            "total_results": len(result) if result else 0,
            "routes": result if result else []
        }
        
    except Exception as e:
        logger.error(f"Error buscando rutas con query '{query}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al buscar rutas"
        )

@router.get("/{route_id}/pois")
async def get_route_pois(route_id: int, db: Database = Depends(get_db)):
    """Obtener información detallada de todos los POIs de una ruta"""
    try:
        result = db.execute_query(
            "SELECT name, pois FROM routes WHERE id = %s",
            (route_id,)
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ruta no encontrada"
            )
        
        route_data = result[0]
        pois = route_data.get('pois', [])
        
        # Enriquecer POIs con información adicional
        enriched_pois = []
        for i, poi in enumerate(pois):
            if isinstance(poi, dict):
                enriched_poi = poi.copy()
                enriched_poi['index'] = i
                enriched_poi['is_start'] = i == 0
                enriched_poi['is_end'] = i == len(pois) - 1
                enriched_pois.append(enriched_poi)
        
        return {
            "route_id": route_id,
            "route_name": route_data['name'],
            "total_pois": len(pois),
            "pois": enriched_pois
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo POIs de ruta {route_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener los puntos de interés"
        )