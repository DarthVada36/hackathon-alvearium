"""
Madrid Knowledge - Sistema de conocimiento sobre Madrid
Integrado con Pinecone para búsquedas vectoriales y Wikipedia para contenido dinámico
"""

from typing import Dict, Any, List, Optional
import logging
import requests
import os

# ============================
# Configuración
# ============================
USE_PINECONE = True  # ✅ Cambiado a True
WIKIPEDIA_API_URL = "https://es.wikipedia.org/api/rest_v1/page/summary/"

logger = logging.getLogger(__name__)

# Importar servicios
try:
    from Server.core.services.pinecone_service import pinecone_service
    logger.info("✅ Pinecone service importado correctamente")
except ImportError as e:
    logger.error(f"❌ Error importando pinecone_service: {e}")
    pinecone_service = None
    USE_PINECONE = False

# ============================
# POIs de la ruta (solo IDs y nombres)
# ============================
RATON_PEREZ_POIS = [
    {"id": "plaza_oriente", "name": "Plaza de Oriente"},
    {"id": "plaza_ramales", "name": "Plaza de Ramales"},
    {"id": "calle_vergara", "name": "Calle de Vergara"},
    {"id": "plaza_isabel_ii", "name": "Plaza de Isabel II"},
    {"id": "calle_arenal_1", "name": "Calle del Arenal"},
    {"id": "calle_bordadores", "name": "Calle de Bordadores"},
    {"id": "plazuela_san_gines", "name": "Plazuela de San Ginés"},
    {"id": "pasadizo_san_gines", "name": "Pasadizo de San Ginés"},
    {"id": "calle_arenal_2", "name": "Calle del Arenal"},
    {"id": "museo_raton_perez", "name": "Museo del Ratoncito Pérez"},
]

# Ubicaciones adicionales clásicas
CLASSIC_MADRID_POIS = [
    {"id": "plaza_mayor", "name": "Plaza Mayor"},
    {"id": "palacio_real", "name": "Palacio Real"},
    {"id": "puerta_del_sol", "name": "Puerta del Sol"},
    {"id": "mercado_san_miguel", "name": "Mercado de San Miguel"},
    {"id": "teatro_real", "name": "Teatro Real"},
]

ALL_POIS = RATON_PEREZ_POIS + CLASSIC_MADRID_POIS

