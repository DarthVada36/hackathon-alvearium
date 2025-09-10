#!/usr/bin/env python3
"""
Test de Coherencia del Ratoncito Pérez 
10 puntos reales de la Ruta del Ratoncito Pérez
"""

import asyncio
import aiohttp
import json
from typing import Optional, Dict, Any
import sys

class CoherenceAnalyzer:
    """Analizador de coherencia actualizado para la nueva ruta de 10 POIs"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        
        # RUTA REAL DEL RATONCITO PÉREZ - 10 PUNTOS
        self.raton_perez_pois = {
            "1": {
                "name": "Plaza de Oriente",
                "coords": {"lat": 40.4184, "lng": -3.7109},
                "description": "Plaza histórica frente al Palacio Real"
            },
            "2": {
                "name": "Plaza de Ramales", 
                "coords": {"lat": 40.4172, "lng": -3.7115},
                "description": "Pequeña plaza con historia arqueológica"
            },
            "3": {
                "name": "Calle Vergara",
                "coords": {"lat": 40.4169, "lng": -3.7095}, 
                "description": "Calle histórica del centro de Madrid"
            },
            "4": {
                "name": "Plaza de Isabel II",
                "coords": {"lat": 40.4180, "lng": -3.7088},
                "description": "Plaza junto al Teatro Real"
            },
            "5": {
                "name": "Calle del Arenal (Teatro)",
                "coords": {"lat": 40.4175, "lng": -3.7080},
                "description": "Famosa calle comercial madrileña"
            },
            "6": {
                "name": "Museo Ratoncito Pérez",
                "coords": {"lat": 40.4169, "lng": -3.7038},
                "description": "¡El hogar oficial del Ratoncito Pérez!"
            }
        }
        
        # TEST SCENARIOS ACTUALIZADOS CON COORDENADAS REALES
        self.test_scenarios = [
            {
                "name": "🏠 Saludo inicial sin ubicación",
                "message": "Hola Ratoncito Pérez, somos una familia que quiere explorar Madrid",
                "location": None,
                "expected_points_range": (0, 30),  # Chat inicial básico
                "expected_situation": "general_chat"
            },
            {
                "name": "📍 Llegada a Plaza de Oriente (POI 1)",
                "message": "¡Hemos llegado a la plaza!",
                "location": {"lat": 40.4184, "lng": -3.7109},  # Plaza de Oriente REAL
                "expected_points_range": (80, 120),  # Arrival points
                "expected_situation": "poi_arrival"
            },
            {
                "name": "❓ Pregunta sobre Plaza de Oriente",
                "message": "¿Qué puedes contarnos sobre este lugar?",
                "location": {"lat": 40.4184, "lng": -3.7109},  # Misma ubicación
                "expected_points_range": (50, 100),  # Question points
                "expected_situation": "location_question"
            },
            {
                "name": "😍 Engagement en Plaza de Oriente", 
                "message": "¡Qué lugar tan impresionante e histórico!",
                "location": {"lat": 40.4184, "lng": -3.7109},  # Misma ubicación
                "expected_points_range": (40, 80),   # Engagement points
                "expected_situation": "general_chat"
            },
            {
                "name": "🚶 Llegada a Plaza de Ramales (POI 2)",
                "message": "Hemos llegado al siguiente lugar de la ruta",
                "location": {"lat": 40.4172, "lng": -3.7115},  # Plaza de Ramales REAL
                "expected_points_range": (80, 120),  # Nuevo arrival
                "expected_situation": "poi_arrival"
            },
            {
                "name": "🧠 Test de memoria - lugares visitados",
                "message": "¿Dónde hemos estado antes en nuestra ruta?",
                "location": {"lat": 40.4172, "lng": -3.7115},  # Plaza de Ramales
                "expected_points_range": (0, 50),    # Pregunta simple
                "expected_context": "plaza de oriente"  # Debería recordar
            },
            {
                "name": "🗺️ Solicitud de navegación",
                "message": "¿Cómo llegamos al siguiente punto de la ruta?",
                "location": {"lat": 40.4172, "lng": -3.7115},  # Plaza de Ramales
                "expected_points_range": (0, 30),    # Navigation no da muchos puntos
                "expected_situation": "navigation"
            },
            {
                "name": "📚 Solicitud de historia específica",
                "message": "Cuéntanos alguna historia interesante de Madrid",
                "location": {"lat": 40.4169, "lng": -3.7095},  # Calle Vergara
                "expected_points_range": (0, 60),    # Story request
                "expected_situation": "story_request"
            },
            {
                "name": "🎯 Llegada al destino final",
                "message": "¡Por fin llegamos al Museo del Ratoncito Pérez!",
                "location": {"lat": 40.4169, "lng": -3.7038},  # Museo Ratoncito Pérez
                "expected_points_range": (80, 150),  # Final destination bonus
                "expected_situation": "poi_arrival"
            }
        ]
        
        # Timeout configuration
        self.timeout = aiohttp.ClientTimeout(total=30)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_test_family(self) -> bool:
        """Crea familia específica para la nueva ruta"""
        family_data = {
            "name": "Los Exploradores",
            "preferred_language": "es",
            "members": [
                {"name": "Carmen", "age": 35, "member_type": "adult"},
                {"name": "Miguel", "age": 38, "member_type": "adult"},
                {"name": "Sofía", "age": 9, "member_type": "child"},
                {"name": "Diego", "age": 12, "member_type": "child"}
            ]
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/families/", 
                json=family_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.family_id = data["id"]
                    print(f"✅ Familia 'Los Exploradores' creada (ID: {self.family_id})")
                    print(f"   👨‍👩‍👧‍👦 Carmen (35), Miguel (38), Sofía (9), Diego (12)")
                    return True
                else:
                    print(f"❌ Error creando familia: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def send_message_and_analyze(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Envía mensaje y analiza la respuesta"""
        
        chat_data = {
            "message": scenario["message"],
            "family_id": self.family_id,
        }
        
        if scenario.get("location"):
            chat_data["location"] = scenario["location"]
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/chat/message", 
                json=chat_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Análisis detallado
                    analysis = {
                        "success": True,
                        "response": data,
                        "points_earned": data.get("points_earned", 0),
                        "total_points": data.get("total_points", 0),
                        "situation": data.get("situation", "unknown"),
                        "agent_response": data.get("response", ""),
                        "achievements": data.get("achievements", []),
                        
                        # Análisis de coherencia
                        "points_coherent": False,
                        "situation_coherent": False,
                        "context_coherent": False,
                        "issues": []
                    }
                    
                    # Verificar coherencia de puntos
                    points = analysis["points_earned"]
                    expected_min, expected_max = scenario["expected_points_range"]
                    
                    if expected_min <= points <= expected_max:
                        analysis["points_coherent"] = True
                    else:
                        analysis["issues"].append(
                            f"Puntos incoherentes: {points} (esperado: {expected_min}-{expected_max})"
                        )
                    
                    # Verificar situación
                    if scenario.get("expected_situation"):
                        if analysis["situation"] == scenario["expected_situation"]:
                            analysis["situation_coherent"] = True
                        else:
                            analysis["issues"].append(
                                f"Situación incorrecta: '{analysis['situation']}' (esperado: '{scenario['expected_situation']}')"
                            )
                    
                    # Verificar contexto (si aplica)
                    if scenario.get("expected_context"):
                        context_keyword = scenario["expected_context"].lower()
                        agent_response_lower = analysis["agent_response"].lower()
                        if context_keyword in agent_response_lower:
                            analysis["context_coherent"] = True
                        else:
                            analysis["issues"].append(
                                f"Contexto perdido: no menciona '{context_keyword}'"
                            )
                    else:
                        analysis["context_coherent"] = True  # No aplica
                    
                    return analysis
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "issues": [f"Request failed: {error_text[:200]}"],
                        "points_coherent": False,
                        "situation_coherent": False,
                        "context_coherent": False
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "issues": [f"Network error: {e}"],
                "points_coherent": False,
                "situation_coherent": False,
                "context_coherent": False
            }
    
    def print_scenario_analysis(self, scenario: Dict, analysis: Dict):
        """Imprime análisis detallado de cada scenario"""
        
        print(f"\n{scenario['name']}")
        print("=" * 55)
        
        if not analysis.get("success"):
            print(f"❌ FALLÓ: {analysis.get('error', 'Error desconocido')}")
            if analysis.get("issues"):
                print("📋 Detalles del error:")
                for issue in analysis["issues"]:
                    print(f"   • {issue}")
            return
        
        # Input
        print(f"💬 Mensaje: '{scenario['message']}'")
        if scenario.get("location"):
            lat, lng = scenario["location"]["lat"], scenario["location"]["lng"]
            # Identificar POI por coordenadas
            poi_name = "Ubicación desconocida"
            for poi_id, poi_data in self.raton_perez_pois.items():
                poi_coords = poi_data["coords"]
                distance = ((lat - poi_coords["lat"])**2 + (lng - poi_coords["lng"])**2)**0.5 * 111000  # Aprox km to m
                if distance < 100:  # Dentro de 100m
                    poi_name = poi_data["name"]
                    break
            print(f"📍 Ubicación: {poi_name} ({lat:.4f}, {lng:.4f})")
        
        # Output del agente
        response_preview = analysis["agent_response"][:150] + "..." if len(analysis["agent_response"]) > 150 else analysis["agent_response"]
        print(f"🐭 Respuesta: {response_preview}")
        
        # Métricas
        print(f"\n📊 MÉTRICAS:")
        print(f"   🎯 Puntos ganados: {analysis['points_earned']}")
        if analysis.get('achievements'):
            print(f"   🏆 Logros: {', '.join(analysis.get('achievements', []))}")
        print(f"   📍 Situación detectada: {analysis['situation']}")
        print(f"   💯 Puntos totales: {analysis['total_points']}")
        
        # Análisis de coherencia
        print(f"\n🔍 ANÁLISIS DE COHERENCIA:")
        
        coherence_score = 0
        total_checks = 3
        
        if analysis.get("points_coherent"):
            print("   ✅ Puntos coherentes")
            coherence_score += 1
        else:
            print("   ❌ Puntos incoherentes")
        
        if analysis.get("situation_coherent"):
            print("   ✅ Situación correcta")
            coherence_score += 1
        else:
            print("   ❌ Situación incorrecta")
        
        if analysis.get("context_coherent"):
            print("   ✅ Contexto mantenido")
            coherence_score += 1
        else:
            print("   ❌ Contexto perdido")
        
        # Issues específicos
        if analysis.get("issues"):
            print(f"\n⚠️  PROBLEMAS DETECTADOS:")
            for issue in analysis["issues"]:
                print(f"   • {issue}")
        
        # Score final
        percentage = (coherence_score / total_checks) * 100
        if percentage >= 80:
            print(f"\n🟢 COHERENCIA: {percentage:.1f}% - EXCELENTE")
        elif percentage >= 60:
            print(f"\n🟡 COHERENCIA: {percentage:.1f}% - ACEPTABLE")
        else:
            print(f"\n🔴 COHERENCIA: {percentage:.1f}% - NECESITA MEJORAS")
    
    async def get_family_status(self) -> Dict:
        """Obtiene estado detallado de la familia"""
        try:
            async with self.session.get(
                f"{self.base_url}/api/chat/family/{self.family_id}/status"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Status code: {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def run_coherence_analysis(self):
        """Ejecuta análisis completo de coherencia con nueva ruta"""
        
        print("🔍 ANÁLISIS DE COHERENCIA - RUTA RATONCITO PÉREZ 2.0")
        print("=" * 65)
        print("🗺️ Nueva ruta de 10 POIs en el centro histórico de Madrid")
        print("🎯 Testeando lógica de puntos, ubicaciones y contexto...\n")
        
        # Crear familia
        if not await self.create_test_family():
            return False
        
        # Ejecutar scenarios
        results = []
        total_coherence = 0
        
        for i, scenario in enumerate(self.test_scenarios, 1):
            print(f"\n{'='*15} TEST {i}/{len(self.test_scenarios)} {'='*15}")
            
            analysis = await self.send_message_and_analyze(scenario)
            results.append((scenario, analysis))
            
            self.print_scenario_analysis(scenario, analysis)
            
            if analysis.get("success"):
                # Calcular coherencia de este scenario
                coherent_checks = sum([
                    analysis.get("points_coherent", False),
                    analysis.get("situation_coherent", False), 
                    analysis.get("context_coherent", False)
                ])
                scenario_coherence = (coherent_checks / 3) * 100
                total_coherence += scenario_coherence
            
            # Pausa entre tests
            await asyncio.sleep(2)
        
        # Resumen final
        print(f"\n{'='*25} RESUMEN FINAL {'='*25}")
        
        average_coherence = total_coherence / len(self.test_scenarios)
        print(f"🎯 COHERENCIA PROMEDIO: {average_coherence:.1f}%")
        
        # Estado final de la familia
        family_status = await self.get_family_status()
        if not family_status.get("error"):
            print(f"\n👨‍👩‍👧‍👦 ESTADO FINAL DE LA FAMILIA:")
            print(f"   🎯 Puntos totales: {family_status.get('total_points', 0)}")
            print(f"   📍 POI actual: {family_status.get('current_poi', 0)}")
            print(f"   🗺️ POIs visitados: {family_status.get('visited_pois', 0)}/10")
            print(f"   📈 Progreso: {family_status.get('completion_percentage', 0):.1f}%")
        
        # Recomendaciones mejoradas
        print(f"\n💡 EVALUACIÓN DEL SISTEMA:")
        if average_coherence >= 85:
            print("   🚀 SISTEMA EXCELENTE - Perfecto para hackathon y producción")
        elif average_coherence >= 75:
            print("   ⚡ SISTEMA MUY BUENO - Listo para hackathon")
        elif average_coherence >= 60:
            print("   ✅ SISTEMA FUNCIONAL - Apto para demo con ajustes menores")
        else:
            print("   🔧 SISTEMA NECESITA MEJORAS - Revisar antes de demo")
        
        # Issues más comunes
        all_issues = []
        for _, analysis in results:
            all_issues.extend(analysis.get("issues", []))
        
        if all_issues:
            from collections import Counter
            common_issues = Counter(all_issues).most_common(5)
            print(f"\n🚨 PROBLEMAS MÁS FRECUENTES:")
            for issue, count in common_issues:
                print(f"   • {issue} ({count}x)")
        
        # Análisis por categorías
        successful_tests = sum(1 for _, analysis in results if analysis.get("success"))
        print(f"\n📊 ESTADÍSTICAS DETALLADAS:")
        print(f"   ✅ Tests exitosos: {successful_tests}/{len(self.test_scenarios)}")
        print(f"   🎯 Coherencia promedio: {average_coherence:.1f}%")
        print(f"   🗺️ Ruta nueva: 10 POIs reales de Madrid")
        
        return average_coherence >= 60


async def main():
    """Función principal mejorada"""
    print("🎭 TEST DE COHERENCIA")
    
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"🌐 Servidor: {base_url}")
    print("🗺️  Usando nueva ruta de 10 POIs del centro histórico de Madrid")
    
    try:
        async with CoherenceAnalyzer(base_url) as analyzer:
            success = await analyzer.run_coherence_analysis()
            
            if success:
                print("\n🎉 ¡ANÁLISIS COMPLETADO CON ÉXITO!")
                print("🚀 El Ratoncito Pérez está listo para guiar familias por Madrid")
            else:
                print("\n⚠️  ANÁLISIS COMPLETADO - Se detectaron áreas de mejora")
                print("💡 Revisa los problemas identificados arriba")
                
    except Exception as e:
        print(f"\n💥 Error crítico: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        import aiohttp
        asyncio.run(main())
    except ImportError:
        print("❌ Instala aiohttp: pip install aiohttp")
    except KeyboardInterrupt:
        print("\n⏹️  Test interrumpido")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)