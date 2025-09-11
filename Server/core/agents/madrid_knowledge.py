"""
Madrid Knowledge - Sistema de conocimiento sobre Madrid
Integrado con Pinecone para búsquedas vectoriales y Wikipedia para contenido dinámico
"""

from typing import Dict, Any, List, Optional
import logging
import os
import time
import json

# ============================
# Configuración
# ============================
USE_PINECONE = True  # ✅ Cambiado a True

# Control de inicialización de Pinecone
_last_initialization_check = 0
_initialization_success = False
INITIALIZATION_COOLDOWN = 300  # 5 minutos

logger = logging.getLogger(__name__)

# Importar servicios
try:
    from Server.core.services.pinecone_service import get_pinecone_service
    logger.info("✅ Pinecone service getter importado correctamente")
except ImportError as e:
    logger.error(f"❌ Error importando pinecone_service getter: {e}")
    get_pinecone_service = None
    USE_PINECONE = False

# Importar funciones de Wikipedia consolidadas
try:
    from Server.core.services.madrid_apis import MadridPlace, clear_wikipedia_cache, get_wikipedia_cache_info
    logger.info("✅ Wikipedia functions importadas desde madrid_apis")
except ImportError as e:
    logger.error(f"❌ Error importando funciones de Wikipedia desde madrid_apis: {e}")
    MadridPlace = None

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
# Funciones de Wikipedia integradas
# ============================
def fetch_wikipedia_content(poi_name: str, use_cache: bool = True) -> Dict[str, str]:
    """
    Wrapper para usar la función consolidada de Wikipedia desde madrid_apis
    Mantiene compatibilidad con el código existente
    """
    if not MadridPlace:
        logger.error("MadridPlace no está disponible, usando fallback")
        return {
            "basic_info": f"{poi_name} es un importante lugar histórico en el centro de Madrid, España.",
            "title": poi_name,
            "source_url": "",
            "variant_used": "fallback",
            "success": False
        }
    
    # Crear instancia temporal de MadridPlace para usar su método mejorado
    temp_place = MadridPlace(name=poi_name, place_id="temp", categories=["landmark"])
    
    # Usar el método mejorado de Wikipedia
    summary = temp_place.fetch_wikipedia_summary(poi_name)
    
    if summary:
        return {
            "basic_info": summary,
            "title": poi_name,
            "source_url": f"https://es.wikipedia.org/wiki/{poi_name.replace(' ', '_')}",
            "variant_used": "madrid_apis",
            "success": True
        }
    else:
        # Fallback con información básica
        return {
            "basic_info": f"{poi_name} es un importante lugar histórico en el centro de Madrid, España. Forma parte del patrimonio cultural de la ciudad y es uno de los puntos de interés en la ruta del Ratoncito Pérez.",
            "title": poi_name,
            "source_url": "",
            "variant_used": "fallback", 
            "success": False
        }

