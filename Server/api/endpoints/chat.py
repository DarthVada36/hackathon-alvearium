from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from Server.core.models.schemas import ChatMessage, ChatResponse
from Server.core.agents.raton_perez import process_chat_message, get_family_status as get_family_status_service
from Server.core.models.database import Database
from Server.api.dependencies import get_db
from Server.core.security.dependencies import get_current_user, AuthenticatedUser, require_family_ownership

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

@router.post("/message", response_model=ChatResponse)
async def chat_endpoint(
    chat_data: ChatMessage, 
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    Endpoint principal para enviar mensajes al Ratoncito Pérez (requiere autenticación)
    """
    try:
        # Verificar que la familia pertenece al usuario autenticado
        require_family_ownership(chat_data.family_id, current_user, db)
        
        # Procesar mensaje del chat
        result = await process_chat_message(
            family_id=chat_data.family_id,
            message=chat_data.message,
            location=chat_data.location,
            speaker_name=chat_data.speaker_name,
            db=db
        )
        
        logger.info(f"✅ Chat procesado para familia {chat_data.family_id} de usuario {current_user.id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en endpoint chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/family/{family_id}/status")
async def get_family_status(
    family_id: int, 
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    Obtener estado y progreso de una familia (solo el propietario)
    """
    try:
        # Verificar que la familia pertenece al usuario autenticado
        require_family_ownership(family_id, current_user, db)
        
        # Obtener estado de la familia
        result = await get_family_status_service(family_id, db)
        
        # Agregar información del usuario propietario
        result["user_id"] = current_user.id
        result["user_email"] = current_user.email
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estado de familia {family_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/families")
async def get_user_chat_families(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    Obtener lista de familias del usuario para el chat
    """
    try:
        query = """
            SELECT f.id, f.name, f.preferred_language,
                   frp.points_earned, frp.current_poi_index,
                   COUNT(fm.id) as member_count
            FROM families f
            LEFT JOIN family_route_progress frp ON f.id = frp.family_id
            LEFT JOIN family_members fm ON f.id = fm.family_id
            WHERE f.user_id = %s
            GROUP BY f.id, f.name, f.preferred_language, frp.points_earned, frp.current_poi_index
            ORDER BY f.created_at DESC
        """
        
        families = db.execute_query(query, (current_user.id,))
        
        return {
            "families": families or [],
            "total_families": len(families or []),
            "user_id": current_user.id
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo familias para chat del usuario {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/family/{family_id}/history")
async def get_chat_history(
    family_id: int,
    limit: int = 20,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    Obtener historial de conversaciones de una familia
    """
    try:
        # Verificar que la familia pertenece al usuario autenticado
        require_family_ownership(family_id, current_user, db)
        
        # Obtener el contexto de conversación de la familia
        query = """
            SELECT conversation_context
            FROM families 
            WHERE id = %s AND user_id = %s
        """
        result = db.execute_query(query, (family_id, current_user.id))
        
        if not result:
            raise HTTPException(status_code=404, detail="Familia no encontrada")
        
        conversation_context = result[0].get("conversation_context", {})
        
        # Extraer historial de mensajes
        if isinstance(conversation_context, str):
            import json
            try:
                conversation_context = json.loads(conversation_context)
            except:
                conversation_context = {}
        
        history = conversation_context.get("memory", [])
        
        # Limitar número de mensajes
        recent_history = history[-limit:] if history else []
        
        return {
            "family_id": family_id,
            "messages": recent_history,
            "total_messages": len(history),
            "showing": len(recent_history)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo historial de familia {family_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/family/{family_id}/history")
async def clear_chat_history(
    family_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    Limpiar historial de conversaciones de una familia
    """
    try:
        # Verificar que la familia pertenece al usuario autenticado
        require_family_ownership(family_id, current_user, db)
        
        # Limpiar contexto de conversación
        update_query = """
            UPDATE families 
            SET conversation_context = '{}'::jsonb
            WHERE id = %s AND user_id = %s
        """
        db.execute_query(update_query, (family_id, current_user.id))
        
        logger.info(f"✅ Historial limpiado para familia {family_id} de usuario {current_user.id}")
        return {
            "message": "Historial de conversación limpiado exitosamente",
            "family_id": family_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error limpiando historial de familia {family_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ping")
def ping():
    """
    Health check del servicio de chat
    """
    return {"service": "chat", "ok": True}