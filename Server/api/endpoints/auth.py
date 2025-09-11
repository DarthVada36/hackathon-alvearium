"""
Endpoints de Autenticación para el Ratoncito Pérez
Registro, login, perfil de usuario
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any
import logging
from datetime import datetime

from Server.core.models.database import Database
from Server.api.dependencies import get_db
from Server.core.security.auth import auth_manager
from Server.core.security.dependencies import get_current_user, AuthenticatedUser

# Schemas para autenticación
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

logger = logging.getLogger(__name__)

# ✅ ESTA LÍNEA ES CRUCIAL - DEFINE EL ROUTER
router = APIRouter(prefix="/auth", tags=["authentication"])

# ========================
# SCHEMAS LOCALES
# ========================

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Mínimo 6 caracteres")
    avatar: Optional[str] = "icon1"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    avatar: str
    created_at: datetime
    last_login: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserProfileComplete(BaseModel):
    user: UserResponse
    families: List[Dict[str, Any]]
    total_points: int
    total_families: int

# ========================
# ENDPOINTS
# ========================

@router.post("/register", response_model=Token)
async def register_user(user_data: UserRegister, db: Database = Depends(get_db)):
    """
    Registrar nuevo usuario
    """
    try:
        # Verificar si el email ya existe
        email_check_query = "SELECT id FROM users WHERE email = %s"
        existing_user = db.execute_query(email_check_query, (user_data.email,))
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Hash de la contraseña
        hashed_password = auth_manager.hash_password(user_data.password)
        
        # Crear usuario en la base de datos
        create_user_query = """
            INSERT INTO users (email, hashed_password, avatar, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id, email, avatar, created_at
        """
        
        user_result = db.execute_query(
            create_user_query,
            (user_data.email, hashed_password, user_data.avatar, datetime.utcnow())
        )
        
        if not user_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creando usuario"
            )
        
        new_user = user_result[0]
        
        # Crear token JWT
        access_token = auth_manager.create_user_token(new_user["id"], new_user["email"])
        
        # Actualizar last_login
        update_login_query = "UPDATE users SET last_login = %s WHERE id = %s"
        db.execute_query(update_login_query, (datetime.utcnow(), new_user["id"]))
        
        # Respuesta
        user_response = UserResponse(
            id=new_user["id"],
            email=new_user["email"],
            avatar=new_user["avatar"],
            created_at=new_user["created_at"],
            last_login=datetime.utcnow()
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en registro de usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Database = Depends(get_db)):
    """
    Login de usuario existente
    """
    try:
        # Buscar usuario por email
        user_query = """
            SELECT id, email, hashed_password, avatar, created_at, last_login
            FROM users 
            WHERE email = %s AND is_active = true
        """
        
        user_result = db.execute_query(user_query, (user_credentials.email,))
        
        if not user_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = user_result[0]
        
        # Verificar contraseña
        if not auth_manager.verify_password(user_credentials.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Crear token JWT
        access_token = auth_manager.create_user_token(user["id"], user["email"])
        
        # Actualizar last_login
        update_login_query = "UPDATE users SET last_login = %s WHERE id = %s"
        db.execute_query(update_login_query, (datetime.utcnow(), user["id"]))
        
        # Respuesta
        user_response = UserResponse(
            id=user["id"],
            email=user["email"],
            avatar=user["avatar"],
            created_at=user["created_at"],
            last_login=datetime.utcnow()
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/me", response_model=UserProfileComplete)
async def get_current_user_profile(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    Obtener perfil completo del usuario actual
    """
    try:
        # Obtener datos del usuario
        user_query = """
            SELECT id, email, avatar, created_at, last_login
            FROM users 
            WHERE id = %s
        """
        user_result = db.execute_query(user_query, (current_user.id,))
        
        if not user_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        user_data = user_result[0]
        
        # Obtener familias del usuario
        families_query = """
            SELECT f.id, f.name, f.preferred_language, f.created_at,
                   frp.points_earned,
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
            GROUP BY f.id, f.name, f.preferred_language, f.created_at, frp.points_earned
            ORDER BY f.created_at DESC
        """
        
        families_result = db.execute_query(families_query, (current_user.id,))
        
        # Calcular estadísticas
        total_points = sum(family.get("points_earned", 0) or 0 for family in families_result)
        total_families = len(families_result)
        
        # Formatear respuesta
        user_response = UserResponse(
            id=user_data["id"],
            email=user_data["email"],
            avatar=user_data["avatar"],
            created_at=user_data["created_at"],
            last_login=user_data["last_login"]
        )
        
        return UserProfileComplete(
            user=user_response,
            families=families_result or [],
            total_points=total_points,
            total_families=total_families
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo perfil de usuario {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/logout")
async def logout_user(current_user: AuthenticatedUser = Depends(get_current_user)):
    """
    Logout del usuario (invalidar token en el frontend)
    """
    # En JWT stateless, el logout se maneja en el frontend eliminando el token
    # Aquí podríamos registrar el evento o actualizar last_login
    return {
        "message": "Logout exitoso",
        "user_id": current_user.id
    }

@router.put("/profile")
async def update_user_profile(
    avatar: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    Actualizar perfil del usuario (solo avatar por ahora)
    """
    try:
        # Validar avatar
        valid_avatars = ["icon1", "icon2", "icon3", "icon4", "icon5", "icon6"]
        if avatar not in valid_avatars:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Avatar inválido. Opciones válidas: {valid_avatars}"
            )
        
        # Actualizar avatar
        update_query = "UPDATE users SET avatar = %s WHERE id = %s"
        db.execute_query(update_query, (avatar, current_user.id))
        
        return {
            "message": "Perfil actualizado exitosamente",
            "avatar": avatar
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando perfil de usuario {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/ping")
def ping():
    """
    Health check del servicio de autenticación
    """
    return {"service": "auth", "ok": True}