"""
Location Helper - Sistema de navegación y ubicación
Preparado para Google Maps con cálculos mock actuales
"""

from typing import Dict, Any, Optional, List, Tuple
import math


# Configuración para futuro Google Maps
USE_GOOGLE_MAPS = False  # Cambiar a True cuando esté disponible
GOOGLE_MAPS_API_KEY = None


# Ruta del Ratoncito Pérez - Coordenadas reales de Madrid
MADRID_ROUTE = [
    {
        "id": "plaza_mayor",
        "name": "Plaza Mayor",
        "coordinates": {"lat": 40.4155, "lng": -3.7074},
        "address": "Plaza Mayor, 28012 Madrid, España",
        "visit_duration": 20,  # minutos
        "index": 0
    },
    {
        "id": "mercado_san_miguel", 
        "name": "Mercado de San Miguel",
        "coordinates": {"lat": 40.4154, "lng": -3.7085},
        "address": "Plaza de San Miguel, s/n, 28005 Madrid, España", 
        "visit_duration": 25,
        "index": 1
    },
    {
        "id": "palacio_real",
        "name": "Palacio Real",
        "coordinates": {"lat": 40.4179, "lng": -3.7143},
        "address": "C. de Bailén, s/n, 28071 Madrid, España",
        "visit_duration": 30,
        "index": 2
    },
    {
        "id": "teatro_real",
        "name": "Teatro Real",
        "coordinates": {"lat": 40.4184, "lng": -3.7109},
        "address": "Plaza de Oriente, s/n, 28013 Madrid, España",
        "visit_duration": 15,
        "index": 3
    },
    {
        "id": "puerta_del_sol",
        "name": "Puerta del Sol", 
        "coordinates": {"lat": 40.4168, "lng": -3.7038},
        "address": "Puerta del Sol, 28013 Madrid, España",
        "visit_duration": 20,
        "index": 4
    }
]


def check_poi_arrival(location: Dict[str, float], threshold_meters: int = 50) -> Dict[str, Any]:
    """
    Verifica si la ubicación actual está cerca de algún POI
    
    Args:
        location: {"lat": float, "lng": float}
        threshold_meters: Distancia mínima para considerar "llegada"
        
    Returns:
        Dict con información de llegada
    """
    
    if not location or "lat" not in location or "lng" not in location:
        return {"arrived": False, "error": "Ubicación inválida"}
    
    closest_poi = None
    min_distance = float('inf')
    
    # Buscar POI más cercano
    for poi in MADRID_ROUTE:
        distance = _calculate_distance(location, poi["coordinates"])
        
        if distance < min_distance:
            min_distance = distance
            closest_poi = poi
    
    # Verificar si está dentro del threshold
    if closest_poi and min_distance <= threshold_meters:
        return {
            "arrived": True,
            "poi_id": closest_poi["id"],
            "poi_name": closest_poi["name"],
            "poi_index": closest_poi["index"],
            "distance_meters": round(min_distance, 1),
            "message": f"¡Habéis llegado a {closest_poi['name']}!"
        }
    
    # No llegaron a ningún POI
    return {
        "arrived": False,
        "closest_poi": closest_poi["name"] if closest_poi else "Desconocido",
        "distance_to_closest": round(min_distance, 1) if closest_poi else None,
        "message": f"Os faltan {round(min_distance, 1)}m para llegar a {closest_poi['name']}" if closest_poi else "No hay POIs cercanos"
    }


