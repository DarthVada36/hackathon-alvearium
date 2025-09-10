"""
Location Helper - Sistema de navegación con OpenStreetMap
Integrado con Nominatim (geocoding) y OSRM (routing)
"""

from typing import Dict, Any, Optional, List, Tuple
import math
import logging
import aiohttp
import asyncio
import json
from urllib.parse import quote

logger = logging.getLogger(__name__)

# Configuración OpenStreetMap
OSM_CONFIG = {
    "nominatim_url": "https://nominatim.openstreetmap.org",
    "osrm_url": "https://router.project-osrm.org/route/v1/walking",
    "user_agent": "RatonPerezDigital/1.0 (hackathon@example.com)",
    "request_delay": 1.0,  # Seconds between requests (fair use)
}

# Threshold más realista para móviles GPS
POI_ARRIVAL_THRESHOLD = 50  # metros (más preciso para el centro de Madrid)

#  RUTA DEL RATONCITO PÉREZ - 10 PUNTOS 
RATON_PEREZ_ROUTE = [
    {
        "id": "plaza_oriente",
        "name": "Plaza de Oriente",
        "coordinates": {"lat": 40.4184, "lng": -3.7109},
        "address": "Plaza de Oriente, Madrid, España",
        "description": "Plaza histórica frente al Palacio Real",
        "visit_duration": 15,
        "index": 0
    },
    {
        "id": "plaza_ramales",
        "name": "Plaza de Ramales",
        "coordinates": {"lat": 40.4172, "lng": -3.7115},
        "address": "Plaza de Ramales, Madrid, España",
        "description": "Pequeña plaza con historia arqueológica",
        "visit_duration": 10,
        "index": 1
    },
    {
        "id": "calle_vergara",
        "name": "Calle Vergara",
        "coordinates": {"lat": 40.4169, "lng": -3.7095},
        "address": "Calle de Vergara, Madrid, España",
        "description": "Calle histórica del centro de Madrid",
        "visit_duration": 8,
        "index": 2
    },
    {
        "id": "plaza_isabel_ii",
        "name": "Plaza de Isabel II",
        "coordinates": {"lat": 40.4180, "lng": -3.7088},
        "address": "Plaza de Isabel II, Madrid, España",
        "description": "Plaza junto al Teatro Real",
        "visit_duration": 12,
        "index": 3
    },
    {
        "id": "calle_arenal_1",
        "name": "Calle del Arenal (Teatro)",
        "coordinates": {"lat": 40.4175, "lng": -3.7080},
        "address": "Calle del Arenal, Madrid, España",
        "description": "Famosa calle comercial madrileña",
        "visit_duration": 10,
        "index": 4
    },
    {
        "id": "calle_bordadores",
        "name": "Calle de Bordadores",
        "coordinates": {"lat": 40.4164, "lng": -3.7082},
        "address": "Calle de Bordadores, Madrid, España",
        "description": "Calle de artesanos tradicionales",
        "visit_duration": 8,
        "index": 5
    },
    {
        "id": "plazuela_san_gines",
        "name": "Plazuela de San Ginés",
        "coordinates": {"lat": 40.4159, "lng": -3.7085},
        "address": "Plazuela de San Ginés, Madrid, España",
        "description": "Rincón histórico junto a la iglesia",
        "visit_duration": 10,
        "index": 6
    },
    {
        "id": "pasadizo_san_gines",
        "name": "Pasadizo de San Ginés",
        "coordinates": {"lat": 40.4158, "lng": -3.7087},
        "address": "Pasadizo de San Ginés, Madrid, España",
        "description": "Famoso por la chocolatería centenaria",
        "visit_duration": 15,
        "index": 7
    },
    {
        "id": "calle_arenal_2",
        "name": "Calle del Arenal (Sol)",
        "coordinates": {"lat": 40.4168, "lng": -3.7075},
        "address": "Calle del Arenal, Madrid, España",
        "description": "Tramo hacia Puerta del Sol",
        "visit_duration": 8,
        "index": 8
    },
    {
        "id": "museo_raton_perez",
        "name": "Museo Ratoncito Pérez",
        "coordinates": {"lat": 40.4169, "lng": -3.7038},
        "address": "Calle del Arenal, 8, 28013 Madrid, España",
        "description": "¡El hogar oficial del Ratoncito Pérez!",
        "visit_duration": 20,
        "index": 9
    }
]


