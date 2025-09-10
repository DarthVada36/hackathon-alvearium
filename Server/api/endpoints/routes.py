from fastapi import APIRouter, HTTPException, Depends
import logging

from core.models.database import Database, get_db
from Server.core.agents.raton_perez import get_next_destination
from Server.core.agents.location_helper import RATON_PEREZ_ROUTE

router = APIRouter(prefix="/routes", tags=["routes"])
logger = logging.getLogger(__name__)

@router.get("/family/{family_id}/next")
async def get_next_poi(family_id: int, db: Database = Depends(get_db)):
    """
    Obtener el siguiente POI para una familia.
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
    Obtener vista general de la ruta (usando la ruta fija para la demo).
    """
    try:
        return {"route": RATON_PEREZ_ROUTE}
    except Exception as e:
        logger.error(f"Error obteniendo overview de ruta: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/location/update")
async def update_location(location_data: dict, db: Database = Depends(get_db)):
    """
    Actualizar ubicación de una familia (simulación para la demo).
    """
    try:
        family_id = location_data.get("family_id")
        latitude = location_data.get("latitude")
        longitude = location_data.get("longitude")

        if not all([family_id, latitude, longitude]):
            raise HTTPException(status_code=400, detail="Datos de ubicación incompletos")

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

    except Exception as e:
        logger.error(f"Error actualizando ubicación: {e}")
        raise HTTPException(status_code=500, detail=str(e))
