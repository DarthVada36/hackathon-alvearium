import os
import logging
import requests
import time
from typing import List, Dict, Optional, Any
from datetime import datetime
from urllib.parse import quote
from pinecone import Pinecone, ServerlessSpec

# Cache para evitar requests repetidos de Wikipedia
_wikipedia_cache: Dict[str, Dict[str, Any]] = {}
_cache_expiry: Dict[str, float] = {}
CACHE_DURATION = 3600  # 1 hora

# ---------------- Funciones de utilidad para caché ----------------
def clear_wikipedia_cache():
    """Limpia completamente el caché de Wikipedia"""
    global _wikipedia_cache, _cache_expiry
    _wikipedia_cache.clear()
    _cache_expiry.clear()
    logging.info("Caché de Wikipedia limpiado completamente")

def get_wikipedia_cache_info() -> Dict[str, Any]:
    """Obtiene información sobre el estado del caché de Wikipedia"""
    current_time = time.time()
    cache_info = {
        'total_entries': len(_wikipedia_cache),
        'valid_entries': 0,
        'expired_entries': 0,
        'entries': []
    }
    
    for poi_name, cache_data in _wikipedia_cache.items():
        expiry_time = _cache_expiry.get(poi_name, 0)
        is_valid = current_time < expiry_time
        
        if is_valid:
            cache_info['valid_entries'] += 1
        else:
            cache_info['expired_entries'] += 1
        
        cache_info['entries'].append({
            'poi_name': poi_name,
            'success': cache_data.get('success', False),
            'timestamp': cache_data.get('timestamp', 0),
            'expires_at': expiry_time,
            'is_valid': is_valid,
            'variant_used': cache_data.get('variant_used', 'N/A')
        })
    
    return cache_info
try:
    import googlemaps  # type: ignore
except Exception:
    googlemaps = None
import time
import json
try:
    import redis  # Optional scalable cache
except ImportError:
    redis = None

# Load .env for standalone/REPL usage (Server/main.py also loads dotenv on app start)
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# ---------------- Configuración ----------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EVENTBRITE_TOKEN = os.getenv("EVENTBRITE_TOKEN")
EMT_API_URL = "https://openapi.emtmadrid.es/v1/transport/busemtmad/stops"
EMBED_MODEL = os.getenv("EMBED_MODEL", "intfloat/e5-large-v2")

# --- Pinecone v3 index init (serverless) ---
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "perez")
PINECONE_DIM = int(os.getenv("PINECONE_DIM", "1024"))  # match your embedding size (e5-large-v2=1024)
PINECONE_METRIC = os.getenv("PINECONE_METRIC", "cosine")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")

pinecone_index = None
if PINECONE_API_KEY:
    try:
        _pc = Pinecone(api_key=PINECONE_API_KEY)
        # Create index if it doesn't exist
        names = [i["name"] for i in _pc.list_indexes()] if hasattr(_pc, "list_indexes") else []
        if PINECONE_INDEX not in names:
            _pc.create_index(
                name=PINECONE_INDEX,
                dimension=PINECONE_DIM,
                metric=PINECONE_METRIC,
                spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
            )
        pinecone_index = _pc.Index(PINECONE_INDEX)
    except Exception as e:
        logging.warning(f"Pinecone init failed: {e}")
        pinecone_index = None
else:
    logging.info("PINECONE_API_KEY not set; vector DB disabled")

gmaps = googlemaps.Client(key=GOOGLE_API_KEY) if (GOOGLE_API_KEY and googlemaps) else None

API_ENDPOINTS = {
    "wikipedia": "https://es.wikipedia.org/api/rest_v1/page/summary/",
    "nominatim": "https://nominatim.openstreetmap.org/search",
    "eventbrite": "https://www.eventbriteapi.com/v3/events/search/"
}

# ---------------- Cache settings (ENV) ----------------
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "1800"))  # default 30 min
REDIS_URL = os.getenv("REDIS_URL")
CACHE_KEY_PREFIX = os.getenv("CACHE_KEY_PREFIX", "madrid_place:")

_redis_client = None
if REDIS_URL and redis is not None:
    try:
        _redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)
        # quick ping to validate connection (non-fatal if fails)
        try:
            _redis_client.ping()
            logging.info("✅ Redis cache enabled")
        except Exception:
            logging.warning("Redis URL set but ping failed; falling back to in-process cache")
            _redis_client = None
    except Exception as e:
        logging.warning(f"Could not init Redis client: {e}")
        _redis_client = None

# ---------------- Clase MadridPlace ----------------
class MadridPlace:
    def __init__(self, name: str, place_id: str, categories: List[str], age_group: Optional[str] = None):
        self.name = name
        self.place_id = place_id
        self.categories = categories
        self.age_group = age_group
        self.sources: Dict[str, str] = {}
        self.events: List[Dict] = []
        self.transport: List[Dict] = []
        self.restaurants: List[Dict] = []
        self.embedding: Optional[List[float]] = None
        self.metadata: Dict = {}

    def _clean_poi_name_for_wikipedia(self, poi_name: str) -> List[str]:
        """
        Limpia y normaliza el nombre del POI para búsqueda en Wikipedia.
        Devuelve múltiples variantes para mejorar las posibilidades de éxito.
        """
        if not poi_name:
            return []
        
        # Removemos caracteres problemáticos y normalizamos
        base_clean = poi_name.strip()
        
        # Múltiples variantes para buscar
        variants = []
        
        # 1. Nombre original limpio
        variants.append(base_clean)
        
        # 2. Sin "(Madrid)" o similar
        import re
        without_parentheses = re.sub(r'\s*\([^)]*\)\s*', '', base_clean).strip()
        if without_parentheses and without_parentheses != base_clean:
            variants.append(without_parentheses)
        
        # 3. Con "Madrid" al final si no lo tiene
        if "madrid" not in base_clean.lower() and "madrid" not in without_parentheses.lower():
            variants.append(f"{without_parentheses} Madrid")
            variants.append(f"{without_parentheses} (Madrid)")
        
        # 4. Versiones especiales para lugares conocidos
        special_cases = {
            "palacio real": ["Palacio Real de Madrid", "Real Alcázar de Madrid"],
            "teatro real": ["Teatro Real de Madrid", "Teatro Real (Madrid)"],
            "puerta del sol": ["Puerta del Sol (Madrid)", "Puerta del Sol"],
            "plaza mayor": ["Plaza Mayor de Madrid", "Plaza Mayor (Madrid)"],
            "retiro": ["Parque del Retiro", "Parque del Buen Retiro"],
            "prado": ["Museo del Prado", "Museo Nacional del Prado"],
            "reina sofia": ["Museo Reina Sofía", "Museo Nacional Reina Sofía"],
            "thyssen": ["Museo Thyssen-Bornemisza", "Thyssen-Bornemisza"],
        }
        
        poi_lower = base_clean.lower()
        for key, alternatives in special_cases.items():
            if key in poi_lower:
                variants.extend(alternatives)
        
        # Eliminamos duplicados manteniendo el orden
        seen = set()
        unique_variants = []
        for variant in variants:
            if variant and variant not in seen:
                seen.add(variant)
                unique_variants.append(variant)
        
        return unique_variants

    def fetch_wikipedia_summary(self, poi_name: Optional[str] = None) -> Optional[str]:
        """
        Obtiene el resumen de Wikipedia para un POI con manejo robusto de errores,
        caché y múltiples estrategias de búsqueda.
        """
        # Usar el nombre del POI pasado como parámetro o el nombre de la instancia
        name_to_search = poi_name or self.name
        
        if not name_to_search:
            return None
        
        # Verificar caché
        current_time = time.time()
        if name_to_search in _wikipedia_cache and name_to_search in _cache_expiry:
            if current_time < _cache_expiry[name_to_search]:
                logging.info(f"Wikipedia cache hit para '{name_to_search}'")
                cached_result = _wikipedia_cache[name_to_search]
                if cached_result.get('success'):
                    summary = cached_result.get('summary')
                    # Si no se pasó parámetro, almacenar en sources
                    if not poi_name:
                        self.sources['wikipedia'] = summary
                    return summary
                else:
                    return None
        
        # Obtener variantes del nombre
        poi_variants = self._clean_poi_name_for_wikipedia(name_to_search)
        
        if not poi_variants:
            logging.warning(f"No se pudieron generar variantes para el POI: {name_to_search}")
            return None
        
        logging.info(f"Buscando Wikipedia para '{name_to_search}' con {len(poi_variants)} variantes: {poi_variants}")
        
        # Intentar con cada variante
        for i, variant in enumerate(poi_variants):
            try:
                # URL de la API de Wikipedia en español
                encoded_variant = quote(variant)
                url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{encoded_variant}"
                
                # Headers para simular navegador
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'application/json',
                    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
                }
                
                # Request con timeout
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verificar que tenemos contenido útil
                    if 'extract' in data and data['extract']:
                        summary = data['extract'].strip()
                        
                        # Verificar que no sea una página de desambiguación
                        if len(summary) > 50 and not summary.lower().startswith('puede referirse a'):
                            logging.info(f"✅ Wikipedia éxito con variante '{variant}' (intento {i+1}/{len(poi_variants)})")
                            logging.info(f"Resumen obtenido: {len(summary)} caracteres")
                            
                            # Guardar en caché
                            _wikipedia_cache[name_to_search] = {
                                'success': True,
                                'summary': summary,
                                'variant_used': variant,
                                'timestamp': current_time
                            }
                            _cache_expiry[name_to_search] = current_time + CACHE_DURATION
                            
                            # Si no se pasó parámetro, almacenar en sources
                            if not poi_name:
                                self.sources['wikipedia'] = summary
                            
                            return summary
                        else:
                            logging.warning(f"Contenido muy corto o desambiguación para '{variant}': {summary[:100]}...")
                    
                elif response.status_code == 404:
                    logging.info(f"Página no encontrada para variante '{variant}' (intento {i+1}/{len(poi_variants)})")
                else:
                    logging.warning(f"Error HTTP {response.status_code} para variante '{variant}': {response.text[:200]}")
                    
            except requests.exceptions.Timeout:
                logging.warning(f"Timeout en Wikipedia para variante '{variant}' (intento {i+1}/{len(poi_variants)})")
            except requests.exceptions.RequestException as e:
                logging.warning(f"Error de conexión en Wikipedia para variante '{variant}': {str(e)}")
            except Exception as e:
                logging.error(f"Error inesperado al buscar '{variant}' en Wikipedia: {str(e)}")
        
        # Si llegamos aquí, ninguna variante funcionó
        logging.warning(f"❌ No se pudo obtener información de Wikipedia para '{name_to_search}' con ninguna de las {len(poi_variants)} variantes")
        
        # Guardar resultado negativo en caché (pero por menos tiempo)
        _wikipedia_cache[name_to_search] = {
            'success': False,
            'summary': None,
            'variants_tried': poi_variants,
            'timestamp': current_time
        }
        _cache_expiry[name_to_search] = current_time + (CACHE_DURATION // 4)  # 15 minutos para reintentos
        
        return None

    def fetch_wikipedia_summary_old(self):
        """Método antiguo - DEPRECADO: usar fetch_wikipedia_summary() en su lugar"""
        try:
            url = f"{API_ENDPOINTS['wikipedia']}{self.name.replace(' ', '_')}"
            r = requests.get(url)
            if r.status_code == 200:
                self.sources['wikipedia'] = r.json().get('extract', '')
            else:
                logging.warning(f"Wikipedia summary not found for {self.name}")
        except Exception as e:
            logging.error(f"Wikipedia fetch error for {self.name}: {e}")

    def fetch_transport_info(self):
        """Obtiene transporte público en tiempo real usando EMT (bus/metro)."""
        try:
            geo = geocode_place(self.name)
            lat, lon = float(geo.get("lat", 0)), float(geo.get("lon", 0))
            # Ejemplo EMT API: buscar estaciones cercanas (placeholder)
            resp = requests.get(f"{EMT_API_URL}?lat={lat}&lon={lon}")
            stops_data = resp.json()
            self.transport = stops_data.get("stops", [])[:5]  # Solo las 5 más cercanas
            self.sources['transport'] = "Transporte en tiempo real obtenido"
        except Exception as e:
            logging.error(f"Transport fetch error for {self.name}: {e}")

    def fetch_family_events(self, location="Madrid", category="105"):
        """Eventos familiares vía Eventbrite filtrados por fecha."""
        if not EVENTBRITE_TOKEN:
            logging.warning("Eventbrite token not set")
            return
        try:
            headers = {"Authorization": f"Bearer {EVENTBRITE_TOKEN}"}
            params = {
                "location.address": location,
                "categories": category,
                "sort_by": "date",
                "start_date.range_start": datetime.utcnow().isoformat() + "Z"
            }
            resp = requests.get(API_ENDPOINTS['eventbrite'], headers=headers, params=params)
            data = resp.json()
            self.events = data.get("events", [])
            self.sources['eventbrite'] = "Eventos obtenidos"
        except Exception as e:
            logging.error(f"Event fetch error for {self.name}: {e}")

    def fetch_restaurants(self, radius=500):
        """Restaurantes reales usando Google Places API cercanos al lugar."""
        if not gmaps:
            logging.info("Google Maps not configured; skipping restaurants")
            return
        try:
            geo = geocode_place(self.name)
            lat, lon = float(geo.get("lat", 0)), float(geo.get("lon", 0))
            places_result = gmaps.places_nearby(location=(lat, lon), radius=radius, type="restaurant")
            self.restaurants = places_result.get("results", [])
            self.sources['restaurants'] = "Restaurantes obtenidos"
        except Exception as e:
            logging.error(f"Restaurant fetch error for {self.name}: {e}")

    # ---------- Procesamiento ----------
    def consolidate_text(self) -> str:
        narrative_parts = [v for v in self.sources.values() if v]
        for event in self.events:
            narrative_parts.append(f"Evento: {event.get('name', {}).get('text','')} ({event.get('category','familia')})")
        for t in self.transport:
            narrative_parts.append(f"Transporte: {t.get('line','')} parada en {t.get('stop','')}, próximo a las {t.get('next_arrival','')}")
        for r in self.restaurants:
            narrative_parts.append(f"Restaurante cercano: {r.get('name','')}")
        return "\n".join(narrative_parts)

    def generate_embedding(self):
        text = self.consolidate_text()
        if text:
            try:
                vecs = _embed_texts([text], kind="passage")
                self.embedding = vecs[0] if vecs else None
            except Exception as e:
                logging.error(f"Embedding generation failed for {self.name}: {e}")
                self.embedding = None
            self.metadata = {
                "name": self.name,
                "place_id": self.place_id,
                "categories": self.categories,
                "age_group": self.age_group,
                "sources": list(self.sources.keys()),
                "events_count": len(self.events),
                "transport_count": len(self.transport),
                "restaurants_count": len(self.restaurants)
            }
        else:
            logging.warning(f"No text to embed for {self.name}")

    def upsert_to_vector_db(self):
        if not self.embedding:
            logging.warning(f"No embedding for {self.name}")
            return
        if pinecone_index is None:
            logging.info("Pinecone index not available; skipping upsert")
            return
        vector_data = {"id": self.place_id, "values": self.embedding, "metadata": self.metadata}
        pinecone_index.upsert(vectors=[vector_data])

    def generate_magical_story(self, llm: Any = None):
        base_text = self.consolidate_text()
        prompt = f"""
        Eres un narrador mágico para familias que visitan Madrid.
        Crea una historia corta, divertida y mágica sobre {self.name}, basada en:
        {base_text}
        """
        try:
            if llm is None:
                logging.info("LLM not provided; skipping magical story generation")
                return
            story_text = llm(prompt)
            self.metadata["magical_story"] = story_text
            story_embedding = _embed_texts([story_text], kind="passage")[0]
            story_vector_data = {
                "id": f"{self.place_id}_story",
                "values": story_embedding,
                "metadata": {**self.metadata, "type": "magical_story"}
            }
            if pinecone_index is not None:
                pinecone_index.upsert(vectors=[story_vector_data])
            logging.info(f"Magical story generated for {self.name}")
        except Exception as e:
            logging.error(f"Error generating magical story for {self.name}: {e}")

# ---------------- Utilities ----------------
def geocode_place(place_name: str) -> dict:
    try:
        params = {"q": f"{place_name}, Madrid, Spain", "format": "json", "limit": 1}
        resp = requests.get(API_ENDPOINTS["nominatim"], params=params)
        results = resp.json()
        return results[0] if results else {}
    except Exception as e:
        logging.error(f"Geocode error for {place_name}: {e}")
        return {}

def create_places_embedding(places: List[MadridPlace], llm: Any = None):
    for place in places:
        place.fetch_wikipedia_summary()
        place.fetch_transport_info()
        place.fetch_family_events()
        place.fetch_restaurants()
        place.generate_embedding()
        place.upsert_to_vector_db()
        place.generate_magical_story(llm)
        logging.info(f"Processed {place.name}")

def query_places(query: str, top_k=5, filters: Optional[Dict] = None) -> List[Dict]:
    query_vec = _embed_texts([query], kind="query")[0]
    if pinecone_index is None:
        logging.info("Pinecone index not available; returning empty results")
        return []
    results = pinecone_index.query(vector=query_vec, top_k=top_k, filter=filters, include_metadata=True)
    return results if isinstance(results, list) else results.to_dict() if hasattr(results, "to_dict") else results

# ---------------- Cache serialization helpers ----------------
def _serialize_place(place: MadridPlace) -> Dict:
    return {
        "name": place.name,
        "place_id": place.place_id,
        "categories": place.categories,
        "age_group": place.age_group,
        "sources": place.sources,
        "events": place.events,
        "transport": place.transport,
        "restaurants": place.restaurants,
        "embedding": place.embedding,
        "metadata": place.metadata,
    }

def _deserialize_place(data: Dict) -> MadridPlace:
    p = MadridPlace(
        name=data.get("name", ""),
        place_id=data.get("place_id", ""),
        categories=data.get("categories", []),
        age_group=data.get("age_group")
    )
    p.sources = data.get("sources", {})
    p.events = data.get("events", [])
    p.transport = data.get("transport", [])
    p.restaurants = data.get("restaurants", [])
    p.embedding = data.get("embedding")
    p.metadata = data.get("metadata", {})
    return p

# ---------------- Cache accessors ----------------

def _cache_key(place_id: str) -> str:
    return f"{CACHE_KEY_PREFIX}{place_id}"

# Keep in-process cache as fallback already defined: DATA_CACHE

def _cache_get(place_id: str) -> Optional[MadridPlace]:
    # Try Redis first
    if _redis_client is not None:
        try:
            raw = _redis_client.get(_cache_key(place_id))
            if raw:
                data = json.loads(raw)
                return _deserialize_place(data)
        except Exception as e:
            logging.warning(f"Redis get failed for {place_id}: {e}")
    # Fallback to in-process cache
    cached = DATA_CACHE.get(place_id)
    if cached:
        return cached.get("place")
    return None

def _cache_set(place: MadridPlace, timestamp: float) -> None:
    # Set into Redis if available
    if _redis_client is not None:
        try:
            payload = json.dumps(_serialize_place(place))
            _redis_client.setex(_cache_key(place.place_id), CACHE_TTL, payload)
            return
        except Exception as e:
            logging.warning(f"Redis set failed for {place.place_id}: {e}")
    # Fallback to in-process cache
    DATA_CACHE[place.place_id] = {"timestamp": timestamp, "place": place}

# ---------------- Configuración de cache ----------------
DATA_CACHE: Dict[str, Dict] = {}  # {place_id: { "timestamp": ..., "place": MadridPlace }}
# CACHE_TTL is configured via env (CACHE_TTL_SECONDS). See top of file.


# ---------------- Ejemplo de búsqueda con refresco ----------------

def query_places_dynamic(query: str, places: List[MadridPlace], llm: Any = None, top_k: int = 5) -> List[Dict]:
    """Refresca info de lugares (cache/Redis), genera embedding de la query y busca semánticamente."""
    # Asegura datos frescos (usa cache con TTL y Redis si está disponible)
    _ = [get_fresh_place(p, llm) for p in places]

    query_vec = _embed_texts([query], kind="query")[0]
    if pinecone_index is None:
        logging.info("Pinecone index not available; returning empty results")
        return []
    results = pinecone_index.query(vector=query_vec, top_k=top_k, include_metadata=True)
    return results if isinstance(results, list) else results.to_dict() if hasattr(results, "to_dict") else results

def get_fresh_place(place: MadridPlace, llm: Any = None, force_refresh: bool = False) -> MadridPlace:
    """
    Devuelve un MadridPlace con información actualizada.
    - Si los datos son recientes (<CACHE_TTL), devuelve los cacheados.
    - Si han expirado o force_refresh=True, hace fetch de transporte, eventos y restaurantes.
    """
    now = time.time()

    if not force_refresh:
        cached_place = _cache_get(place.place_id)
        # In Redis, expiración se gestiona por TTL; para fallback local, comprobamos timestamp
        if cached_place is not None:
            # Si viene de Redis, ya está dentro de TTL
            if cached_place is not place:
                return cached_place
        else:
            cached = DATA_CACHE.get(place.place_id)
            if cached:
                age = now - cached.get("timestamp", 0)
                if age < CACHE_TTL:
                    logging.info(f"Usando cache para {place.name} (age: {age:.0f}s)")
                    return cached["place"]

    logging.info(f"Refrescando datos para {place.name}...")
    place.fetch_transport_info()
    place.fetch_family_events()
    place.fetch_restaurants()
    place.generate_embedding()
    place.upsert_to_vector_db()
    place.generate_magical_story(llm)

    _cache_set(place, now)
    return place

# Helper para forzar refresco explícito

def force_refresh_place(place: MadridPlace, llm: Any = None) -> MadridPlace:
    return get_fresh_place(place, llm, force_refresh=True)

# ---------------- Example Usage ----------------
if __name__ == "__main__":
    # Optional manual run: requires an LLM compatible with your setup.
    try:
        from langchain_openai import OpenAI as OpenAILLM  # type: ignore
        llm = OpenAILLM(temperature=0.7, max_tokens=300, api_key=OPENAI_API_KEY)
    except Exception:
        llm = None
        logging.info("OpenAI LLM not configured; proceeding without story generation")
    places = [
        MadridPlace("Plaza Mayor", "plaza_mayor", ["historia","juego"], "family"),
        MadridPlace("Palacio Real", "palacio_real", ["historia","turismo"], "general")
    ]
    create_places_embedding(places, llm)
    search_results = query_places("lugares mágicos para niños", top_k=3)
    logging.info(f"Search results: {search_results}")
    # Búsqueda dinámica con refresco
    dynamic_results = query_places_dynamic("lugares mágicos para niños", places, llm, top_k=3)
    logging.info(f"Resultados dinámicos: {dynamic_results}")

# ---------------- Embeddings helper (Sentence-Transformers E5) ----------------
_EMBEDDER = None

def _get_embedder():
    global _EMBEDDER
    if _EMBEDDER is not None:
        return _EMBEDDER
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            f"sentence-transformers not installed: {e}. Please install it (pip install sentence-transformers)."
        )
    model_name = EMBED_MODEL
    _EMBEDDER = SentenceTransformer(model_name)
    return _EMBEDDER

def _embed_texts(texts: List[str], kind: str = "passage") -> List[List[float]]:
    """
    kind: "passage" for documents, "query" for search queries. E5 models benefit from prefixes.
    """
    embedder = _get_embedder()
    if not texts:
        return []
    if kind == "query":
        prepped = [f"query: {t}" for t in texts]
    else:
        prepped = [f"passage: {t}" for t in texts]
    vectors = embedder.encode(prepped, normalize_embeddings=True)
    return vectors.tolist() if hasattr(vectors, "tolist") else vectors
