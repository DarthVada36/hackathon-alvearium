from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import uvicorn

# Importar routers de los endpoints
from api.endpoints import chat, routes, family
from core.models.database import Database

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar base de datos global
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionar el ciclo de vida de la aplicación"""
    global db
    
    # Startup
    logger.info("Iniciando aplicación Ratoncito Pérez Digital...")
    
    # Inicializar conexión a base de datos
    db = Database(use_pooler=False)
    
    # Verificar conexión
    if not db.health_check():
        logger.error("Error: No se puede conectar a la base de datos")
        raise RuntimeError("Database connection failed")
    
    logger.info("✅ Base de datos conectada correctamente")
    
    # Verificar esquema de base de datos
    required_tables = ['users', 'families', 'family_members', 'routes', 'family_route_progress', 'location_updates']
    
    try:
        result = db.execute_query("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = ANY(%s)
        """, (required_tables,))
        
        existing_tables = [row['table_name'] for row in result] if result else []
        missing_tables = set(required_tables) - set(existing_tables)
        
        if missing_tables:
            logger.warning(f"⚠️ Tablas faltantes: {list(missing_tables)}")
        else:
            logger.info("✅ Todas las tablas requeridas están presentes")
            
    except Exception as e:
        logger.error(f"Error verificando esquema: {e}")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")
    if db:
        db.close()

# Crear aplicación FastAPI
app = FastAPI(
    title="Ratoncito Pérez Digital API",
    description="API para el agente turístico virtual Ratoncito Pérez",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(chat.router, prefix="/api")
app.include_router(family.router, prefix="/api")
app.include_router(routes.router, prefix="/api")

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
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
async def health_check():
    """Verificar estado de la aplicación y servicios"""
    global db
    
    health_status = {
        "status": "healthy",
        "database": "disconnected",
        "services": {
            "groq": "unknown",
            "pinecone": "unknown"
        }
    }
    
    # Verificar base de datos
    if db and db.health_check():
        health_status["database"] = "connected"
    else:
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
    
    # TODO: Verificar otros servicios cuando estén implementados
    
    return health_status

# Manejadores de errores globales
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Endpoint no encontrado",
        "message": "El Ratoncito Pérez no puede encontrar lo que buscas 🐭",
        "suggestion": "Visita /docs para ver todos los endpoints disponibles"
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Error interno del servidor: {exc}")
    return {
        "error": "Error interno del servidor",
        "message": "¡Oops! El Ratoncito Pérez tuvo un problemita técnico 🐭",
        "suggestion": "Intenta de nuevo en unos momentos"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )