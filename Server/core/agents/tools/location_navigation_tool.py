"""
Location Navigation Tool - Sistema de navegación para la ruta del Ratoncito Pérez
Herramienta mock para desarrollo, preparada para Google Maps API u otras APIs gratuitas de mapas
"""

from typing import Dict, Any, Optional, List, Tuple
from langchain_core.tools import Tool
import math
import sys
import os

# Imports para integración futura con Google Maps u otras apis gratuitas de mapas
# import googlemaps

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))


class LocationNavigationToolError(Exception):
    """Errores específicos de la herramienta de navegación"""
    pass


class LocationNavigationTool:
    """Herramienta de navegación con datos mock de Madrid"""
    
    def __init__(self, use_google_maps: bool = False, api_key: Optional[str] = None):
        self.use_google_maps = use_google_maps
        self.api_key = api_key
        # self.gmaps_client = googlemaps.Client(key=api_key) if use_google_maps and api_key else None
        
        # Datos mock de la ruta del Ratoncito Pérez en Madrid
        self.route_pois = self._initialize_madrid_route()
        
    def _initialize_madrid_route(self) -> List[Dict[str, Any]]:
        """Ruta predefinida del Ratoncito Pérez con coordenadas reales de Madrid"""
        return [
            {
                "id": "plaza_mayor",
                "name": "Plaza Mayor",
                "coordinates": {"lat": 40.4155, "lng": -3.7074},
                "address": "Plaza Mayor, 28012 Madrid, España",
                "description": "El corazón histórico de Madrid",
                "visit_duration": 20,  # minutos
                "walking_area": True
            },
            {
                "id": "mercado_san_miguel", 
                "name": "Mercado de San Miguel",
                "coordinates": {"lat": 40.4154, "lng": -3.7085},
                "address": "Plaza de San Miguel, s/n, 28005 Madrid, España", 
                "description": "Mercado gastronómico histórico",
                "visit_duration": 25,
                "walking_area": True
            },
            {
                "id": "palacio_real",
                "name": "Palacio Real",
                "coordinates": {"lat": 40.4179, "lng": -3.7143},
                "address": "C. de Bailén, s/n, 28071 Madrid, España",
                "description": "Residencia oficial de la Familia Real Española", 
                "visit_duration": 30,
                "walking_area": False
            },
            {
                "id": "teatro_real",
                "name": "Teatro Real",
                "coordinates": {"lat": 40.4184, "lng": -3.7109},
                "address": "Plaza de Oriente, s/n, 28013 Madrid, España",
                "description": "Teatro de ópera histórico de Madrid",
                "visit_duration": 15,
                "walking_area": False  
            },
            {
                "id": "puerta_del_sol",
                "name": "Puerta del Sol", 
                "coordinates": {"lat": 40.4168, "lng": -3.7038},
                "address": "Puerta del Sol, 28013 Madrid, España",
                "description": "Kilómetro cero de España",
                "visit_duration": 20,
                "walking_area": True
            }
        ]
    
    def calculate_distance_between_points(self, point1: Dict[str, float], 
                                        point2: Dict[str, float]) -> float:
        """
        Calcula distancia en metros entre dos coordenadas usando fórmula de Haversine
        
        Args:
            point1: {"lat": float, "lng": float}
            point2: {"lat": float, "lng": float}
        
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
    
    def find_nearest_poi(self, current_location: Dict[str, float], 
                        visited_pois: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Encuentra el POI más cercano no visitado
        
        Args:
            current_location: Ubicación actual {"lat": float, "lng": float}
            visited_pois: Lista de IDs de POIs ya visitados
        
        Returns:
            Información del POI más cercano
        """
        if visited_pois is None:
            visited_pois = []
            
        available_pois = [poi for poi in self.route_pois if poi["id"] not in visited_pois]
        
        if not available_pois:
            return {"error": "No hay más POIs disponibles en la ruta"}
        
        nearest_poi = None
        min_distance = float('inf')
        
        for poi in available_pois:
            distance = self.calculate_distance_between_points(
                current_location, poi["coordinates"]
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest_poi = poi
        
        if nearest_poi:
            nearest_poi["distance_meters"] = round(min_distance, 1)
            nearest_poi["walking_time"] = self._estimate_walking_time(min_distance)
        
        return nearest_poi
    
    def get_directions_to_poi(self, current_location: Dict[str, float], 
                            target_poi_id: str) -> Dict[str, Any]:
        """
        Obtiene direcciones desde ubicación actual hasta POI específico
        
        Args:
            current_location: Ubicación actual
            target_poi_id: ID del POI destino
        
        Returns:
            Información de navegación
        """
        target_poi = self._find_poi_by_id(target_poi_id)
        
        if not target_poi:
            return {"error": f"POI '{target_poi_id}' no encontrado en la ruta"}
        
        if self.use_google_maps and self.api_key:
            return self._get_google_directions(current_location, target_poi)
        else:
            return self._get_mock_directions(current_location, target_poi)
    
    def check_arrival_at_poi(self, current_location: Dict[str, float], 
                           poi_id: str, threshold_meters: int = 50) -> Dict[str, Any]:
        """
        Verifica si la familia ha llegado a un POI específico
        
        Args:
            current_location: Ubicación actual
            poi_id: ID del POI a verificar
            threshold_meters: Distancia mínima para considerar "llegada"
        
        Returns:
            Información sobre la llegada
        """
        target_poi = self._find_poi_by_id(poi_id)
        
        if not target_poi:
            return {"arrived": False, "error": f"POI '{poi_id}' no encontrado"}
        
        distance = self.calculate_distance_between_points(
            current_location, target_poi["coordinates"]
        )
        
        arrived = distance <= threshold_meters
        
        return {
            "arrived": arrived,
            "poi_name": target_poi["name"],
            "distance_meters": round(distance, 1),
            "threshold": threshold_meters,
            "message": f"{'¡Habéis llegado!' if arrived else f'Os faltan {round(distance, 1)}m para llegar'} a {target_poi['name']}"
        }
    
    def get_route_overview(self, current_location: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Obtiene vista general de la ruta completa
        
        Args:
            current_location: Ubicación actual (opcional)
        
        Returns:
            Información completa de la ruta
        """
        route_info = {
            "total_pois": len(self.route_pois),
            "estimated_total_time": sum(poi["visit_duration"] for poi in self.route_pois),
            "total_walking_distance": self._calculate_total_route_distance(),
            "pois": []
        }
        
        for i, poi in enumerate(self.route_pois):
            poi_info = poi.copy()
            poi_info["order"] = i + 1
            
            if current_location:
                distance = self.calculate_distance_between_points(
                    current_location, poi["coordinates"]
                )
                poi_info["distance_from_current"] = round(distance, 1)
                poi_info["walking_time_from_current"] = self._estimate_walking_time(distance)
            
            route_info["pois"].append(poi_info)
        
        return route_info
    
    def suggest_next_poi(self, current_poi_index: int, 
                        current_location: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Sugiere el próximo POI en la ruta
        
        Args:
            current_poi_index: Índice del POI actual
            current_location: Ubicación actual (opcional)
        
        Returns:
            Información del próximo POI recomendado
        """
        if current_poi_index >= len(self.route_pois) - 1:
            return {
                "completed": True,
                "message": "¡Habéis completado toda la ruta del Ratoncito Pérez! ¡Enhorabuena!"
            }
        
        next_poi = self.route_pois[current_poi_index + 1]
        suggestion = {
            "next_poi": next_poi,
            "completed": False,
            "message": f"¡Vuestro próximo destino es {next_poi['name']}!"
        }
        
        if current_location:
            current_poi = self.route_pois[current_poi_index]
            distance = self.calculate_distance_between_points(
                current_poi["coordinates"], next_poi["coordinates"]
            )
            suggestion["distance_meters"] = round(distance, 1)
            suggestion["walking_time"] = self._estimate_walking_time(distance)
            suggestion["directions"] = self._get_mock_directions(
                current_poi["coordinates"], next_poi
            )
        
        return suggestion
    
    def _find_poi_by_id(self, poi_id: str) -> Optional[Dict[str, Any]]:
        """Encuentra un POI por su ID"""
        for poi in self.route_pois:
            if poi["id"] == poi_id:
                return poi
        return None
    
    def _estimate_walking_time(self, distance_meters: float) -> Dict[str, Any]:
        """Estima tiempo de caminata (velocidad promedio: 4 km/h)"""
        walking_speed_mps = 4000 / 3600  # 4 km/h en metros/segundo
        time_seconds = distance_meters / walking_speed_mps
        
        minutes = int(time_seconds // 60)
        seconds = int(time_seconds % 60)
        
        return {
            "total_seconds": int(time_seconds),
            "minutes": minutes,
            "display": f"{minutes}m {seconds}s" if seconds > 0 else f"{minutes}m"
        }
    
    def _calculate_total_route_distance(self) -> float:
        """Calcula distancia total de la ruta completa"""
        total_distance = 0
        
        for i in range(len(self.route_pois) - 1):
            distance = self.calculate_distance_between_points(
                self.route_pois[i]["coordinates"],
                self.route_pois[i + 1]["coordinates"]
            )
            total_distance += distance
        
        return round(total_distance, 1)
    
    def _get_mock_directions(self, start_location: Dict[str, float], 
                           target_poi: Dict[str, Any]) -> Dict[str, Any]:
        """Genera direcciones mock realistas"""
        distance = self.calculate_distance_between_points(
            start_location, target_poi["coordinates"]
        )
        
        # Direcciones simplificadas basadas en ubicaciones reales
        directions_map = {
            "plaza_mayor": "Dirígete hacia el centro histórico por la Calle Mayor",
            "mercado_san_miguel": "Camina hacia el oeste desde Plaza Mayor, está muy cerca",
            "palacio_real": "Dirígete hacia el oeste por la Calle de Bailén",
            "teatro_real": "Camina hacia la Plaza de Oriente, frente al Palacio Real", 
            "puerta_del_sol": "Dirígete hacia el este por la Calle Mayor hasta el centro"
        }
        
        return {
            "distance": round(distance, 1),
            "duration": self._estimate_walking_time(distance),
            "instructions": directions_map.get(target_poi["id"], "Dirígete hacia tu destino"),
            "start_address": "Ubicación actual",
            "end_address": target_poi["address"]
        }
    
    # Preparado para Google Maps (implementar cuando se tenga API key)
    def _get_google_directions(self, start_location: Dict[str, float], 
                             target_poi: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene direcciones reales de Google Maps"""
        # TODO: Implementar cuando se tenga API key
        # directions = self.gmaps_client.directions(
        #     origin=f"{start_location['lat']},{start_location['lng']}",
        #     destination=f"{target_poi['coordinates']['lat']},{target_poi['coordinates']['lng']}",
        #     mode="walking"
        # )
        # return self._process_google_directions(directions)
        
        # Fallback a mock por ahora
        return self._get_mock_directions(start_location, target_poi)


# Crear instancia de la herramienta
location_navigation_tool_instance = LocationNavigationTool(use_google_maps=False)

# Crear herramientas de LangChain
def create_location_navigation_tools() -> List[Tool]:
    """Crea herramientas de LangChain para navegación"""
    
    tools = []
    
    # Herramienta para encontrar POI más cercano
    tools.append(Tool(
        name="find_nearest_poi",
        description="Encuentra el POI más cercano no visitado. Input: coordenadas actuales como 'lat,lng'",
        func=lambda coords: location_navigation_tool_instance.find_nearest_poi(
            _parse_coordinates(coords)
        )
    ))
    
    # Herramienta para obtener direcciones
    tools.append(Tool(
        name="get_directions",
        description="Obtiene direcciones a un POI específico. Input: 'coordenadas_actuales|poi_id'",
        func=lambda input_str: _handle_directions_input(input_str)
    ))
    
    # Herramienta para verificar llegada
    tools.append(Tool(
        name="check_poi_arrival",
        description="Verifica si se ha llegado a un POI. Input: 'coordenadas_actuales|poi_id'", 
        func=lambda input_str: _handle_arrival_check(input_str)
    ))
    
    # Herramienta para vista general de ruta
    tools.append(Tool(
        name="route_overview",
        description="Obtiene información completa de la ruta. Input: coordenadas actuales (opcional)",
        func=lambda coords="": location_navigation_tool_instance.get_route_overview(
            _parse_coordinates(coords) if coords else None
        )
    ))
    
    return tools


# Helper functions para parsing de inputs
def _parse_coordinates(coord_string: str) -> Dict[str, float]:
    """Parsea string de coordenadas a diccionario"""
    try:
        if not coord_string.strip():
            return {"lat": 40.4168, "lng": -3.7038}  # Puerta del Sol por defecto
        
        lat, lng = coord_string.split(",")
        return {"lat": float(lat.strip()), "lng": float(lng.strip())}
    except:
        return {"lat": 40.4168, "lng": -3.7038}  # Fallback

def _handle_directions_input(input_str: str) -> Dict[str, Any]:
    """Maneja input para direcciones"""
    try:
        coords_str, poi_id = input_str.split("|")
        coords = _parse_coordinates(coords_str)
        return location_navigation_tool_instance.get_directions_to_poi(coords, poi_id.strip())
    except:
        return {"error": "Format: 'lat,lng|poi_id'"}

def _handle_arrival_check(input_str: str) -> Dict[str, Any]:
    """Maneja input para verificación de llegada"""
    try:
        coords_str, poi_id = input_str.split("|")
        coords = _parse_coordinates(coords_str)
        return location_navigation_tool_instance.check_arrival_at_poi(coords, poi_id.strip())
    except:
        return {"error": "Format: 'lat,lng|poi_id'"}


# Helper para uso directo
def check_location_proximity(current_coords: Dict[str, float], poi_id: str) -> bool:
    """Helper para verificar proximidad rápida"""
    result = location_navigation_tool_instance.check_arrival_at_poi(current_coords, poi_id)
    return result.get("arrived", False)