# ============================
# Funciones de embedding
# ============================
def _get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Genera embeddings usando sentence-transformers
    """
    try:
        from sentence_transformers import SentenceTransformer
        
        # Usar el modelo configurado en el .env o uno por defecto
        model_name = os.getenv("PINECONE_EMBEDDING_MODEL", "intfloat/e5-large-v2")
        if model_name == "llama-text-embed-v2":
            # Si es el modelo de Llama, usar uno compatible con sentence-transformers
            model_name = "intfloat/e5-large-v2"
        
        model = SentenceTransformer(model_name)
        
        # Preparar textos con prefijo para e5
        prepared_texts = [f"passage: {text}" for text in texts]
        embeddings = model.encode(prepared_texts, normalize_embeddings=True)
        
        return embeddings.tolist()
    except Exception as e:
        logger.error(f"❌ Error generando embeddings: {e}")
        return []

def _get_query_embedding(query: str) -> List[float]:
    """
    Genera embedding para una consulta
    """
    try:
        from sentence_transformers import SentenceTransformer
        
        model_name = os.getenv("PINECONE_EMBEDDING_MODEL", "intfloat/e5-large-v2")
        if model_name == "llama-text-embed-v2":
            model_name = "intfloat/e5-large-v2"
        
        model = SentenceTransformer(model_name)
        
        # Prefijo para consultas
        prepared_query = f"query: {query}"
        embedding = model.encode([prepared_query], normalize_embeddings=True)
        
        return embedding[0].tolist()
    except Exception as e:
        logger.error(f"❌ Error generando embedding de consulta: {e}")
        return []

# ============================
# Funciones de Wikipedia
# ============================
def fetch_wikipedia_content(poi_name: str) -> Dict[str, str]:
    """
    Obtiene contenido de Wikipedia para un POI
    """
    try:
        # Limpiar nombre para URL
        clean_name = poi_name.replace(" ", "_")
        url = f"{WIKIPEDIA_API_URL}{clean_name}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "basic_info": data.get("extract", ""),
                "title": data.get("title", poi_name),
                "source_url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
            }
        else:
            logger.warning(f"⚠️ Wikipedia no encontró información para: {poi_name}")
            return {"basic_info": f"Información sobre {poi_name} no disponible en este momento."}
            
    except Exception as e:
        logger.error(f"❌ Error obteniendo datos de Wikipedia para {poi_name}: {e}")
        return {"basic_info": f"Información sobre {poi_name} no disponible temporalmente."}

# ============================
# Funciones principales
# ============================
def initialize_madrid_knowledge():
    """
    Inicializa la base de conocimiento obteniendo datos de Wikipedia y subiéndolos a Pinecone
    """
    if not USE_PINECONE or not pinecone_service or not pinecone_service.is_available():
        logger.warning("⚠️ Pinecone no disponible, usando modo offline")
        return False
    
    logger.info("🚀 Inicializando base de conocimiento de Madrid...")
    
    success_count = 0
    
    for poi in ALL_POIS:
        poi_id = poi["id"]
        poi_name = poi["name"]
        
        logger.info(f"📍 Procesando {poi_name}...")
        
        # Obtener contenido de Wikipedia
        wiki_content = fetch_wikipedia_content(poi_name)
        
        if wiki_content.get("basic_info"):
            # Generar embedding
            embeddings = _get_embeddings([wiki_content["basic_info"]])
            
            if embeddings:
                # Subir a Pinecone
                success = pinecone_service.upsert_madrid_content(
                    poi_id=poi_id,
                    content_type="basic_info",
                    text=wiki_content["basic_info"],
                    embedding=embeddings[0]
                )
                
                if success:
                    success_count += 1
                    logger.info(f"✅ {poi_name} subido a Pinecone")
                else:
                    logger.error(f"❌ Error subiendo {poi_name} a Pinecone")
            else:
                logger.error(f"❌ No se pudo generar embedding para {poi_name}")
        else:
            logger.warning(f"⚠️ No se obtuvo contenido para {poi_name}")
    
    logger.info(f"🎯 Inicialización completada: {success_count}/{len(ALL_POIS)} POIs procesados")
    return success_count > 0

def get_location_info(poi_id: str, info_type: str = "basic_info") -> str:
    """
    Obtiene información sobre una ubicación específica
    """
    if USE_PINECONE and pinecone_service and pinecone_service.is_available():
        # Buscar en Pinecone por POI específico
        dummy_query = f"información sobre {poi_id}"
        query_embedding = _get_query_embedding(dummy_query)
        
        if query_embedding:
            results = pinecone_service.search_madrid_content(
                query_embedding=query_embedding,
                poi_id=poi_id,
                content_type=info_type,
                top_k=1
            )
            
            if results and len(results) > 0:
                return results[0].get("metadata", {}).get("text", "Información no disponible")
    
    # Fallback: obtener directamente de Wikipedia
    poi_name = _get_poi_name_by_id(poi_id)
    if poi_name:
        wiki_content = fetch_wikipedia_content(poi_name)
        return wiki_content.get("basic_info", "Información no disponible en este momento.")
    
    return f"Lo siento, no tengo información específica sobre '{poi_id}' en este momento."

def search_madrid_content(query: str) -> str:
    """
    Busca contenido en toda la base de conocimiento usando búsqueda semántica
    """
    if USE_PINECONE and pinecone_service and pinecone_service.is_available():
        # Búsqueda semántica en Pinecone
        query_embedding = _get_query_embedding(query)
        
        if query_embedding:
            results = pinecone_service.search_madrid_content(
                query_embedding=query_embedding,
                top_k=3
            )
            
            if results:
                # Combinar resultados más relevantes
                combined_info = []
                for result in results:
                    metadata = result.get("metadata", {})
                    text = metadata.get("text", "")
                    poi_id = metadata.get("poi_id", "")
                    
                    if text and poi_id:
                        poi_name = _get_poi_name_by_id(poi_id)
                        combined_info.append(f"{poi_name}: {text[:200]}...")
                
                if combined_info:
                    return "\n\n".join(combined_info)
    
    # Fallback: búsqueda manual por palabras clave
    return _search_by_keywords(query)

def _search_by_keywords(query: str) -> str:
    """
    Búsqueda simple por palabras clave como fallback
    """
    query_lower = query.lower()
    
    # Mapeo de palabras clave a POIs
    keyword_mapping = {
        "plaza mayor": "plaza_mayor",
        "palacio real": "palacio_real",
        "palacio": "palacio_real",
        "puerta del sol": "puerta_del_sol",
        "sol": "puerta_del_sol",
        "oriente": "plaza_oriente",
        "teatro real": "teatro_real",
        "teatro": "teatro_real",
        "ratoncito pérez": "museo_raton_perez",
        "ratón": "museo_raton_perez",
        "san ginés": "plazuela_san_gines",
        "arenal": "calle_arenal_1",
    }
    
    # Buscar coincidencias
    for keyword, poi_id in keyword_mapping.items():
        if keyword in query_lower:
            return get_location_info(poi_id, "basic_info")
    
    # Respuesta genérica
    return ("Madrid es la capital de España con un rico patrimonio histórico. "
            "¿Te interesa algún lugar específico como la Plaza Mayor, el Palacio Real o la Puerta del Sol?")

# ============================
# Funciones auxiliares
# ============================
def _get_poi_name_by_id(poi_id: str) -> Optional[str]:
    """
    Obtiene el nombre de un POI por su ID
    """
    for poi in ALL_POIS:
        if poi["id"] == poi_id:
            return poi["name"]
    return None

def get_poi_stories(poi_id: str) -> str:
    """
    Obtiene historias específicas de un POI (placeholder por ahora)
    """
    poi_name = _get_poi_name_by_id(poi_id)
    if poi_name:
        return f"En {poi_name}, cuentan que los ratoncitos guardan secretos mágicos entre sus piedras..."
    return "No hay historias disponibles para este lugar."

def get_poi_curiosities(poi_id: str) -> str:
    """
    Obtiene curiosidades de un POI
    """
    return get_location_info(poi_id, "basic_info")  # Por ahora usamos la info básica

def get_available_locations() -> List[str]:
    """
    Devuelve lista de POIs disponibles
    """
    return [poi["id"] for poi in ALL_POIS]

def get_location_summary(poi_id: str) -> Dict[str, str]:
    """
    Obtiene un resumen de una ubicación
    """
    poi_name = _get_poi_name_by_id(poi_id)
    if not poi_name:
        return {"error": f"Ubicación '{poi_id}' no encontrada"}
    
    basic_info = get_location_info(poi_id, "basic_info")
    
    return {
        "name": poi_name,
        "basic_info": basic_info,
        "main_curiosity": basic_info[:100] + "..." if len(basic_info) > 100 else basic_info,
        "magical_story": get_poi_stories(poi_id),
    }

# ============================
# Inicialización automática
# ============================
def ensure_knowledge_initialized():
    """
    Asegura que la base de conocimiento esté inicializada para los 10 POIs de la ruta
    """
    if not USE_PINECONE:
        logger.info("📚 Modo offline: usando respuestas predefinidas")
        return True
    
    if not pinecone_service or not pinecone_service.is_available():
        logger.warning("⚠️ Pinecone no disponible")
        return False
    
    # Verificar si ya hay datos en Pinecone
    try:
        stats = pinecone_service.get_index_stats()
        vector_count = stats.get("total_vector_count", 0)
        
        if vector_count == 0:
            logger.info("📊 Pinecone vacío, inicializando 10 POIs de la ruta...")
            return initialize_madrid_knowledge()
        elif vector_count < 10:
            logger.info(f"📊 Pinecone tiene {vector_count} vectores, completando hasta 10...")
            return initialize_madrid_knowledge()
        else:
            logger.info(f"📊 Pinecone ya tiene {vector_count} vectores (≥10 POIs)")
            return True
    except Exception as e:
        logger.error(f"❌ Error verificando estado de Pinecone: {e}")
        return False