class OSMLocationHelper:
    """Helper para integración con OpenStreetMap APIs"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = 0
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={"User-Agent": OSM_CONFIG["user_agent"]}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _rate_limit(self):
        """Implementa rate limiting para fair use"""
        import time
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < OSM_CONFIG["request_delay"]:
            await asyncio.sleep(OSM_CONFIG["request_delay"] - time_since_last)
        
        self.last_request_time = time.time()
    
    async def geocode_location(self, location_name: str, city: str = "Madrid") -> Optional[Dict[str, float]]:
        """
        Convierte nombre de lugar a coordenadas usando Nominatim
        """
        await self._rate_limit()
        
        query = f"{location_name}, {city}, España"
        url = f"{OSM_CONFIG['nominatim_url']}/search"
        
        params = {
            "q": query,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        result = data[0]
                        return {
                            "lat": float(result["lat"]),
                            "lng": float(result["lon"])
                        }
                    else:
                        logger.warning(f"No se encontraron coordenadas para: {query}")
                        return None
                else:
                    logger.error(f"Error en geocoding: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error en geocoding: {e}")
            return None
    
    async def reverse_geocode(self, lat: float, lng: float) -> Optional[str]:
        """
        Convierte coordenadas a nombre de lugar usando Nominatim
        """
        await self._rate_limit()
        
        url = f"{OSM_CONFIG['nominatim_url']}/reverse"
        
        params = {
            "lat": lat,
            "lon": lng,
            "format": "json",
            "addressdetails": 1
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extraer nombre más relevante
                    display_name = data.get("display_name", "")
                    address = data.get("address", {})
                    
                    # Priorizar: POI > road > neighbourhood
                    if "tourism" in address:
                        return address["tourism"]
                    elif "amenity" in address:
                        return address["amenity"]
                    elif "road" in address:
                        return address["road"]
                    elif "neighbourhood" in address:
                        return address["neighbourhood"]
                    else:
                        # Tomar primera parte del display_name
                        return display_name.split(",")[0] if display_name else "Ubicación desconocida"
                        
                else:
                    logger.error(f"Error en reverse geocoding: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error en reverse geocoding: {e}")
            return None
    
    async def get_walking_route(self, start_coords: Dict[str, float], 
                              end_coords: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """
        Obtiene ruta de caminata entre dos puntos usando OSRM
        """
        await self._rate_limit()
        
        # Formato: lng,lat;lng,lat (OSRM usa lng primero)
        coordinates = f"{start_coords['lng']},{start_coords['lat']};{end_coords['lng']},{end_coords['lat']}"
        url = f"{OSM_CONFIG['osrm_url']}/{coordinates}"
        
        params = {
            "overview": "geometry",
            "steps": "true",
            "geometries": "geojson"
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("code") == "Ok" and data.get("routes"):
                        route = data["routes"][0]
                        
                        return {
                            "distance_meters": route["distance"],
                            "duration_seconds": route["duration"],
                            "geometry": route["geometry"],
                            "steps": route["legs"][0].get("steps", [])
                        }
                    else:
                        logger.warning(f"OSRM no pudo calcular ruta: {data.get('message', 'Unknown error')}")
                        return None
                        
                else:
                    logger.error(f"Error en routing: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error en routing: {e}")
            return None


# Instancia global del helper
osm_helper = OSMLocationHelper()


# FUNCIONES PÚBLICAS ACTUALIZADAS

async def check_poi_arrival(location: Dict[str, float], threshold_meters: int = None) -> Dict[str, Any]:
    """
    Verifica si la ubicación actual está cerca de algún POI - CON OSM
    """
    if threshold_meters is None:
        threshold_meters = POI_ARRIVAL_THRESHOLD
    
    if not location or "lat" not in location or "lng" not in location:
        logger.error("❌ Ubicación inválida para check_poi_arrival")
        return {"arrived": False, "error": "Ubicación inválida"}
    
    logger.info(f"🔍 Verificando llegada en {location['lat']:.4f}, {location['lng']:.4f}")
    
    closest_poi = None
    min_distance = float('inf')
    
    # Buscar POI más cercano en la nueva ruta
    for poi in RATON_PEREZ_ROUTE:
        distance = calculate_distance(location, poi["coordinates"])
        logger.debug(f"   Distancia a {poi['name']}: {distance:.1f}m")
        
        if distance < min_distance:
            min_distance = distance
            closest_poi = poi
    
    logger.info(f"📍 POI más cercano: {closest_poi['name']} a {min_distance:.1f}m")
    
    # Verificar si está dentro del threshold
    if closest_poi and min_distance <= threshold_meters:
        result = {
            "arrived": True,
            "poi_id": closest_poi["id"],
            "poi_name": closest_poi["name"],
            "poi_index": closest_poi["index"],
            "distance_meters": round(min_distance, 1),
            "message": f"¡Habéis llegado a {closest_poi['name']}!",
            "closest_poi": closest_poi["name"],
            "distance_to_closest": round(min_distance, 1)
        }
        logger.info(f"✅ LLEGADA DETECTADA: {closest_poi['name']} ({min_distance:.1f}m)")
        return result
    
    # No llegaron pero dar info del más cercano
    result = {
        "arrived": False,
        "closest_poi": closest_poi["name"] if closest_poi else "Desconocido",
        "distance_to_closest": round(min_distance, 1) if closest_poi else None,
        "message": f"Os faltan {round(min_distance - threshold_meters, 1)}m para llegar a {closest_poi['name']}" if closest_poi else "No hay POIs cercanos"
    }
    
    logger.info(f"ℹ️ No hay llegada - Más cercano: {result['closest_poi']} a {result['distance_to_closest']}m")
    return result


async def get_directions_osm(start_location: Optional[Dict[str, float]], current_poi_index: int) -> str:
    """
    Obtiene direcciones reales usando OSRM
    """
    if current_poi_index >= len(RATON_PEREZ_ROUTE):
        return "¡Habéis completado toda la ruta del Ratoncito Pérez! ¡Enhorabuena! 🎉"
    
    target_poi = RATON_PEREZ_ROUTE[current_poi_index]
    
    if not start_location:
        return f"""🎯 **Próximo destino:** {target_poi['name']}