# ============================
# Funciones principales
# ============================
def initialize_madrid_knowledge(force_refresh: bool = False):
    """
    Inicializa la base de conocimiento obteniendo datos de Wikipedia y subiéndolos a Pinecone
    Incluye control de rate limiting para evitar inicializaciones excesivas
    """
    global _last_initialization_check, _initialization_success
    
    current_time = time.time()
    
    # Control de cooldown - no reinicializar si fue exitoso recientemente
    if not force_refresh and _initialization_success and (current_time - _last_initialization_check) < INITIALIZATION_COOLDOWN:
        logger.debug(f"🕐 Inicialización en cooldown, esperando {INITIALIZATION_COOLDOWN - (current_time - _last_initialization_check):.0f}s más")
        return True
    
    _last_initialization_check = current_time
    
    svc = get_pinecone_service() if get_pinecone_service is not None else None
    if not USE_PINECONE or not svc or not svc.is_available():
        logger.warning("⚠️ Pinecone no disponible, usando modo offline")
        _initialization_success = False
        return False
    
    logger.info("🚀 Inicializando base de conocimiento de Madrid...")
    
    success_count = 0
    errors = []
    
    # Procesar POIs en lotes más pequeños para evitar rate limits
    batch_size = 3
    for i in range(0, len(ALL_POIS), batch_size):
        batch = ALL_POIS[i:i + batch_size]
        
        for poi in batch:
            poi_id = poi["id"]
            poi_name = poi["name"]
            
            logger.info(f"📍 Procesando {poi_name}...")
            
            try:
                # Obtener contenido de Wikipedia con cache
                wiki_content = fetch_wikipedia_content(poi_name, use_cache=True)
                
                # Solo contar como éxito si realmente obtuvimos contenido de Wikipedia
                if wiki_content.get("basic_info") and wiki_content.get("success", False):
                    # Generar embedding
                    embeddings = _get_embeddings([wiki_content["basic_info"]])
                    
                    if embeddings:
                        # Subir a Pinecone
                        svc = get_pinecone_service() if get_pinecone_service is not None else None
                        success = svc.upsert_madrid_content(
                            poi_id=poi_id,
                            content_type="basic_info",
                            text=wiki_content["basic_info"],
                            embedding=embeddings[0]
                        )
                        
                        if success:
                            success_count += 1
                            variant_used = wiki_content.get("variant_used", "unknown")
                            logger.info(f"✅ {poi_name} subido a Pinecone (variante: {variant_used})")
                        else:
                            error_msg = f"Error subiendo {poi_name} a Pinecone"
                            logger.error(f"❌ {error_msg}")
                            errors.append(error_msg)
                    else:
                        error_msg = f"No se pudo generar embedding para {poi_name}"
                        logger.error(f"❌ {error_msg}")
                        errors.append(error_msg)
                elif wiki_content.get("basic_info"):
                    # Tenemos contenido pero es fallback
                    error_msg = f"Solo contenido fallback disponible para {poi_name}"
                    logger.warning(f"⚠️ {error_msg}")
                    errors.append(error_msg)
                else:
                    error_msg = f"No se obtuvo contenido para {poi_name}"
                    logger.warning(f"⚠️ {error_msg}")
                    errors.append(error_msg)
                    
            except Exception as e:
                error_msg = f"Error procesando {poi_name}: {str(e)}"
                logger.error(f"❌ {error_msg}")
                errors.append(error_msg)
        
        # Pausa breve entre lotes para evitar rate limits
        if i + batch_size < len(ALL_POIS):
            logger.debug("⏳ Pausa entre lotes...")
            time.sleep(2)
    
    # Determinar éxito
    success_rate = success_count / len(ALL_POIS)
    _initialization_success = success_rate >= 0.7  # 70% de éxito mínimo
    
    if _initialization_success:
        logger.info(f"🎯 Inicialización exitosa: {success_count}/{len(ALL_POIS)} POIs procesados ({success_rate:.1%})")
    else:
        logger.warning(f"⚠️ Inicialización parcial: {success_count}/{len(ALL_POIS)} POIs procesados ({success_rate:.1%})")
        if errors:
            logger.warning(f"Errores encontrados: {'; '.join(errors[:3])}{'...' if len(errors) > 3 else ''}")
    
    return _initialization_success

