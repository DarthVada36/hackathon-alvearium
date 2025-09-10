"""
Location Helper - Versión simplificada para DEMO
Itinerario fijo controlado por botón "Siguiente punto"
"""

from typing import Dict, Any, Optional, List

#  Ruta del Ratoncito Pérez, 10 POIs
RATON_PEREZ_ROUTE = [
    {
        "id": "plaza_oriente",
        "name": "Plaza de Oriente",
        "address": "Plaza de Oriente, Madrid, España",
        "description": "Plaza histórica frente al Palacio Real",
        "visit_duration": 15,
        "index": 0
    },
    {
        "id": "plaza_ramales",
        "name": "Plaza de Ramales",
        "address": "Plaza de Ramales, Madrid, España",
        "description": "Pequeña plaza con historia arqueológica",
        "visit_duration": 10,
        "index": 1
    },
    {
        "id": "calle_vergara",
        "name": "Calle Vergara",
        "address": "Calle de Vergara, Madrid, España",
        "description": "Calle histórica del centro de Madrid",
        "visit_duration": 8,
        "index": 2
    },
    {
        "id": "plaza_isabel_ii",
        "name": "Plaza de Isabel II",
        "address": "Plaza de Isabel II, Madrid, España",
        "description": "Plaza junto al Teatro Real",
        "visit_duration": 12,
        "index": 3
    },
    {
        "id": "calle_arenal_1",
        "name": "Calle del Arenal (Teatro)",
        "address": "Calle del Arenal, Madrid, España",
        "description": "Famosa calle comercial madrileña",
        "visit_duration": 10,
        "index": 4
    },
    {
        "id": "calle_bordadores",
        "name": "Calle de Bordadores",
        "address": "Calle de Bordadores, Madrid, España",
        "description": "Calle de artesanos tradicionales",
        "visit_duration": 8,
        "index": 5
    },
    {
        "id": "plazuela_san_gines",
        "name": "Plazuela de San Ginés",
        "address": "Plazuela de San Ginés, Madrid, España",
        "description": "Rincón histórico junto a la iglesia",
        "visit_duration": 10,
        "index": 6
    },
    {
        "id": "pasadizo_san_gines",
        "name": "Pasadizo de San Ginés",
        "address": "Pasadizo de San Ginés, Madrid, España",
        "description": "Famoso por la chocolatería centenaria",
        "visit_duration": 15,
        "index": 7
    },
    {
        "id": "calle_arenal_2",
        "name": "Calle del Arenal (Sol)",
        "address": "Calle del Arenal, Madrid, España",
        "description": "Tramo hacia Puerta del Sol",
        "visit_duration": 8,
        "index": 8
    },
    {
        "id": "museo_raton_perez",
        "name": "Museo Ratoncito Pérez",
        "address": "Calle del Arenal, 8, 28013 Madrid, España",
        "description": "¡El hogar oficial del Ratoncito Pérez!",
        "visit_duration": 20,
        "index": 9
    }
]


# Funciones  

def force_poi_arrival(poi_id: str) -> Dict[str, Any]:
    """
    Simula llegada directa a un POI para la demo.
    Se usa cuando el front pulsa "Siguiente punto".
    """
    poi = get_poi_by_id(poi_id)
    if not poi:
        return {"arrived": False, "error": f"POI '{poi_id}' no encontrado"}

    return {
        "arrived": True,
        "poi_id": poi["id"],
        "poi_name": poi["name"],
        "poi_index": poi["index"],
        "message": f"¡Habéis llegado a {poi['name']} (simulado)!",
    }


def get_poi_by_id(poi_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene información de un POI por su ID"""
    for poi in RATON_PEREZ_ROUTE:
        if poi["id"] == poi_id:
            return poi
    return None


def get_poi_by_index(index: int) -> Optional[Dict[str, Any]]:
    """Obtiene un POI por su índice"""
    if 0 <= index < len(RATON_PEREZ_ROUTE):
        return RATON_PEREZ_ROUTE[index]
    return None


def get_total_pois() -> int:
    """Devuelve el número total de POIs"""
    return len(RATON_PEREZ_ROUTE)
