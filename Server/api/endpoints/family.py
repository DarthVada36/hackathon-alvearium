from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from Server.core.models.database import Database
from Server.api.dependencies import get_db
from Server.core.models.schemas import FamilyCreate, FamilyResponse
from Server.core.security.dependencies import get_current_user, AuthenticatedUser, require_family_ownership

router = APIRouter(prefix="/families", tags=["families"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=FamilyResponse)
async def create_family(
    family_data: FamilyCreate, 
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    Crear una nueva familia (requiere autenticación)
    """
    try:
        # Insertar familia asociada al usuario autenticado
        family_query = """
            INSERT INTO families (user_id, name, preferred_language)
            VALUES (%s, %s, %s)
            RETURNING id, name, preferred_language, created_at
        """
        family_result = db.execute_query(
            family_query, 
            (current_user.id, family_data.name, family_data.preferred_language)  # user_id del token
        )
        
        if not family_result:
            raise HTTPException(status_code=500, detail="Error creando familia")
        
        family_id = family_result[0]['id']
        
        # Insertar miembros
        members_queries = []
        for member in family_data.members:
            members_queries.append((
                "INSERT INTO family_members (family_id, name, age, member_type) VALUES (%s, %s, %s, %s)",
                (family_id, member.name, member.age, member.member_type)
            ))
        
        db.execute_transaction(members_queries)
        
        # Crear registro de progreso
        progress_query = """
            INSERT INTO family_route_progress (family_id, current_poi_index, points_earned)
            VALUES (%s, 0, 0)
        """
        db.execute_query(progress_query, (family_id,))
        
        # Obtener familia creada con miembros
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
        
        logger.info(f"✅ Familia creada: {family_data.name} por usuario {current_user.id}")
        return family[0] if family else None
        
    except Exception as e:
        logger.error(f"Error creando familia: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{family_id}", response_model=FamilyResponse)
async def get_family(
    family_id: int, 
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    Obtener información de una familia (solo el propietario)
    """
    try:
        # Verificar que la familia pertenece al usuario actual
        require_family_ownership(family_id, current_user, db)
        
        # Obtener familia con miembros
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
            WHERE f.id = %s AND f.user_id = %s
            GROUP BY f.id
        """
        result = db.execute_query(query, (family_id, current_user.id))
        
        if not result:
            raise HTTPException(status_code=404, detail="Familia no encontrada")
        
        return result[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo familia {family_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_user_families(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    Listar todas las familias del usuario autenticado
    
    Este endpoint requiere autenticación. Si no hay token válido,
    get_current_user lanzará HTTPException con código 401.
    """
    try:
        # Si llegamos aquí, el usuario está correctamente autenticado
        query = """
            SELECT f.id, f.name, f.preferred_language, f.created_at,
                   frp.points_earned,
                   frp.current_poi_index,
                   json_agg(
                       json_build_object(
                           'name', fm.name,
                           'age', fm.age,
                           'member_type', fm.member_type
                       )
                   ) as members
            FROM families f
            LEFT JOIN family_members fm ON f.id = fm.family_id
            LEFT JOIN family_route_progress frp ON f.id = frp.family_id
            WHERE f.user_id = %s
            GROUP BY f.id, f.name, f.preferred_language, f.created_at, frp.points_earned, frp.current_poi_index
            ORDER BY f.created_at DESC
        """
        
        families = db.execute_query(query, (current_user.id,))
        
        # Calcular estadísticas del usuario
        total_points = sum(family.get("points_earned", 0) or 0 for family in families or [])
        total_families = len(families or [])
        
        return {
            "families": families or [],
            "total_families": total_families,
            "total_points": total_points,
            "user_id": current_user.id
        }
        
    except HTTPException:
        # Re-lanzar excepciones HTTP (como 401 de get_current_user)
        raise
    except Exception as e:
        logger.error(f"Error obteniendo familias del usuario {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{family_id}")
async def delete_family(
    family_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    Eliminar una familia (solo el propietario)
    """
    try:
        # Verificar que la familia pertenece al usuario actual
        require_family_ownership(family_id, current_user, db)
        
        # Eliminar familia (CASCADE eliminará miembros y progreso automáticamente)
        delete_query = "DELETE FROM families WHERE id = %s AND user_id = %s"
        db.execute_query(delete_query, (family_id, current_user.id))
        
        logger.info(f"✅ Familia {family_id} eliminada por usuario {current_user.id}")
        return {"message": "Familia eliminada exitosamente", "family_id": family_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando familia {family_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))