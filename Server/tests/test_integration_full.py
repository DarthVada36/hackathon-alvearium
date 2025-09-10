"""
Test de integración completo del Ratoncito Pérez Digital
Prueba todo el flujo: API + Chat + Pinecone + Base de datos
"""

import pytest
import asyncio
import requests
import time
from typing import Dict, Any

# Configuración del test
BASE_URL = "http://localhost:8000"
TEST_FAMILY_NAME = "Familia Test Integración"
TEST_TIMEOUT = 30  # segundos

class TestRatonPerezIntegration:
    """Test de integración completa de la aplicación"""
    
    @classmethod
    def setup_class(cls):
        """Setup inicial - verificar que el servidor esté funcionando"""
        print("\n🚀 Iniciando test de integración completo...")
        cls.family_id = None
        cls.total_points = 0
        
        # Verificar que el servidor esté up
        try:
            response = requests.get(f"{BASE_URL}/", timeout=10)
            assert response.status_code == 200
            print("✅ Servidor funcionando correctamente")
        except Exception as e:
            pytest.fail(f"❌ Servidor no está disponible en {BASE_URL}: {e}")
    
    def test_01_health_check(self):
        """Test 1: Verificar salud del sistema"""
        print("\n🏥 Test 1: Health Check del sistema...")
        
        # Probar diferentes endpoints de health posibles
        health_endpoints = ["/health", "/healthz", "/api/health"]
        health_data = None
        
        for endpoint in health_endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}")
                if response.status_code == 200:
                    health_data = response.json()
                    print(f"   Health endpoint encontrado: {endpoint}")
                    break
            except:
                continue
        
        # Si no hay health endpoint, verificar que al menos el servidor responda
        if not health_data:
            response = requests.get(f"{BASE_URL}/")
            assert response.status_code == 200
            print(f"   Servidor funcionando en root endpoint")
            health_data = {"status": "healthy", "database": "unknown"}
        
        print(f"   Estado: {health_data.get('status', 'unknown')}")
        print(f"   Base de datos: {health_data.get('database', 'unknown')}")
        
        print("✅ Sistema saludable")
    
    def test_02_create_family(self):
        """Test 2: Crear familia de prueba"""
        print("\n👨‍👩‍👧‍👦 Test 2: Creando familia de prueba...")
        
        family_data = {
            "name": TEST_FAMILY_NAME,
            "preferred_language": "es",
            "members": [
                {"name": "Ana", "age": 35, "member_type": "adult"},
                {"name": "Carlos", "age": 37, "member_type": "adult"},
                {"name": "Sofia", "age": 8, "member_type": "child"},
                {"name": "Pablo", "age": 5, "member_type": "child"}
            ]
        }
        
        response = requests.post(f"{BASE_URL}/api/families/", json=family_data)
        assert response.status_code == 200
        
        family_response = response.json()
        self.__class__.family_id = family_response["id"]
        
        print(f"   Familia creada con ID: {self.family_id}")
        print(f"   Nombre: {family_response['name']}")
        print(f"   Miembros: {len(family_response['members'])}")
        
        assert family_response["name"] == TEST_FAMILY_NAME
        assert len(family_response["members"]) == 4
        
        print("✅ Familia creada exitosamente")
    
    def test_03_get_family_info(self):
        """Test 3: Obtener información de la familia"""
        print(f"\n📋 Test 3: Obteniendo info de familia {self.family_id}...")
        
        response = requests.get(f"{BASE_URL}/api/families/{self.family_id}")
        assert response.status_code == 200
        
        family_data = response.json()
        print(f"   Familia: {family_data['name']}")
        print(f"   Idioma: {family_data['preferred_language']}")
        
        assert family_data["id"] == self.family_id
        assert family_data["name"] == TEST_FAMILY_NAME
        
        print("✅ Información de familia obtenida")
    
    def test_04_initial_chat_arrival(self):
        """Test 4: Chat inicial - llegada a Plaza de Oriente"""
        print(f"\n💬 Test 4: Chat inicial - Llegada al primer POI...")
        
        chat_data = {
            "family_id": self.family_id,
            "message": "¡Hola Ratoncito Pérez! ¡Estamos muy emocionados!",
            "speaker_name": "Sofia"
        }
        
        response = requests.post(f"{BASE_URL}/api/chat/message", json=chat_data)
        assert response.status_code == 200
        
        chat_response = response.json()
        print(f"   Éxito: {chat_response.get('success')}")
        print(f"   Puntos ganados: {chat_response.get('points_earned')}")
        print(f"   Situación: {chat_response.get('situation')}")
        print(f"   Respuesta: {chat_response.get('response')[:100]}...")
        
        assert chat_response["success"] is True
        assert chat_response["points_earned"] == 100  # Puntos de llegada
        assert "Plaza de Oriente" in chat_response["response"]
        
        self.__class__.total_points += chat_response["points_earned"]
        
        print("✅ Chat inicial exitoso - Llegada registrada")
    
    def test_05_location_question(self):
        """Test 5: Pregunta sobre el lugar actual"""
        print(f"\n❓ Test 5: Pregunta sobre ubicación actual...")
        
        chat_data = {
            "family_id": self.family_id,
            "message": "¿Qué es este lugar? ¿Puedes contarnos sobre la Plaza de Oriente?",
            "speaker_name": "Carlos"
        }
        
        response = requests.post(f"{BASE_URL}/api/chat/message", json=chat_data)
        assert response.status_code == 200
        
        chat_response = response.json()
        print(f"   Puntos ganados: {chat_response.get('points_earned')}")
        print(f"   Situación: {chat_response.get('situation')}")
        print(f"   Respuesta incluye info histórica: {'historia' in chat_response.get('response', '').lower()}")
        
        assert chat_response["success"] is True
        assert chat_response["points_earned"] > 0  # Puntos de engagement
        
        self.__class__.total_points += chat_response["points_earned"]
        
        print("✅ Pregunta sobre ubicación respondida")
    
    def test_06_answer_agent_question(self):
        """Test 6: Responder pregunta del agente"""
        print(f"\n🗣️ Test 6: Respondiendo pregunta del agente...")
        
        chat_data = {
            "family_id": self.family_id,
            "message": "¡Sí, nos encanta este lugar! Es muy bonito y tiene mucha historia.",
            "speaker_name": "Ana"
        }
        
        response = requests.post(f"{BASE_URL}/api/chat/message", json=chat_data)
        assert response.status_code == 200
        
        chat_response = response.json()
        print(f"   Puntos ganados: {chat_response.get('points_earned')}")
        print(f"   Total acumulado: {chat_response.get('total_points')}")
        
        assert chat_response["success"] is True
        
        self.__class__.total_points += chat_response["points_earned"]
        
        print("✅ Respuesta a pregunta del agente procesada")
    
    def test_07_get_family_status(self):
        """Test 7: Obtener estado del progreso familiar"""
        print(f"\n📊 Test 7: Consultando estado de progreso...")
        
        response = requests.get(f"{BASE_URL}/api/chat/family/{self.family_id}/status")
        assert response.status_code == 200
        
        status_data = response.json()
        print(f"   Familia: {status_data.get('family_name', 'N/A')}")
        print(f"   Puntos totales: {status_data.get('total_points', 0)}")
        print(f"   POI actual: {status_data.get('current_poi_index', 0)}")
        print(f"   POIs visitados: {status_data.get('visited_pois', 0)}")
        print(f"   Progreso: {status_data.get('progress_percentage', 0)}%")
        
        assert status_data.get("success") is True
        assert status_data.get("total_points", 0) > 0
        
        print("✅ Estado de progreso obtenido")
    
    def test_08_get_next_destination(self):
        """Test 8: Obtener siguiente destino"""
        print(f"\n🗺️ Test 8: Consultando siguiente destino...")
        
        response = requests.get(f"{BASE_URL}/api/routes/family/{self.family_id}/next")
        assert response.status_code == 200
        
        next_poi = response.json()
        print(f"   Siguiente POI: {next_poi.get('name', 'N/A')}")
        print(f"   Índice: {next_poi.get('index', 'N/A')}")
        print(f"   Progreso: {next_poi.get('progress', 'N/A')}")
        
        # Debería ser Plaza de Ramales (índice 1)
        assert next_poi.get("name") == "Plaza de Ramales"
        assert next_poi.get("index") == 1
        
        print("✅ Siguiente destino obtenido")
    
    def test_09_route_overview(self):
        """Test 9: Obtener vista general de la ruta"""
        print(f"\n🌍 Test 9: Consultando vista general de la ruta...")
        
        response = requests.get(f"{BASE_URL}/api/routes/overview")
        assert response.status_code == 200
        
        route_data = response.json()
        route_pois = route_data.get("route", [])
        
        print(f"   Total POIs en la ruta: {len(route_pois)}")
        print(f"   Primer POI: {route_pois[0]['name'] if route_pois else 'N/A'}")
        print(f"   Último POI: {route_pois[-1]['name'] if route_pois else 'N/A'}")
        
        assert len(route_pois) == 10  # 10 POIs en la ruta
        assert route_pois[0]["name"] == "Plaza de Oriente"
        assert route_pois[-1]["name"] == "Museo Ratoncito Pérez"
        
        print("✅ Vista general de la ruta obtenida")
    
    def test_10_madrid_knowledge_search(self):
        """Test 10: Buscar información sobre Madrid"""
        print(f"\n🔍 Test 10: Búsqueda de conocimiento sobre Madrid...")
        
        search_queries = [
            "¿Qué es la Plaza Mayor?",
            "Cuéntame sobre el Palacio Real",
            "Historia del Teatro Real",
            "Lugares para niños en Madrid"
        ]
        
        for query in search_queries:
            chat_data = {
                "family_id": self.family_id,
                "message": query,
                "speaker_name": "Sofia"
            }
            
            response = requests.post(f"{BASE_URL}/api/chat/message", json=chat_data)
            assert response.status_code == 200
            
            chat_response = response.json()
            print(f"   Query: '{query[:30]}...'")
            print(f"   Respuesta exitosa: {chat_response.get('success')}")
            
            assert chat_response["success"] is True
            assert len(chat_response.get("response", "")) > 0
        
        print("✅ Búsquedas de conocimiento exitosas")
    
    def test_11_multiple_speakers(self):
        """Test 11: Conversación con múltiples hablantes"""
        print(f"\n👥 Test 11: Conversación con múltiples miembros...")
        
        conversations = [
            {"speaker": "Sofia", "message": "¡Me gusta mucho este lugar!"},
            {"speaker": "Pablo", "message": "¿Hay ratoncitos de verdad aquí?"},
            {"speaker": "Ana", "message": "Sofia, ¿qué es lo que más te gusta?"},
            {"speaker": "Carlos", "message": "Deberíamos tomar una foto aquí"},
        ]
        
        for conv in conversations:
            chat_data = {
                "family_id": self.family_id,
                "message": conv["message"],
                "speaker_name": conv["speaker"]
            }
            
            response = requests.post(f"{BASE_URL}/api/chat/message", json=chat_data)
            assert response.status_code == 200
            
            chat_response = response.json()
            print(f"   {conv['speaker']}: {chat_response.get('success')}")
            
            assert chat_response["success"] is True
        
        print("✅ Conversación multi-hablante exitosa")
    
    def test_12_final_status_check(self):
        """Test 12: Verificación final del estado"""
        print(f"\n🏁 Test 12: Verificación final del estado...")
        
        response = requests.get(f"{BASE_URL}/api/chat/family/{self.family_id}/status")
        assert response.status_code == 200
        
        final_status = response.json()
        final_points = final_status.get("total_points", 0)
        
        print(f"   Puntos finales: {final_points}")
        print(f"   POIs visitados: {final_status.get('visited_pois', 0)}")
        print(f"   Progreso total: {final_status.get('progress_percentage', 0)}%")
        
        assert final_points >= 100  # Al menos puntos de llegada
        assert final_status.get("visited_pois", 0) >= 1  # Al menos 1 POI visitado
        
        print("✅ Estado final verificado")
        print(f"\n🎉 TEST COMPLETO EXITOSO - Puntos totales: {final_points}")


# Funciones de utilidad para ejecutar manualmente
def run_integration_test():
    """Ejecuta el test de integración manualmente"""
    print("🚀 Ejecutando test de integración completo...")
    pytest.main(["-v", "-s", "Server/tests/test_integration_full.py"])

def quick_health_check():
    """Verificación rápida de salud del sistema"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Sistema: {health.get('status')}")
            print(f"✅ DB: {health.get('database')}")
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False

if __name__ == "__main__":
    print("Verificando servidor antes del test...")
    if quick_health_check():
        run_integration_test()
    else:
        print("❌ Servidor no disponible. Inicia el servidor primero:")
        print("   python Server/main.py")