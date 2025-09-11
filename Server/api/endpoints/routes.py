from fastapi import APIRouter, HTTPException, Depends
import logging

from Server.core.models.database import Database
from Server.api.dependencies import get_db
from Server.core.agents.raton_perez import get_next_destination
from Server.core.agents.location_helper import RATON_PEREZ_ROUTE
from Server.core.security.dependencies import get_current_user, AuthenticatedUser, require_family_ownership

router = APIRouter(prefix="/routes", tags=["routes"])
logger = logging.getLogger(__name__)

@router.get("/family/{family_id}/next")
async def get_next_poi(
    family_id: int, 
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    Obtener el siguiente POI para una familia (requiere autenticación).
    """
    try:
        # Verificar que la familia pertenece al usuario
        require_family_ownership(family_id, current_user, db)
        
        result = await get_next_destination(family_id, db)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo siguiente POI para familia {family_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/family/{family_id}/advance")
async def advance_to_next_poi(
    family_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    Avanzar manualmente al siguiente POI (simula botón 'Siguiente POI')
    El agente sabrá automáticamente que estamos en el nuevo POI
    """
    try:
        # Verificar que la familia pertenece al usuario
        require_family_ownership(family_id, current_user, db)
        
        # Cargar contexto actual de la familia
        from Server.core.agents.family_context import load_family_context, save_family_context
        
        context = await load_family_context(family_id, db)
        current_index = context.current_poi_index
        next_index = current_index + 1
        
        # Verificar que no hemos completado la ruta
        if next_index >= len(RATON_PEREZ_ROUTE):
            return {
                "success": False,
                "completed": True,
                "message": "¡Felicidades! ¡Habéis completado toda la ruta del Ratoncito Pérez!",
                "total_pois": len(RATON_PEREZ_ROUTE),
                "final_points": context.total_points
            }
        
        # Obtener información del nuevo POI
        next_poi = RATON_PEREZ_ROUTE[next_index]
        
        # Actualizar el contexto
        context.current_poi_index = next_index
        
        # Marcar llegada automática al nuevo POI con 100 puntos
        context.add_visited_poi({
            "poi_id": next_poi["id"],
            "poi_name": next_poi["name"],
            "poi_index": next_index,
            "points": 100
        }, mark_arrival=True)
        
        # Otorgar puntos por llegada
        arrival_points = 100
        context.total_points += arrival_points
        
        # Guardar contexto actualizado
        await save_family_context(context, db)
        
        logger.info(f"✅ Familia {family_id} avanzada a POI {next_index}: {next_poi['name']}")
        
        return {
            "success": True,
            "advanced": True,
            "message": f"¡Bienvenidos a {next_poi['name']}!",
            "poi": {
                "id": next_poi["id"],
                "name": next_poi["name"],
                "description": next_poi.get("description", ""),
                "index": next_index
            },
            "progress": f"{next_index + 1}/{len(RATON_PEREZ_ROUTE)}",
            "points_earned": arrival_points,
            "total_points": context.total_points,
            "arrival_message": f"¡Acabamos de llegar a {next_poi['name']}! 🐭✨"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error avanzando POI para familia {family_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/overview")
async def route_overview():
    """
    Obtener vista general de la ruta (usando la ruta fija para la demo).
    """
    try:
        return {"route": RATON_PEREZ_ROUTE}
    except Exception as e:
        logger.error(f"Error obteniendo overview de ruta: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/location/update")
async def update_location(
    location_data: dict, 
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    Actualizar ubicación de una familia (simulación para la demo).
    Requiere autenticación.
    """
    try:
        family_id = location_data.get("family_id")
        latitude = location_data.get("latitude")
        longitude = location_data.get("longitude")

        if not all([family_id, latitude, longitude]):
            raise HTTPException(status_code=400, detail="Datos de ubicación incompletos")

        # Verificar que la familia pertenece al usuario
        require_family_ownership(family_id, current_user, db)

        # Guardar ubicación actual en la base de datos (simulación)
        query = """
            UPDATE family_route_progress 
            SET current_location = %s
            WHERE family_id = %s
        """
        db.execute_query(query, ({"lat": latitude, "lng": longitude}, family_id))

        # Para la demo, no comprobamos llegada real: devolvemos estado fijo
        return {
            "location_updated": True,
            "arrival_check": {"arrived": False, "message": "Ubicación actualizada (demo, sin validación de POI)."}
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando ubicación: {e}")
        raise HTTPException(status_code=500, detail=str(e))