def get_directions(start_location: Optional[Dict[str, float]], current_poi_index: int) -> str:
    """
    Obtiene direcciones al siguiente POI en la ruta
    
    Args:
        start_location: Ubicación actual
        current_poi_index: Índice del POI actual
        
    Returns:
        Instrucciones de navegación
    """
    
    if USE_GOOGLE_MAPS and GOOGLE_MAPS_API_KEY:
        return _get_google_directions(start_location, current_poi_index)
    
    # Direcciones mock pero realistas
    if current_poi_index >= len(MADRID_ROUTE):
        return "¡Habéis completado toda la ruta del Ratoncito Pérez! ¡Enhorabuena!"
    
    target_poi = MADRID_ROUTE[current_poi_index]
    
    if not start_location:
        return f"Vuestro siguiente destino es {target_poi['name']} en {target_poi['address']}"
    
    # Calcular distancia y tiempo
    distance = _calculate_distance(start_location, target_poi["coordinates"])
    walking_time = _estimate_walking_time(distance)
    
    # Direcciones específicas basadas en ubicaciones reales
    directions = _get_mock_directions(current_poi_index, target_poi)
    
    return f"""🎯 Próximo destino: {target_poi['name']}
📍 Distancia: {round(distance, 0)}m ({walking_time})
🚶 Direcciones: {directions}
📱 Dirección exacta: {target_poi['address']}"""


def get_next_poi(current_poi_index: int, current_location: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Obtiene información del próximo POI en la ruta
    
    Args:
        current_poi_index: Índice actual en la ruta
        current_location: Ubicación actual (opcional)
        
    Returns:
        Información del próximo POI
    """
    
    if current_poi_index >= len(MADRID_ROUTE):
        return {
            "completed": True,
            "message": "¡Habéis completado toda la ruta del Ratoncito Pérez! ¡Sois unos verdaderos exploradores de Madrid!"
        }
    
    next_poi = MADRID_ROUTE[current_poi_index]
    
    result = {
        "completed": False,
        "poi_id": next_poi["id"],
        "poi_name": next_poi["name"],
        "poi_index": next_poi["index"],
        "address": next_poi["address"],
        "visit_duration": next_poi["visit_duration"],
        "coordinates": next_poi["coordinates"]
    }
    
    # Añadir información de navegación si hay ubicación actual
    if current_location:
        distance = _calculate_distance(current_location, next_poi["coordinates"])
        result.update({
            "distance_meters": round(distance, 1),
            "walking_time": _estimate_walking_time(distance),
            "directions": _get_mock_directions(current_poi_index, next_poi)
        })
    
    return result


def get_route_overview(current_location: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Obtiene vista general de toda la ruta
    
    Returns:
        Información completa de la ruta
    """
    
    total_distance = _calculate_total_route_distance()
    total_time = sum(poi["visit_duration"] for poi in MADRID_ROUTE)
    
    route_info = {
        "total_pois": len(MADRID_ROUTE),
        "estimated_walking_distance": f"{round(total_distance/1000, 1)} km",
        "estimated_total_time": f"{total_time + 60} minutos",  # +60 para caminar
        "pois": []
    }
    
    for poi in MADRID_ROUTE:
        poi_info = {
            "name": poi["name"],
            "order": poi["index"] + 1,
            "visit_duration": poi["visit_duration"],
            "address": poi["address"]
        }
        
        # Añadir distancia desde ubicación actual si está disponible
        if current_location:
            distance = _calculate_distance(current_location, poi["coordinates"])
            poi_info["distance_from_current"] = f"{round(distance, 0)}m"
            poi_info["walking_time_from_current"] = _estimate_walking_time(distance)
        
        route_info["pois"].append(poi_info)
    
    return route_info


def find_nearest_poi(location: Dict[str, float]) -> Dict[str, Any]:
    """
    Encuentra el POI más cercano a una ubicación
    
    Args:
        location: Ubicación actual
        
    Returns:
        Información del POI más cercano
    """
    
    if not location:
        return {"error": "Ubicación requerida"}
    
    closest_poi = None
    min_distance = float('inf')
    
    for poi in MADRID_ROUTE:
        distance = _calculate_distance(location, poi["coordinates"])
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
            "coordinates": closest_poi["coordinates"]
        }
    
    return {"error": "No se encontraron POIs cercanos"}


# Funciones auxiliares

def _calculate_distance(point1: Dict[str, float], point2: Dict[str, float]) -> float:
    """
    Calcula distancia entre dos coordenadas usando fórmula de Haversine
    
    Returns:
        Distancia en metros
    """
    
    lat1, lon1 = math.radians(point1["lat"]), math.radians(point1["lng"])
    lat2, lon2 = math.radians(point2["lat"]), math.radians(point2["lng"])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radio de la Tierra en metros
    r = 6371000
    
    return c * r


