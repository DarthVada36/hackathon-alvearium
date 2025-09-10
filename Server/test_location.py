#!/usr/bin/env python3
"""
Test simple del location_helper - IMPORTS CORREGIDOS
"""

import asyncio
import sys
import os

# Añadir el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

async def test_location_helper():
    """Test básico de las funciones"""
    print("🧪 Testing location_helper con OpenStreetMap...")
    
    try:
        # IMPORTS CORREGIDOS - sin 'Server.' al principio
        from core.agents.location_helper import (
            check_poi_arrival, 
            get_directions_osm, 
            find_nearest_poi,
            get_route_overview
        )
        
        print("✅ Imports exitosos!")
        
        # Test 1: Llegada a Plaza de Oriente
        print("\n1️⃣ Test: Llegada a Plaza de Oriente")
        location = {"lat": 40.4184, "lng": -3.7109}
        result = await check_poi_arrival(location)
        print(f"   Resultado: {result}")
        
        # Test 2: Buscar POI más cercano
        print("\n2️⃣ Test: POI más cercano")
        nearest = find_nearest_poi(location)
        print(f"   Más cercano: {nearest.get('poi_name', 'N/A')} ({nearest.get('distance_meters', 'N/A')}m)")
        
        # Test 3: Overview de la ruta
        print("\n3️⃣ Test: Vista general de la ruta")
        overview = get_route_overview()
        print(f"   Total POIs: {overview['total_pois']}")
        print(f"   Distancia total: {overview['estimated_walking_distance']}")
        print(f"   Tiempo total: {overview['estimated_total_time']}")
        
        print("\n✅ Tests básicos completados!")
        
        # Test 4: Direcciones con API (puede tardar)
        print("\n4️⃣ Test: Direcciones reales OSM (puede tardar unos segundos)...")
        try:
            directions = await get_directions_osm(location, 1)  # Al segundo POI
            print(f"   Direcciones: {directions[:200]}...")
        except Exception as e:
            print(f"   Error en direcciones: {e}")
        
        print("\n🎉 ¡Todos los tests completados!")
        
    except ImportError as e:
        print(f"❌ Error de import: {e}")
        print("💡 Posibles soluciones:")
        print("   1. Verifica que estés en la carpeta 'Server' (o 'server')")
        print("   2. Verifica que existe core/agents/location_helper.py")
        print("   3. Ejecuta: pip install aiohttp")
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Verificar estructura primero
    print(f"📁 Directorio actual: {os.getcwd()}")
    print(f"📁 Archivos aquí: {os.listdir('.')}")
    
    if os.path.exists('core/agents/location_helper.py'):
        print("✅ Archivo location_helper.py encontrado")
        asyncio.run(test_location_helper())
    else:
        print("❌ No se encuentra core/agents/location_helper.py")
        print("💡 Asegúrate de estar en la carpeta correcta y que el archivo exista")