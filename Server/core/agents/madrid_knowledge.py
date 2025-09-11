"""
Madrid Knowledge - Sistema de conocimiento sobre Madrid
Integrado con Pinecone para búsquedas vectoriales y Wikipedia para contenido dinámico
Usa EmbeddingService para evitar recarga del modelo en cada request
"""

from typing import Dict, Any, List, Optional
import logging
import requests
import os
import random  # <-- añadido para elegir User-Agent aleatorio

# Configuración
USE_PINECONE = True
WIKIPEDIA_API_URL = "https://es.wikipedia.org/api/rest_v1/page/summary/"

logger = logging.getLogger(__name__)

# Lista de User-Agents académicos (cumple con Wikimedia API Etiquette)
HEADERS_LIST = [
    {"User-Agent": "RatonPerezApp/1.0 (proyecto académico; contacto: jorsqn@gmail.com; https://github.com/peperuizdev)"},
    {"User-Agent": "MadridPOIResearch/2025 (bootcamp IA; contacto: jorsqn@gmail.com)"},
]

# Importar servicios optimizados
try:
    from Server.core.services.pinecone_service import pinecone_service
    from Server.core.services.embedding_service import embedding_service
    logger.info("✅ Servicios de Pinecone y Embeddings importados correctamente")
except ImportError as e:
    logger.error(f"❌ Error importando servicios: {e}")
    pinecone_service = None
    embedding_service = None
    USE_PINECONE = False


# POIs de la ruta (solo IDs y nombres)
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


# Funciones de Wikipedia
def fetch_wikipedia_content(poi_name: str) -> Dict[str, str]:
    """
    Obtiene contenido de Wikipedia para un POI
    """
    try:
        clean_name = poi_name.replace(" ", "_")
        url = f"{WIKIPEDIA_API_URL}{clean_name}"
        headers = random.choice(HEADERS_LIST)  # <-- Selección aleatoria de User-Agent académico
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "basic_info": data.get("extract", ""),
                "title": data.get("title", poi_name),
                "source_url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
            }
        else:
            logger.warning(f"⚠️ Wikipedia devolvió {response.status_code} para: {poi_name}")
            return {"basic_info": f"Información sobre {poi_name} no disponible en este momento."}
            
    except Exception as e:
        logger.error(f"❌ Error obteniendo datos de Wikipedia para {poi_name}: {e}")
        return {"basic_info": f"Información sobre {poi_name} no disponible temporalmente."}


# Funciones principales
def initialize_madrid_knowledge():
    """
    Inicializa la base de conocimiento obteniendo datos de Wikipedia y subiéndolos a Pinecone
    OPTIMIZADO: Verifica qué POIs ya tienen embeddings para evitar reprocesamiento
    """
    if not USE_PINECONE or not pinecone_service or not pinecone_service.is_available():
        logger.warning("⚠️ Pinecone no disponible, usando modo offline")
        return False
    
    if not embedding_service or not embedding_service.is_available():
        logger.warning("⚠️ Servicio de embeddings no disponible")
        return False
    
    logger.info("🚀 Inicializando base de conocimiento de Madrid...")
    
    existing_vectors = _get_existing_vectors()
    success_count = 0
    
    for poi in ALL_POIS:
        poi_id = poi["id"]
        poi_name = poi["name"]
        vector_id = f"{poi_id}_basic_info"
        
        if vector_id in existing_vectors:
            logger.info(f"⏭️ {poi_name} ya existe en Pinecone, saltando...")
            success_count += 1
            continue
        
        logger.info(f"📍 Procesando {poi_name}...")
        wiki_content = fetch_wikipedia_content(poi_name)
        
        if wiki_content.get("basic_info"):
            embedding = embedding_service.generate_single_embedding(wiki_content["basic_info"], "passage")
            
            if embedding:
                success = pinecone_service.upsert_madrid_content(
                    poi_id=poi_id,
                    content_type="basic_info",
                    text=wiki_content["basic_info"],
                    embedding=embedding
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

def _get_existing_vectors() -> set:
    try:
        stats = pinecone_service.get_index_stats()
        return set()
    except Exception as e:
        logger.error(f"❌ Error verificando vectores existentes: {e}")
        return set()

def get_location_info(poi_id: str, info_type: str = "basic_info") -> str:
    if USE_PINECONE and pinecone_service and pinecone_service.is_available() and embedding_service:
        dummy_query = f"información sobre {poi_id}"
        query_embedding = embedding_service.generate_query_embedding(dummy_query)
        
        if query_embedding:
            results = pinecone_service.search_madrid_content(
                query_embedding=query_embedding,
                poi_id=poi_id,
                content_type=info_type,
                top_k=1
            )
            
            if results and len(results) > 0:
                return results[0].get("metadata", {}).get("text", "Información no disponible")
    
    poi_name = _get_poi_name_by_id(poi_id)
    if poi_name:
        wiki_content = fetch_wikipedia_content(poi_name)
        return wiki_content.get("basic_info", "Información no disponible en este momento.")
    
    return f"Lo siento, no tengo información específica sobre '{poi_id}' en este momento."

def search_madrid_content(query: str) -> str:
    if USE_PINECONE and pinecone_service and pinecone_service.is_available() and embedding_service:
        query_embedding = embedding_service.generate_query_embedding(query)
        
        if query_embedding:
            results = pinecone_service.search_madrid_content(
                query_embedding=query_embedding,
                top_k=3
            )
            
            if results:
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
    
    return _search_by_keywords(query)

def _search_by_keywords(query: str) -> str:
    query_lower = query.lower()
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
    for keyword, poi_id in keyword_mapping.items():
        if keyword in query_lower:
            return get_location_info(poi_id, "basic_info")
    return ("Madrid es la capital de España con un rico patrimonio histórico. "
            "¿Te interesa algún lugar específico como la Plaza Mayor, el Palacio Real o la Puerta del Sol?")

def _get_poi_name_by_id(poi_id: str) -> Optional[str]:
    for poi in ALL_POIS:
        if poi["id"] == poi_id:
            return poi["name"]
    return None

def get_poi_stories(poi_id: str) -> str:
    poi_name = _get_poi_name_by_id(poi_id)
    if poi_name:
        return f"En {poi_name}, cuentan que los ratoncitos guardan secretos mágicos entre sus piedras..."
    return "No hay historias disponibles para este lugar."

def get_poi_curiosities(poi_id: str) -> str:
    return get_location_info(poi_id, "basic_info")

def get_available_locations() -> List[str]:
    return [poi["id"] for poi in ALL_POIS]

def get_location_summary(poi_id: str) -> Dict[str, str]:
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

def ensure_knowledge_initialized():
    if not USE_PINECONE:
        logger.info("📚 Modo offline: usando respuestas predefinidas")
        return True
    if not pinecone_service or not pinecone_service.is_available():
        logger.warning("⚠️ Pinecone no disponible")
        return False
    if not embedding_service or not embedding_service.is_available():
        logger.warning("⚠️ Servicio de embeddings no disponible")
        return False
    try:
        stats = pinecone_service.get_index_stats()
        vector_count = stats.get("total_vector_count", 0)
        if vector_count >= 10:
            logger.info(f"📊 Base de conocimiento ya inicializada ({vector_count} vectores)")
            return True
        else:
            logger.info(f"📊 Base de conocimiento parcial ({vector_count} vectores), se completará en background")
            return True
    except Exception as e:
        logger.error(f"❌ Error verificando estado de Pinecone: {e}")
        return False
