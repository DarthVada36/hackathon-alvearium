from fastapi import APIRouter, HTTPException, Depends
import logging

from core.models.database import Database, get_db
from Server.core.agents.raton_perez import get_next_destination
from Server.core.agents.location_helper import get_route_overview, find_nearest_poi

router = APIRouter(prefix="/routes", tags=["routes"])
logger = logging.getLogger(__name__)

@router.get("/family/{family_id}/next")
async def get_next_poi(family_id: int, db: Database = Depends(get_db)):
    """
    Obtener siguiente POI para una familia
    """
    try:
        result = await get_next_destination(family_id, db)
        return result
    except Exception as e:
        logger.error(f"Error obteniendo siguiente POI para familia {family_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/overview")
async def route_overview():
    """
    Obtener vista general de la ruta
    """
    try:
        return get_route_overview()
    except Exception as e:
        logger.error(f"Error obteniendo overview de ruta: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/location/update")
async def update_location(location_data: dict, db: Database = Depends(get_db)):
    """
    Actualizar ubicación de una familia
    """
    try:
        family_id = location_data.get("family_id")
        latitude = location_data.get("latitude")
        longitude = location_data.get("longitude")
        
        if not all([family_id, latitude, longitude]):
            raise HTTPException(status_code=400, detail="Datos de ubicación incompletos")
        
        # Actualizar ubicación en progreso de ruta
        query = """
            UPDATE family_route_progress 
            SET current_location = %s
            WHERE family_id = %s
        """
        db.execute_query(query, (
            {"lat": latitude, "lng": longitude},
            family_id
        ))
        
        # Verificar si llegaron a algún POI
        from core.services.location_helper import check_poi_arrival
        arrival_check = check_poi_arrival({"lat": latitude, "lng": longitude})
        
        return {
            "location_updated": True,
            "arrival_check": arrival_check
        }
        
    except Exception as e:
        logger.error(f"Error actualizando ubicación: {e}")
        raise HTTPException(status_code=500, detail=str(e))