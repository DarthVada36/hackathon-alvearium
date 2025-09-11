from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import uvicorn
import os

# Load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from Server.api.endpoints import chat, routes, family, debug, auth
from Server.core.models.database import Database
from Server.core.agents.raton_perez import raton_perez, RatonPerez

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicación Ratoncito Pérez Digital...")

    # Iniciar DB y guardarla en app.state
    db = Database()
    if not db.health_check():
        logger.error("Error: No se puede conectar a la base de datos")
        raise RuntimeError("Database connection failed")

    logger.info("✅ Base de datos conectada correctamente")
    app.state.db = db

    # Inicializar agente
    global raton_perez
    raton_perez = RatonPerez(db)
    logger.info("✅ Ratoncito Pérez inicializado (con base de datos real)")

    # Verificar tablas (actualizado con nuevas tablas de auth)
    required_tables = ['users', 'families', 'family_members', 'family_route_progress']
    try:
        if db.connection:
            result = db.execute_query("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name = ANY(%s)
            """, (required_tables,))
            existing = [r['table_name'] for r in result] if result else []
            missing = set(required_tables) - set(existing)
            if missing:
                logger.warning(f"⚠️ Tablas faltantes: {list(missing)}")
            else:
                logger.info("✅ Todas las tablas requeridas están presentes")
                
            # Verificar columna is_active en users
            users_check = db.execute_query("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'is_active'
            """)
            if not users_check:
                logger.warning("⚠️ Columna 'is_active' faltante en tabla 'users'")
            else:
                logger.info("✅ Columna 'is_active' presente en tabla 'users'")
                
        else:
            logger.info("⚠️ Solo API Supabase disponible, omitiendo verificación directa")
    except Exception as e:
        logger.error(f"Error verificando esquema: {e}")

    yield

    logger.info("Cerrando aplicación...")
    if db:
        db.close()

# Crear aplicación principal
app = FastAPI(
    title="Ratoncito Pérez Digital API",
    description="API para el agente turístico virtual Ratoncito Pérez",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS C
app.include_router(auth.router, prefix="/api")    
app.include_router(chat.router, prefix="/api")
app.include_router(family.router, prefix="/api")
app.include_router(routes.router, prefix="/api")
app.include_router(debug.router)  # Debug sin prefijo para compatibilidad

# Endpoints principales
@app.get("/")
async def root():
    return {
        "message": "¡Hola! Soy el Ratoncito Pérez Digital 🐭",
        "description": "API para experiencias turísticas familiares en Madrid",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "auth": "/api/auth",       
            "chat": "/api/chat",
            "families": "/api/families",
            "routes": "/api/routes",
            "debug": "/debug",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check(request: Request):
    """Health check principal con formato estándar"""
    db = getattr(request.app.state, "db", None)
    status = {
        "status": "healthy",
        "database": "connected" if db and db.health_check() else "disconnected",
        "timestamp": int(__import__('time').time())
    }
    if status["database"] == "disconnected":
        status["status"] = "unhealthy"
    return status

@app.get("/healthz")
def healthz():
    """Health check adicional con información de servicios"""
    status = {"status": "ok"}
    
    # JWT Auth health check
    try:
        from Server.core.security.auth import auth_manager
        # Test básico del sistema de auth
        test_token = auth_manager.create_user_token(1, "test@test.com")
        token_valid = auth_manager.verify_token(test_token) is not None
        status["auth"] = {"available": token_valid, "jwt_working": True}
    except Exception as e:
        status["auth"] = {"available": False, "error": str(e)}
    
    # Pinecone health
    try:
        from Server.core.services.pinecone_service import pinecone_service
        if pinecone_service is not None:
            status["pinecone"] = pinecone_service.get_status()
        else:
            status["pinecone"] = {"available": False, "reason": "service not imported"}
    except Exception as e:
        status["pinecone"] = {"available": False, "error": str(e)}

    # Redis health
    try:
        import redis
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            client = redis.StrictRedis.from_url(redis_url, socket_connect_timeout=0.25, socket_timeout=0.25)
            ok = bool(client.ping())
            status["redis"] = {"available": ok, "url": redis_url}
        else:
            status["redis"] = {"available": False, "reason": "REDIS_URL not set"}
    except Exception as e:
        status["redis"] = {"available": False, "error": str(e)}
    
    return status

@app.get("/_routes")
def list_routes():
    """Endpoint de descubrimiento para debugging"""
    routes = []
    for route in app.router.routes:
        methods = getattr(route, "methods", None)
        path = getattr(route, "path", None)
        name = getattr(route, "name", None)
        include = getattr(route, "include_in_schema", True)
        if path:
            routes.append({
                "path": path,
                "name": name,
                "methods": sorted(list(methods)) if methods else [],
                "include_in_schema": include,
            })
    return {"count": len(routes), "routes": routes}

# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint no encontrado",
            "message": "El Ratoncito Pérez no puede encontrar lo que buscas 🐭",
            "suggestion": "Visita /docs para ver todos los endpoints disponibles",
            "available_endpoints": [
                "/health", 
                "/api/auth/register", "/api/auth/login",   
                "/api/chat/message", "/api/families/", 
                "/api/routes/overview", "/debug/ping"
            ]
        },
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Error interno del servidor: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "message": "¡Oops! El Ratoncito Pérez tuvo un problemita técnico 🐭",
            "suggestion": "Intenta de nuevo en unos momentos"
        },
    )

if __name__ == "__main__":
    # EJECUTAR DESDE RAÍZ
    uvicorn.run("Server.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")