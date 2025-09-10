from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import uvicorn

from Server.api.endpoints import chat, routes, family
from core.models.database import Database
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
    app.state.db = db  # 🔑 Guardar en app.state para que las dependencias puedan usarla

    # Inicializar agente
    global raton_perez
    raton_perez = RatonPerez(db)
    logger.info("✅ Ratoncito Pérez inicializado (con base de datos real)")

    # Verificar tablas
    required_tables = ['users', 'families', 'family_members', 'routes',
                       'family_route_progress', 'location_updates']
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
        else:
            logger.info("⚠️ Solo API Supabase disponible, omitiendo verificación directa")
    except Exception as e:
        logger.error(f"Error verificando esquema: {e}")

    yield

    logger.info("Cerrando aplicación...")
    if db:
        db.close()

app = FastAPI(
    title="Ratoncito Pérez Digital API",
    description="API para el agente turístico virtual Ratoncito Pérez",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(family.router, prefix="/api")
app.include_router(routes.router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "¡Hola! Soy el Ratoncito Pérez Digital 🐭",
        "description": "API para experiencias turísticas familiares en Madrid",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "families": "/api/families",
            "routes": "/api/routes",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check(request: Request):
    db = getattr(request.app.state, "db", None)
    status = {
        "status": "healthy",
        "database": "connected" if db and db.health_check() else "disconnected"
    }
    if status["database"] == "disconnected":
        status["status"] = "unhealthy"
    return status

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint no encontrado",
            "message": "El Ratoncito Pérez no puede encontrar lo que buscas 🐭",
            "suggestion": "Visita /docs para ver todos los endpoints disponibles"
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
    uvicorn.run("Server.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