def get_location_info(poi_id: str, info_type: str = "basic_info") -> str:
    """
    Obtiene información sobre una ubicación específica
    """
    svc = get_pinecone_service() if get_pinecone_service is not None else None
    if USE_PINECONE and svc and svc.is_available():
        # Buscar en Pinecone por POI específico
        dummy_query = f"información sobre {poi_id}"
        query_embedding = _get_query_embedding(dummy_query)
        
        if query_embedding:
            results = svc.search_madrid_content(
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
    svc = get_pinecone_service() if get_pinecone_service is not None else None
    if USE_PINECONE and svc and svc.is_available():
        # Búsqueda semántica en Pinecone
        query_embedding = _get_query_embedding(query)
        
        if query_embedding:
            results = svc.search_madrid_content(
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
    Con control mejorado de frecuencia y estado persistente
    """
    global _initialization_success, _last_initialization_check
    
    current_time = time.time()
    
    if not USE_PINECONE:
        logger.info("📚 Modo offline: usando respuestas predefinidas")
        return True
    
    svc = get_pinecone_service() if get_pinecone_service is not None else None
    if not svc or not svc.is_available():
        logger.warning("⚠️ Pinecone no disponible")
        return False
    
    # Si la inicialización fue exitosa recientemente, no verificar de nuevo
    if _initialization_success and (current_time - _last_initialization_check) < INITIALIZATION_COOLDOWN:
        logger.debug("✅ Base de conocimiento confirmada como lista (cache)")
        return True
    
    try:
        # Verificar estado actual del índice
        stats = svc.get_index_stats()
        vector_count = stats.get("total_vector_count", 0)
        
        if vector_count == 0:
            logger.info("📊 Pinecone vacío, inicializando 10 POIs de la ruta...")
            return initialize_madrid_knowledge(force_refresh=False)
        elif vector_count < len(ALL_POIS):
            logger.info(f"📊 Pinecone tiene {vector_count} vectores, completando hasta {len(ALL_POIS)}...")
            return initialize_madrid_knowledge(force_refresh=False)
        else:
            logger.debug(f"📊 Pinecone ya tiene {vector_count} vectores (≥{len(ALL_POIS)} POIs)")
            _initialization_success = True
            _last_initialization_check = current_time
            return True
            
    except Exception as e:
        logger.error(f"❌ Error verificando estado de Pinecone: {e}")
        # En caso de error, intentar inicialización solo si ha pasado suficiente tiempo
        if (current_time - _last_initialization_check) > INITIALIZATION_COOLDOWN:
            logger.info("🔄 Reintentando inicialización tras error de verificación...")
            return initialize_madrid_knowledge(force_refresh=False)
        return False

# ============================
# Funciones de utilidad para cache
# ============================
# Funciones de utilidad - Cache consolidado
# ============================
def get_cache_stats() -> Dict[str, Any]:
    """Obtiene estadísticas del cache usando las funciones consolidadas"""
    if get_wikipedia_cache_info:
        consolidated_info = get_wikipedia_cache_info()
        return {
            "total_cached_items": consolidated_info.get('total_entries', 0),
            "valid_cached_items": consolidated_info.get('valid_entries', 0),
            "expired_items": consolidated_info.get('expired_entries', 0),
            "cache_hit_potential": consolidated_info.get('valid_entries', 0) / len(ALL_POIS) if len(ALL_POIS) > 0 else 0,
            "last_initialization_check": _last_initialization_check,
            "initialization_success": _initialization_success,
            "cooldown_remaining": max(0, INITIALIZATION_COOLDOWN - (time.time() - _last_initialization_check))
        }
    else:
        return {
            "total_cached_items": 0,
            "valid_cached_items": 0,
            "expired_items": 0,
            "cache_hit_potential": 0,
            "last_initialization_check": _last_initialization_check,
            "initialization_success": _initialization_success,
            "cooldown_remaining": max(0, INITIALIZATION_COOLDOWN - (time.time() - _last_initialization_check))
        }

def force_knowledge_refresh():
    """Fuerza una actualización completa de la base de conocimiento"""
    global _initialization_success, _last_initialization_check
    logger.info("🔄 Forzando actualización completa de la base de conocimiento...")
    
    # Limpiar cache usando función consolidada
    if clear_wikipedia_cache:
        clear_wikipedia_cache()
    
    # Resetear estado de inicialización
    _initialization_success = False
    _last_initialization_check = 0
    
    # Inicializar con refresh forzado
    return initialize_madrid_knowledge(force_refresh=True)