def _estimate_walking_time(distance_meters: float) -> str:
    """
    Estima tiempo de caminata (velocidad: 4 km/h)
    
    Returns:
        Tiempo formateado (ej: "5m" o "12m")
    """
    
    walking_speed_mps = 4000 / 3600  # 4 km/h en m/s
    time_seconds = distance_meters / walking_speed_mps
    minutes = int(time_seconds // 60)
    
    return f"{minutes}m" if minutes > 0 else "1m"


def _calculate_total_route_distance() -> float:
    """Calcula distancia total de toda la ruta"""
    
    total_distance = 0
    
    for i in range(len(MADRID_ROUTE) - 1):
        distance = _calculate_distance(
            MADRID_ROUTE[i]["coordinates"],
            MADRID_ROUTE[i + 1]["coordinates"]
        )
        total_distance += distance
    
    return total_distance


def _get_mock_directions(poi_index: int, target_poi: Dict[str, Any]) -> str:
    """Genera direcciones mock realistas basadas en ubicaciones reales"""
    
    directions_map = {
        0: "Dirígete hacia el centro histórico de Madrid por la Calle Mayor",
        1: "Camina hacia el oeste desde Plaza Mayor, está muy cerca",
        2: "Dirígete hacia el oeste por la Calle de Bailén hasta el Palacio",
        3: "Camina hacia la Plaza de Oriente, frente al Palacio Real", 
        4: "Dirígete hacia el este por la Calle Mayor hasta Puerta del Sol"
    }
    
    return directions_map.get(poi_index, f"Dirígete hacia {target_poi['name']}")


# Funciones preparadas para Google Maps (implementar cuando esté disponible)

def _get_google_directions(start_location: Dict[str, float], target_poi_index: int) -> str:
    """
    Obtiene direcciones reales de Google Maps
    
    TODO: Implementar cuando se tenga API key
    """
    
    # TODO: Implementar con Google Maps API
    # target_poi = MADRID_ROUTE[target_poi_index]
    # 
    # import googlemaps
    # gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    # 
    # directions = gmaps.directions(
    #     origin=f"{start_location['lat']},{start_location['lng']}",
    #     destination=f"{target_poi['coordinates']['lat']},{target_poi['coordinates']['lng']}",
    #     mode="walking",
    #     language="es"
    # )
    # 
    # return _process_google_directions(directions)
    
    # Fallback a mock
    return get_directions(start_location, target_poi_index)


def _process_google_directions(directions_result: List[Dict]) -> str:
    """Procesa resultado de Google Directions API"""
    
    # TODO: Implementar procesamiento de respuesta real de Google Maps
    # route = directions_result[0]
    # leg = route['legs'][0]
    # 
    # distance = leg['distance']['text']
    # duration = leg['duration']['text']
    # steps = [step['html_instructions'] for step in leg['steps']]
    # 
    # return f"Distancia: {distance}\nTiempo: {duration}\nInstrucciones: {' -> '.join(steps)}"
    
    pass


def enable_google_maps(api_key: str):
    """Habilita Google Maps con API key"""
    global USE_GOOGLE_MAPS, GOOGLE_MAPS_API_KEY
    USE_GOOGLE_MAPS = True
    GOOGLE_MAPS_API_KEY = api_key
    print("✅ Google Maps habilitado")


def disable_google_maps():
    """Deshabilita Google Maps (usar mock)"""
    global USE_GOOGLE_MAPS, GOOGLE_MAPS_API_KEY
    USE_GOOGLE_MAPS = False
    GOOGLE_MAPS_API_KEY = None
    print("📍 Usando navegación mock")


def get_poi_by_id(poi_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene información de un POI por su ID"""
    for poi in MADRID_ROUTE:
        if poi["id"] == poi_id:
            return poi
    return None


def get_poi_by_index(index: int) -> Optional[Dict[str, Any]]:
    """Obtiene información de un POI por su índice"""
    if 0 <= index < len(MADRID_ROUTE):
        return MADRID_ROUTE[index]
    return None