📍 **Dirección:** {target_poi['address']}
ℹ️ **Información:** {target_poi['description']}
⏱️ **Tiempo estimado de visita:** {target_poi['visit_duration']} minutos"""
    
    # Obtener ruta real con OSRM
    try:
        async with osm_helper as helper:
            route_data = await helper.get_walking_route(start_location, target_poi["coordinates"])
            
            if route_data:
                distance_m = route_data["distance_meters"]
                duration_s = route_data["duration_seconds"]
                
                # Formatear tiempo
                if duration_s < 60:
                    time_str = f"{int(duration_s)} segundos"
                else:
                    minutes = int(duration_s // 60)
                    time_str = f"{minutes} minuto{'s' if minutes != 1 else ''}"
                
                return f"""🎯 **Próximo destino:** {target_poi['name']}
📏 **Distancia:** {distance_m:.0f} metros
🚶 **Tiempo caminando:** {time_str}
📍 **Dirección exacta:** {target_poi['address']}
ℹ️ **Sobre el lugar:** {target_poi['description']}
⏱️ **Tiempo de visita:** {target_poi['visit_duration']} minutos

🗺️ ¡Seguid las indicaciones de vuestro GPS para llegar!"""
            
            else:
                # Fallback si OSRM falla
                distance_straight = calculate_distance(start_location, target_poi["coordinates"])
                time_estimate = _estimate_walking_time(distance_straight)
                
                return f"""🎯 **Próximo destino:** {target_poi['name']}
📏 **Distancia aproximada:** {distance_straight:.0f} metros
🚶 **Tiempo aproximado:** {time_estimate}
📍 **Dirección:** {target_poi['address']}
ℹ️ **Información:** {target_poi['description']}

⚠️ Usad vuestro GPS para la navegación exacta"""
                
    except Exception as e:
        logger.error(f"Error obteniendo direcciones OSM: {e}")
        
        # Fallback completo
        distance_straight = calculate_distance(start_location, target_poi["coordinates"])
        time_estimate = _estimate_walking_time(distance_straight)
        
        return f"""🎯 **Siguiente destino:** {target_poi['name']}
📏 **Distancia:** {distance_straight:.0f}m (línea recta)
🚶 **Tiempo estimado:** {time_estimate}
📍 **Dirección:** {target_poi['address']}"""


def get_next_poi(current_poi_index: int, current_location: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Obtiene información del próximo POI 
    """
    if current_poi_index >= len(RATON_PEREZ_ROUTE):
        return {
            "completed": True,
            "message": "¡Habéis completado toda la ruta del Ratoncito Pérez! ¡Habéis llegado al Museo! ¡Sois unos verdaderos exploradores de Madrid! 🏆"
        }
    
    next_poi = RATON_PEREZ_ROUTE[current_poi_index]
    
    result = {
        "completed": False,
        "poi_id": next_poi["id"],
        "poi_name": next_poi["name"],
        "poi_index": next_poi["index"],
        "address": next_poi["address"],
        "description": next_poi["description"],
        "visit_duration": next_poi["visit_duration"],
        "coordinates": next_poi["coordinates"]
    }
    
    # Añadir información de distancia si hay ubicación actual
    if current_location:
        distance = calculate_distance(current_location, next_poi["coordinates"])
        result.update({
            "distance_meters": round(distance, 1),
            "walking_time": _estimate_walking_time(distance)
        })
    
    return result


def get_route_overview(current_location: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Vista general de toda la ruta 
    """
    total_distance = _calculate_total_route_distance()
    total_visit_time = sum(poi["visit_duration"] for poi in RATON_PEREZ_ROUTE)
    estimated_walking_time = 45  # Estimado para toda la ruta
    
    route_info = {
        "total_pois": len(RATON_PEREZ_ROUTE),
        "estimated_walking_distance": f"{round(total_distance/1000, 1)} km",
        "estimated_visit_time": f"{total_visit_time} minutos",
        "estimated_walking_time": f"{estimated_walking_time} minutos",
        "estimated_total_time": f"{total_visit_time + estimated_walking_time} minutos",
        "route_theme": "Ruta oficial del Ratoncito Pérez por el Madrid histórico",
        "pois": []
    }
    
    for poi in RATON_PEREZ_ROUTE:
        poi_info = {
            "name": poi["name"],
            "order": poi["index"] + 1,
            "visit_duration": poi["visit_duration"],
            "address": poi["address"],
            "description": poi["description"]
        }
        
        if current_location:
            distance = calculate_distance(current_location, poi["coordinates"])
            poi_info["distance_from_current"] = f"{round(distance, 0)}m"
            poi_info["walking_time_from_current"] = _estimate_walking_time(distance)
        
        route_info["pois"].append(poi_info)
    
    return route_info


def find_nearest_poi(location: Dict[str, float]) -> Dict[str, Any]:
    """
    Encuentra el POI más cercano 
    """
    if not location or "lat" not in location or "lng" not in location:
        return {"error": "Ubicación requerida"}
    
    closest_poi = None
    min_distance = float('inf')
    
    for poi in RATON_PEREZ_ROUTE:
        distance = calculate_distance(location, poi["coordinates"])
        if distance < min_distance:
            min_distance = distance
            closest_poi = poi
    
    if closest_poi:
        return {
            "poi_id": closest_poi["id"],
            "poi_name": closest_poi["name"],
            "poi_index": closest_poi["index"],
            "distance_meters": round(min_distance, 1),
            "walking_time": _estimate_walking_time(min_distance),
            "coordinates": closest_poi["coordinates"],
            "description": closest_poi["description"],
            "is_nearby": min_distance <= POI_ARRIVAL_THRESHOLD
        }
    
    return {"error": "No se encontraron POIs cercanos"}


# FUNCIONES AUXILIARES 

def calculate_distance(point1: Dict[str, float], point2: Dict[str, float]) -> float:
    """
    Calcula distancia con fórmula de Haversine - MEJORADA
    """
    try:
        lat1, lon1 = math.radians(point1["lat"]), math.radians(point1["lng"])
        lat2, lon2 = math.radians(point2["lat"]), math.radians(point2["lng"])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radio de la Tierra en metros
        r = 6371000
        
        distance = c * r
        return distance
        
    except Exception as e:
        logger.error(f"Error calculando distancia: {e}")
        return float('inf')


def _estimate_walking_time(distance_meters: float) -> str:
    """
    Estima tiempo de caminata - 4.5 km/h promedio
    """
    if distance_meters <= 0:
        return "0m"
    
    # Velocidad de caminata urbana: 4.5 km/h
    walking_speed_mps = 4500 / 3600  # 4.5 km/h en m/s
    time_seconds = distance_meters / walking_speed_mps
    
    if time_seconds < 60:
        return f"{max(1, int(time_seconds))}s"
    else:
        minutes = max(1, int(time_seconds // 60))
        return f"{minutes}m"


def _calculate_total_route_distance() -> float:
    """Calcula distancia total de toda la ruta (10 puntos)"""
    total_distance = 0
    
    for i in range(len(RATON_PEREZ_ROUTE) - 1):
        distance = calculate_distance(
            RATON_PEREZ_ROUTE[i]["coordinates"],
            RATON_PEREZ_ROUTE[i + 1]["coordinates"]
        )
        total_distance += distance
    
    return total_distance


def is_valid_location(location: Dict[str, float]) -> bool:
    """Verifica si una ubicación es válida para Madrid centro"""
    if not isinstance(location, dict):
        return False
    
    if "lat" not in location or "lng" not in location:
        return False
    
    try:
        lat, lng = float(location["lat"]), float(location["lng"])
        # Área del centro histórico de Madrid (más específica)
        return (40.410 <= lat <= 40.425) and (-3.720 <= lng <= -3.700)
    except (ValueError, TypeError):
        return False


def get_poi_by_id(poi_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene información de un POI por su ID"""
    for poi in RATON_PEREZ_ROUTE:
        if poi["id"] == poi_id:
            return poi
    return None


def get_poi_by_index(index: int) -> Optional[Dict[str, Any]]:
    """Obtiene información de un POI por su índice"""
    if 0 <= index < len(RATON_PEREZ_ROUTE):
        return RATON_PEREZ_ROUTE[index]
    return None


def get_total_pois() -> int:
    """Obtiene el número total de POIs en la ruta"""
    return len(RATON_PEREZ_ROUTE)


def get_poi_arrival_threshold() -> int:
    """Obtiene el threshold actual de llegada"""
    return POI_ARRIVAL_THRESHOLD


def set_poi_arrival_threshold(meters: int):
    """Establece un nuevo threshold de llegada"""
    global POI_ARRIVAL_THRESHOLD
    POI_ARRIVAL_THRESHOLD = max(25, min(100, meters))  # Entre 25m y 100m para centro urbano
    logger.info(f"📍 Threshold de llegada establecido en {POI_ARRIVAL_THRESHOLD}m")


# FUNCIONES DE COMPATIBILIDAD CON LA API ANTERIOR
get_directions = get_directions_osm  # Alias para compatibilidad