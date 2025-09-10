from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from Server.core.models.schemas import ChatMessage, ChatResponse
from Server.core.agents.raton_perez import process_chat_message, get_family_status as get_family_status_service
from Server.core.models.database import Database
from Server.api.dependencies import get_db

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

@router.post("/message", response_model=ChatResponse)
async def chat_endpoint(chat_data: ChatMessage, db: Database = Depends(get_db)):
    """
    Endpoint para enviar mensajes al Ratoncito Pérez
    """
    try:
        result = await process_chat_message(
            family_id=chat_data.family_id,
            message=chat_data.message,
            location=chat_data.location,
            speaker_name=chat_data.speaker_name,
            db=db
        )
        return result
    except Exception as e:
        logger.error(f"Error en endpoint chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/family/{family_id}/status")
async def get_family_status(family_id: int, db: Database = Depends(get_db)):
    """
    Obtener estado y progreso de una familia
    """
    try:
        result = await get_family_status_service(family_id, db)
        return result
    except Exception as e:
        logger.error(f"Error obteniendo estado de familia {family_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
