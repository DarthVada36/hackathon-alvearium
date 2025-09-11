"""
Dependencias de Autenticación para FastAPI
Middleware y decoradores para proteger rutas
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from Server.core.security.auth import auth_manager
from Server.core.models.database import Database
from Server.api.dependencies import get_db

logger = logging.getLogger(__name__)

# Esquema de seguridad Bearer Token
security = HTTPBearer()

class AuthenticatedUser:
    """Clase para representar un usuario autenticado"""
    def __init__(self, user_id: int, email: str, avatar: str = "icon1"):
        self.id = user_id
        self.email = email
        self.avatar = avatar

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Database = Depends(get_db)
) -> AuthenticatedUser:
    """
    Dependencia para obtener el usuario actual desde el token JWT
    Úsala en endpoints que requieren autenticación
    """
    
    # Extraer token del header Authorization
    token = credentials.credentials
    
    # Verificar token
    token_data = auth_manager.verify_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = int(token_data["user_id"])
    
    # Verificar que el usuario existe en la base de datos
    try:
        user_query = "SELECT id, email, avatar FROM users WHERE id = %s AND is_active = true"
        user_result = db.execute_query(user_query, (user_id,))
        
        if not user_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado o inactivo",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_data = user_result[0]
        return AuthenticatedUser(
            user_id=user_data["id"],
            email=user_data["email"],
            avatar=user_data.get("avatar", "icon1")
        )
        
    except Exception as e:
        logger.error(f"Error verificando usuario {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Database = Depends(get_db)
) -> Optional[AuthenticatedUser]:
    """
    Dependencia para endpoints que pueden funcionar con o sin autenticación
    Retorna None si no hay token válido
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

def require_family_ownership(family_id: int, current_user: AuthenticatedUser, db: Database) -> bool:
    """
    Verificar que el usuario actual es propietario de la familia
    """
    try:
        family_query = "SELECT user_id FROM families WHERE id = %s"
        family_result = db.execute_query(family_query, (family_id,))
        
        if not family_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Familia no encontrada"
            )
        
        family_user_id = family_result[0]["user_id"]
        
        if family_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a esta familia"
            )
        
        return True
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verificando propiedad de familia {family_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )