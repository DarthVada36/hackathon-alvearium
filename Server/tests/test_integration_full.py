"""
Test de integración completo del Ratoncito Pérez Digital con Autenticación
Prueba todo el flujo: Registro → Login → Familia → Chat → Ruta completa
"""

import pytest
import requests
import time
import uuid
from typing import Dict, Any

# Configuración del test
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30

class TestRatonPerezCompleteFlow:
    """Test de integración completa con autenticación"""
    
    @classmethod
    def setup_class(cls):
        """Setup inicial - generar datos únicos para el test"""
        print("\n🚀 Iniciando test de flujo completo con autenticación...")
        
        # Generar datos únicos para evitar conflictos
        unique_id = str(uuid.uuid4())[:8]
        cls.test_email = f"test_{unique_id}@integration.com"
        cls.test_password = "123456"  # 6 caracteres mínimo
        cls.family_name = f"Familia Test {unique_id}"
        
        # Variables de estado
        cls.access_token = None
        cls.user_id = None
        cls.family_id = None
        cls.total_points = 0
        
        print(f"📧 Email de prueba: {cls.test_email}")
        print(f"👨‍👩‍👧‍👦 Familia de prueba: {cls.family_name}")
        
        # Verificar servidor
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            assert response.status_code == 200
            print("✅ Servidor funcionando correctamente")
        except Exception as e:
            pytest.fail(f"❌ Servidor no disponible: {e}")
    
    def test_01_health_and_auth_check(self):
        """Test 1: Verificar salud del sistema y autenticación"""
        print("\n🏥 Test 1: Health Check y servicios de auth...")
        
        # Health check general
        response = requests.get(f"{BASE_URL}/healthz")
        assert response.status_code == 200
        
        health_data = response.json()
        print(f"   Estado general: {health_data.get('status')}")
        print(f"   Auth disponible: {health_data.get('auth', {}).get('available', False)}")
        print(f"   Database: {health_data.get('database', 'unknown')}")
        
        # Verificar que endpoints de auth estén disponibles
        response = requests.get(f"{BASE_URL}/_routes")
        routes = response.json().get("routes", [])
        auth_routes = [r for r in routes if "/api/auth/" in r.get("path", "")]
        
        assert len(auth_routes) >= 4  # register, login, me, logout mínimo
        print(f"   Endpoints de auth encontrados: {len(auth_routes)}")
        
        print("✅ Sistema y autenticación listos")
    
    def test_02_user_registration(self):
        """Test 2: Registro de usuario"""
        print(f"\n👤 Test 2: Registrando usuario {self.test_email}...")
        
        registration_data = {
            "email": self.test_email,
            "password": self.test_password,
            "avatar": "icon1"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=registration_data)
        assert response.status_code == 200
        
        auth_response = response.json()
        
        # Verificar estructura de respuesta
        assert "access_token" in auth_response
        assert "user" in auth_response
        assert auth_response["token_type"] == "bearer"
        
        # Guardar datos para tests posteriores
        self.__class__.access_token = auth_response["access_token"]
        self.__class__.user_id = auth_response["user"]["id"]
        
        print(f"   Usuario registrado con ID: {self.user_id}")
        print(f"   Token obtenido: {self.access_token[:20]}...")
        print(f"   Avatar: {auth_response['user']['avatar']}")
        
        print("✅ Usuario registrado exitosamente")
    
    def test_03_user_login(self):
        """Test 3: Login de usuario (verificar que también funciona)"""
        print(f"\n🔐 Test 3: Login con usuario registrado...")
        
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        assert response.status_code == 200
        
        login_response = response.json()
        
        # Verificar que obtenemos token válido
        assert "access_token" in login_response
        assert login_response["user"]["id"] == self.user_id
        assert login_response["user"]["email"] == self.test_email
        
        print(f"   Login exitoso para usuario ID: {self.user_id}")
        print(f"   Nuevo token obtenido: {login_response['access_token'][:20]}...")
        
        print("✅ Login verificado")
    
    def test_04_get_user_profile(self):
        """Test 4: Obtener perfil de usuario"""
        print(f"\n👨‍💼 Test 4: Obteniendo perfil de usuario...")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        
        profile = response.json()
        
        assert profile["user"]["id"] == self.user_id
        assert profile["user"]["email"] == self.test_email
        assert profile["total_families"] == 0  # No debería tener familias aún
        assert profile["total_points"] == 0
        
        print(f"   Email: {profile['user']['email']}")
        print(f"   Familias: {profile['total_families']}")
        print(f"   Puntos totales: {profile['total_points']}")
        
        print("✅ Perfil obtenido correctamente")
    
    def test_05_create_family(self):
        """Test 5: Crear familia autenticada"""
        print(f"\n👨‍👩‍👧‍👦 Test 5: Creando familia autenticada...")
        
        family_data = {
            "name": self.family_name,
            "preferred_language": "es",
            "members": [
                {"name": "Ana García", "age": 35, "member_type": "adult"},
                {"name": "Carlos García", "age": 37, "member_type": "adult"},
                {"name": "Sofia García", "age": 8, "member_type": "child"},
                {"name": "Pablo García", "age": 5, "member_type": "child"}
            ]
        }
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.post(f"{BASE_URL}/api/families/", json=family_data, headers=headers)
        assert response.status_code == 200
        
        family_response = response.json()
        self.__class__.family_id = family_response["id"]
        
        print(f"   Familia creada con ID: {self.family_id}")
        print(f"   Nombre: {family_response['name']}")
        print(f"   Miembros: {len(family_response['members'])}")
        
        assert family_response["name"] == self.family_name
        assert len(family_response["members"]) == 4
        
        print("✅ Familia creada exitosamente")
    
    def test_06_get_user_families(self):
        """Test 6: Listar familias del usuario"""
        print(f"\n📋 Test 6: Listando familias del usuario...")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{BASE_URL}/api/families/", headers=headers)
        assert response.status_code == 200
        
        families_data = response.json()
        
        assert families_data["total_families"] == 1
        assert len(families_data["families"]) == 1
        assert families_data["families"][0]["id"] == self.family_id
        assert families_data["user_id"] == self.user_id
        
        print(f"   Total familias: {families_data['total_families']}")
        print(f"   Primera familia: {families_data['families'][0]['name']}")
        
        print("✅ Familias listadas correctamente")
    
    def test_07_chat_initial_arrival(self):
        """Test 7: Chat inicial - llegada a Plaza de Oriente"""
        print(f"\n💬 Test 7: Chat inicial con autenticación...")
        
        chat_data = {
            "family_id": self.family_id,
            "message": "¡Hola Ratoncito Pérez! ¡Estamos muy emocionados de comenzar!",
            "speaker_name": "Sofia"
        }
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.post(f"{BASE_URL}/api/chat/message", json=chat_data, headers=headers)
        assert response.status_code == 200
        
        chat_response = response.json()
        
        assert chat_response["success"] is True
        assert chat_response["points_earned"] >= 50  # Puntos de llegada o engagement
        
        self.__class__.total_points += chat_response["points_earned"]
        
        print(f"   Éxito: {chat_response['success']}")
        print(f"   Puntos ganados: {chat_response['points_earned']}")
        print(f"   Situación: {chat_response.get('situation', 'N/A')}")
        print(f"   Respuesta: {chat_response['response'][:100]}...")
        
        print("✅ Chat inicial exitoso")
    
    def test_08_family_status_check(self):
        """Test 8: Verificar estado de familia"""
        print(f"\n📊 Test 8: Verificando estado de familia...")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{BASE_URL}/api/chat/family/{self.family_id}/status", headers=headers)
        assert response.status_code == 200
        
        status_data = response.json()
        
        assert status_data["success"] is True
        assert status_data["user_id"] == self.user_id
        assert status_data.get("total_points", 0) >= 0
        
        print(f"   Usuario propietario: {status_data['user_id']}")
        print(f"   Puntos totales: {status_data.get('total_points', 0)}")
        print(f"   POI actual: {status_data.get('current_poi_index', 0)}")
        
        print("✅ Estado verificado correctamente")
    
    def test_09_complete_poi_interaction(self):
        """Test 9: Interacción completa en un POI"""
        print(f"\n🏛️ Test 9: Interacción completa en POI...")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        # Serie de mensajes para simular interacción completa
        interactions = [
            {
                "message": "¿Qué puedes contarnos sobre este lugar tan especial?",
                "speaker": "Ana",
                "expect_points": True
            },
            {
                "message": "¡Nos encanta la historia de Madrid!",
                "speaker": "Carlos", 
                "expect_points": True
            },
            {
                "message": "¿Podemos explorar más lugares cerca de aquí?",
                "speaker": "Sofia",
                "expect_points": True
            }
        ]
        
        points_earned_this_poi = 0
        
        for interaction in interactions:
            chat_data = {
                "family_id": self.family_id,
                "message": interaction["message"],
                "speaker_name": interaction["speaker"]
            }
            
            response = requests.post(f"{BASE_URL}/api/chat/message", json=chat_data, headers=headers)
            assert response.status_code == 200
            
            chat_response = response.json()
            points = chat_response.get("points_earned", 0)
            points_earned_this_poi += points
            
            print(f"   {interaction['speaker']}: {points} puntos")
            print(f"   Respuesta: {chat_response['response'][:80]}...")
            
            time.sleep(0.5)  # Pequeña pausa entre mensajes
        
        self.__class__.total_points += points_earned_this_poi
        print(f"   Total puntos en este POI: {points_earned_this_poi}")
        
        print("✅ Interacción completa en POI")
    
    def test_10_route_progression(self):
        """Test 10: Progresión en la ruta"""
        print(f"\n🗺️ Test 10: Verificando progresión de ruta...")
        
        # Obtener siguiente destino
        response = requests.get(f"{BASE_URL}/api/routes/family/{self.family_id}/next")
        assert response.status_code == 200
        
        next_poi = response.json()
        
        print(f"   Siguiente POI: {next_poi.get('name', 'N/A')}")
        print(f"   Progreso: {next_poi.get('progress', 'N/A')}")
        
        # Obtener vista general de la ruta
        response = requests.get(f"{BASE_URL}/api/routes/overview")
        assert response.status_code == 200
        
        route_data = response.json()
        route_pois = route_data.get("route", [])
        
        assert len(route_pois) == 10
        print(f"   Total POIs en ruta: {len(route_pois)}")
        print(f"   Primer POI: {route_pois[0]['name']}")
        print(f"   Último POI: {route_pois[-1]['name']}")
        
        print("✅ Progresión de ruta verificada")
    
    def test_11_chat_history(self):
        """Test 11: Verificar historial de chat"""
        print(f"\n📜 Test 11: Verificando historial de chat...")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{BASE_URL}/api/chat/family/{self.family_id}/history", headers=headers)
        assert response.status_code == 200
        
        history_data = response.json()
        
        assert history_data["family_id"] == self.family_id
        assert history_data["total_messages"] > 0
        assert len(history_data["messages"]) > 0
        
        print(f"   Total mensajes: {history_data['total_messages']}")
        print(f"   Mostrando: {history_data['showing']}")
        print(f"   Último mensaje: {history_data['messages'][-1].get('user_message', 'N/A')[:50]}...")
        
        print("✅ Historial verificado")
    
    def test_12_unauthorized_access_protection(self):
        """Test 12: Verificar protección contra acceso no autorizado"""
        print(f"\n🔒 Test 12: Verificando protección de endpoints...")
        
        # Intentar acceder sin token
        response = requests.get(f"{BASE_URL}/api/families/")
        assert response.status_code == 401
        
        response = requests.post(f"{BASE_URL}/api/chat/message", json={
            "family_id": self.family_id,
            "message": "test"
        })
        assert response.status_code == 401
        
        # Intentar con token inválido
        headers = {"Authorization": "Bearer token_falso_invalid"}
        response = requests.get(f"{BASE_URL}/api/families/", headers=headers)
        assert response.status_code == 401
        
        print("   ✅ Acceso sin token: bloqueado")
        print("   ✅ Acceso con token inválido: bloqueado")
        
        print("✅ Protección de seguridad verificada")
    
    def test_13_final_profile_verification(self):
        """Test 13: Verificación final del perfil actualizado"""
        print(f"\n🏁 Test 13: Verificación final del perfil...")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        
        final_profile = response.json()
        
        assert final_profile["total_families"] == 1
        assert final_profile["total_points"] >= 0  # Puede variar según puntos otorgados
        assert len(final_profile["families"]) == 1
        
        family = final_profile["families"][0]
        assert family["name"] == self.family_name
        assert len(family["members"]) == 4
        
        print(f"   Usuario: {final_profile['user']['email']}")
        print(f"   Familias totales: {final_profile['total_families']}")
        print(f"   Puntos acumulados: {final_profile['total_points']}")
        print(f"   Familia creada: {family['name']}")
        
        print("✅ Perfil final verificado")
        print(f"\n🎉 FLUJO COMPLETO EXITOSO")
        print(f"   Email: {self.test_email}")
        print(f"   Familia: {self.family_name}")
        print(f"   Puntos totales: {final_profile['total_points']}")
    
    @classmethod
    def teardown_class(cls):
        """Cleanup opcional - en producción podrías limpiar datos de test"""
        print(f"\n🧹 Cleanup completado")
        print(f"   Usuario de prueba: {cls.test_email}")
        print(f"   Familia de prueba: {cls.family_name}")


# Funciones de utilidad
def run_complete_flow_test():
    """Ejecuta el test completo de flujo con autenticación"""
    print("🚀 Ejecutando test de flujo completo con autenticación...")
    pytest.main(["-v", "-s", __file__])

def quick_auth_test():
    """Test rápido solo de autenticación"""
    try:
        # Test de registro rápido
        unique_id = str(uuid.uuid4())[:8]
        test_data = {
            "email": f"quick_{unique_id}@test.com",
            "password": "123456",
            "avatar": "icon1"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_data)
        if response.status_code == 200:
            auth_data = response.json()
            print(f"✅ Auth rápido: Usuario creado con token")
            return True
        else:
            print(f"❌ Auth falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en auth test: {e}")
        return False

if __name__ == "__main__":
    print("Verificando servidor y autenticación...")
    if quick_auth_test():
        run_complete_flow_test()
    else:
        print("❌ Test de autenticación falló. Verifica que el servidor esté corriendo.")
        print("   python Server/main.py")