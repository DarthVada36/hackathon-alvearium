from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Load .env if available (optional)
try:  # pragma: no cover
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    pass

# Import health status from pinecone service
try:
    from Server.core.services.pinecone_service import pinecone_service
except Exception:
    pinecone_service = None

app = FastAPI(title="ratoncito API", version=os.getenv("APP_VERSION", "0.1.0"))

# Basic CORS for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
try:
    from Server.api.endpoints.chat import router as chat_router
    from Server.api.endpoints.family import router as family_router
    from Server.api.endpoints.routes import router as routes_router
    from Server.api.endpoints.debug import router as debug_router

    app.include_router(chat_router)
    app.include_router(family_router)
    app.include_router(routes_router)
    app.include_router(debug_router)
except Exception:
    # Routers are optional during bootstrap; keep app running even if not available
    pass

@app.get("/")
def read_root():
    return {"message": "ratoncito API up"}

@app.get("/healthz")
def healthz():
    status = {"pinecone": None, "redis": None}
    if pinecone_service is not None:
        try:
            status["pinecone"] = pinecone_service.get_status()
        except Exception as e:
            status["pinecone"] = {"error": str(e)}
    else:
        status["pinecone"] = {"available": False, "reason": "service not imported"}

    # Redis health (optional)
    try:
        import redis  # type: ignore

        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            client = redis.StrictRedis.from_url(redis_url, socket_connect_timeout=0.25, socket_timeout=0.25)
            ok = bool(client.ping())
            status["redis"] = {"available": ok, "url": redis_url}
        else:
            status["redis"] = {"available": False, "reason": "REDIS_URL not set"}
    except Exception as e:  # pragma: no cover - best effort
        status["redis"] = {"available": False, "error": str(e)}
    return {"status": "ok", **status}


@app.get("/_routes")
def list_routes():
    # Handy discovery endpoint for local testing
    routes = []
    for r in app.router.routes:
        methods = getattr(r, "methods", None)
        path = getattr(r, "path", None)
        name = getattr(r, "name", None)
        include = getattr(r, "include_in_schema", True)
        if path:
            routes.append({
                "path": path,
                "name": name,
                "methods": sorted(list(methods)) if methods else [],
                "include_in_schema": include,
            })
    return {"count": len(routes), "routes": routes}
