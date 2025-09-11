#!/usr/bin/env python3
"""
Test script para verificar que la funcionalidad consolidada de Wikipedia funciona correctamente
Verifica tanto las funciones en madrid_apis como la compatibilidad en madrid_knowledge
"""

import sys
import os
import logging

# Añadir el directorio Server al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Server'))

def test_consolidated_wikipedia():
    """Prueba la funcionalidad consolidada de Wikipedia"""
    print("=" * 60)
    print("🧪 PRUEBA DE WIKIPEDIA CONSOLIDADA")
    print("=" * 60)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Probar MadridPlace directamente
    print("\n1️⃣ Probando MadridPlace.fetch_wikipedia_summary()...")
    try:
        from Server.core.services.madrid_apis import MadridPlace
        
        # Crear instancia de prueba
        test_place = MadridPlace(name="Palacio Real", place_id="test", categories=["landmark"])
        
        # Probar función consolidada
        summary = test_place.fetch_wikipedia_summary()
        
        if summary and len(summary) > 50:
            print(f"✅ MadridPlace: Éxito - {len(summary)} caracteres")
            print(f"   Contenido: {summary[:100]}...")
            success_count += 1
        else:
            print(f"❌ MadridPlace: Fallo - contenido insuficiente ({len(summary or '')} chars)")
            
        total_tests += 1
        
    except Exception as e:
        print(f"❌ MadridPlace: Error - {e}")
        total_tests += 1
    
    # Test 2: Probar funciones de cache
    print("\n2️⃣ Probando funciones de cache consolidadas...")
    try:
        from Server.core.services.madrid_apis import get_wikipedia_cache_info, clear_wikipedia_cache
        
        # Obtener info del cache
        cache_info = get_wikipedia_cache_info()
        print(f"✅ Cache info: {cache_info['total_entries']} entradas totales")
        print(f"   Válidas: {cache_info['valid_entries']}, Expiradas: {cache_info['expired_entries']}")
        
        # Probar limpieza de cache
        clear_wikipedia_cache()
        cache_info_after = get_wikipedia_cache_info()
        
        if cache_info_after['total_entries'] == 0:
            print("✅ Limpieza de cache: Éxito")
            success_count += 1
        else:
            print(f"❌ Limpieza de cache: Fallo - quedan {cache_info_after['total_entries']} entradas")
        
        total_tests += 1
        
    except Exception as e:
        print(f"❌ Funciones de cache: Error - {e}")
        total_tests += 1
    
    # Test 3: Probar compatibilidad con madrid_knowledge
    print("\n3️⃣ Probando compatibilidad con madrid_knowledge...")
    try:
        from Server.core.agents.madrid_knowledge import fetch_wikipedia_content
        
        # Probar función wrapper
        result = fetch_wikipedia_content("Teatro Real", use_cache=False)
        
        if result and result.get("success") and len(result.get("basic_info", "")) > 50:
            print(f"✅ Wrapper compatibilidad: Éxito - {len(result['basic_info'])} caracteres")
            print(f"   Título: {result.get('title', 'N/A')}")
            print(f"   Variant used: {result.get('variant_used', 'N/A')}")
            success_count += 1
        else:
            print(f"❌ Wrapper compatibilidad: Fallo - {result}")
            
        total_tests += 1
        
    except Exception as e:
        print(f"❌ Wrapper compatibilidad: Error - {e}")
        total_tests += 1
    
    # Test 4: Probar múltiples POIs conocidos
    print("\n4️⃣ Probando múltiples POIs conocidos...")
    test_pois = ["Plaza Mayor", "Puerta del Sol", "Palacio Real"]
    poi_success = 0
    
    try:
        from Server.core.services.madrid_apis import MadridPlace
        
        for poi in test_pois:
            try:
                test_place = MadridPlace(name=poi, place_id=f"test_{poi.replace(' ', '_')}", categories=["landmark"])
                summary = test_place.fetch_wikipedia_summary()
                
                if summary and len(summary) > 50:
                    print(f"✅ {poi}: {len(summary)} chars")
                    poi_success += 1
                else:
                    print(f"❌ {poi}: contenido insuficiente")
                    
            except Exception as e:
                print(f"❌ {poi}: Error - {e}")
        
        if poi_success == len(test_pois):
            success_count += 1
            
        total_tests += 1
        
    except Exception as e:
        print(f"❌ Múltiples POIs: Error - {e}")
        total_tests += 1
    
    # Resultados finales
    print("\n" + "=" * 60)
    print("📊 RESULTADOS FINALES")
    print("=" * 60)
    print(f"✅ Pruebas exitosas: {success_count}/{total_tests}")
    print(f"📈 Tasa de éxito: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! Wikipedia consolidada funciona correctamente")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar implementación.")
        return False

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Ejecutar pruebas
    success = test_consolidated_wikipedia()
    
    # Salir con código apropiado
    sys.exit(0 if success else 1)
