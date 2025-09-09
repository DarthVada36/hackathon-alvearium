from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging
import json
from datetime import datetime

from core.models.database import Database
from api.dependencies import get_db
from core.agents.raton_perez import RatonPerezAgent

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

# Schemas para request/response
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="Mensaje del usuario")
    location: Optional[Dict[str, float]] = Field(None, description="Ubicación actual (lat, lng)")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Respuesta del Ratoncito Pérez")
    suggestions: Optional[list[str]] = Field(None, description="Sugerencias de seguimiento")
    location_actions: Optional[Dict[str, Any]] = Field(None, description="Acciones relacionadas con ubicación")
    points_awarded: Optional[int] = Field(0, description="Puntos otorgados en esta interacción")
    context_updated: bool = Field(True, description="Si se actualizó el contexto conversacional")

# Inicializar el agente de chat
chat_agent = RatonPerezAgent()

@router.post("/{family_id}", response_model=ChatResponse)
async def chat_with_raton_perez(
    family_id: int,
    chat_request: ChatRequest,
    db: Database = Depends(get_db)
):
    """
    ENDPOINT PRINCIPAL: Conversación con el Ratoncito Pérez
    
    Este es el endpoint central del agente. Maneja:
    - Conversación contextual
    - Integración con ubicación
    - Sistema de puntos
    - Recomendaciones personalizadas
    """
    try:
        # Verificar que la familia existe
        family_result = db.execute_query(
            "SELECT id, preferred_language, conversation_context FROM families WHERE id = %s",
            (family_id,)
        )
        
        if not family_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Familia no encontrada"
            )
        
        family_data = family_result[0]
        preferred_language = family_data.get('preferred_language', 'es')
        conversation_context = family_data.get('conversation_context', {})
        
        # Obtener información de miembros de la familia para personalización
        members_result = db.execute_query(
            "SELECT name, age, member_type FROM family_members WHERE family_id = %s",
            (family_id,)
        )
        
        family_members = members_result if members_result else []
        
        # Obtener ruta activa si existe
        active_route_result = db.execute_query("""
            SELECT frp.*, r.name as route_name, r.pois 
            FROM family_route_progress frp
            JOIN routes r ON frp.route_id = r.id
            WHERE frp.family_id = %s AND frp.completed_at IS NULL
            ORDER BY frp.started_at DESC
            LIMIT 1
        """, (family_id,))
        
        active_route = active_route_result[0] if active_route_result else None
        
        # Preparar contexto completo para el agente
        full_context = {
            "family_id": family_id,
            "preferred_language": preferred_language,
            "family_members": family_members,
            "conversation_history": conversation_context.get('messages', []),
            "current_location": chat_request.location,
            "active_route": active_route,
            "user_context": chat_request.context or {}
        }
        
        # Generar respuesta usando el agente
        agent_response = chat_agent.generate_response(
            message=chat_request.message,
            context=full_context
        )
        
        # Actualizar contexto conversacional
        updated_context = conversation_context.copy()
        if 'messages' not in updated_context:
            updated_context['messages'] = []
        
        # Limitar historial a últimas 20 interacciones
        updated_context['messages'] = updated_context['messages'][-19:] + [
            {
                "user": chat_request.message,
                "assistant": agent_response.get('response', ''),
                "timestamp": datetime.now().isoformat(),
                "location": chat_request.location,
                "points_awarded": agent_response.get('points_awarded', 0)
            }
        ]
        
        # Guardar contexto actualizado
        db.execute_query(
            "UPDATE families SET conversation_context = %s WHERE id = %s",
            (json.dumps(updated_context), family_id)
        )
        
        # Actualizar puntos si se otorgaron
        points_awarded = agent_response.get('points_awarded', 0)
        if points_awarded > 0 and active_route:
            db.execute_query(
                "UPDATE family_route_progress SET points_earned = points_earned + %s WHERE id = %s",
                (points_awarded, active_route['id'])
            )
        
        # Actualizar ubicación si se proporcionó
        if chat_request.location and active_route:
            db.execute_query(
                "UPDATE family_route_progress SET current_location = %s WHERE id = %s",
                (json.dumps(chat_request.location), active_route['id'])
            )
            
            # Agregar actualización de ubicación al historial
            db.execute_query(
                "INSERT INTO location_updates (family_route_progress_id, location) VALUES (%s, %s)",
                (active_route['id'], json.dumps(chat_request.location))
            )
        
        return ChatResponse(
            response=agent_response.get('response', 'Lo siento, no pude procesar tu mensaje.'),
            suggestions=agent_response.get('suggestions', []),
            location_actions=agent_response.get('location_actions'),
            points_awarded=points_awarded,
            context_updated=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en chat con familia {family_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="El Ratoncito Pérez tuvo un problemita técnico. ¡Inténtalo de nuevo!"
        )

@router.get("/{family_id}/history")
async def get_chat_history(
    family_id: int, 
    limit: int = 10,
    db: Database = Depends(get_db)
):
    """Obtener historial de conversación"""
    try:
        result = db.execute_query(
            "SELECT conversation_context FROM families WHERE id = %s",
            (family_id,)
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Familia no encontrada"
            )
        
        context = result[0].get('conversation_context', {})
        messages = context.get('messages', [])
        
        # Devolver últimos N mensajes
        return {
            "messages": messages[-limit:] if limit > 0 else messages,
            "total_messages": len(messages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo historial de familia {family_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el historial de conversación"
        )

@router.delete("/{family_id}/history")
async def clear_chat_history(family_id: int, db: Database = Depends(get_db)):
    """Limpiar historial de conversación"""
    try:
        result = db.execute_query(
            "UPDATE families SET conversation_context = '{}' WHERE id = %s RETURNING id",
            (family_id,)
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Familia no encontrada"
            )
        
        return {"message": "Historial de conversación eliminado correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error limpiando historial de familia {family_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al limpiar el historial de conversación"
        )