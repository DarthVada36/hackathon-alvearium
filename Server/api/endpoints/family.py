from fastapi import APIRouter, HTTPException, Depends
import logging

from Server.core.models.database import Database
from Server.api.dependencies import get_db
from Server.core.models.schemas import FamilyCreate, FamilyResponse

router = APIRouter(prefix="/families", tags=["families"])
logger = logging.getLogger(__name__)


@router.get("/ping")
def ping():
    return {"service": "families", "ok": True}


@router.post("/", response_model=FamilyResponse)
async def create_family(family_data: FamilyCreate, db: Database = Depends(get_db)):
    """
    Crear una nueva familia
    """
    try:
        # Por ahora usamos user_id = 1 para desarrollo (sin autenticación)
        # TODO: Implementar autenticación real y obtener user_id del token
        default_user_id = 1
        
        family_query = """
            INSERT INTO families (user_id, name, preferred_language)
            VALUES (%s, %s, %s)
            RETURNING id, name, preferred_language, created_at
        """
        family_result = db.execute_query(
            family_query,
            (default_user_id, family_data.name, family_data.preferred_language),
        )

        if not family_result:
            raise HTTPException(status_code=500, detail="Error creando familia")

        family_id = family_result[0]["id"]
        logger.info(f"Family created with ID: {family_id}")

        # Insertar miembros uno por uno para mejor control de errores
        for member in family_data.members:
            member_query = """
                INSERT INTO family_members (family_id, name, age, member_type) 
                VALUES (%s, %s, %s, %s)
            """
            try:
                db.execute_query(
                    member_query,
                    (family_id, member.name, member.age, member.member_type)
                )
                logger.info(f"Member '{member.name}' added to family {family_id}")
            except Exception as e:
                logger.error(f"Error adding member '{member.name}': {e}")
                raise HTTPException(status_code=500, detail=f"Error adding member {member.name}: {str(e)}")

        # Crear progreso de ruta
        progress_query = """
            INSERT INTO family_route_progress (family_id, current_poi_index, points_earned)
            VALUES (%s, 0, 0)
        """
        try:
            db.execute_query(progress_query, (family_id,))
            logger.info(f"Route progress created for family {family_id}")
        except Exception as e:
            logger.warning(f"Could not create route progress for family {family_id}: {e}")
            # No fallar si no se puede crear el progreso

        result_query = """
            SELECT f.id, f.name, f.preferred_language, f.created_at,
                   json_agg(
                       json_build_object(
                           'name', fm.name,
                           'age', fm.age,
                           'member_type', fm.member_type
                       )
                   ) as members
            FROM families f
            LEFT JOIN family_members fm ON f.id = fm.family_id
            WHERE f.id = %s
            GROUP BY f.id
        """
        family = db.execute_query(result_query, (family_id,))

        return family[0] if family else None

    except Exception as e:
        logger.error(f"Error creando familia: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{family_id}", response_model=FamilyResponse)
async def get_family(family_id: int, db: Database = Depends(get_db)):
    """
    Obtener información de una familia
    """
    try:
        query = """
            SELECT f.id, f.name, f.preferred_language, f.created_at,
                   json_agg(
                       json_build_object(
                           'name', fm.name,
                           'age', fm.age,
                           'member_type', fm.member_type
                       )
                   ) as members
            FROM families f
            LEFT JOIN family_members fm ON f.id = fm.family_id
            WHERE f.id = %s
            GROUP BY f.id
        """
        result = db.execute_query(query, (family_id,))

        if not result:
            raise HTTPException(status_code=404, detail="Familia no encontrada")

        return result[0]

    except Exception as e:
        logger.error(f"Error obteniendo familia {family_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
