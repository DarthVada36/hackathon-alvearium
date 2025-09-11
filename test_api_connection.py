import requests
import json

def test_api_endpoints():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing API Endpoints")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Database: {response.json().get('database', 'unknown')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 2: Family creation
    try:
        family_data = {
            "name": "Familia Prueba API",
            "preferred_language": "es"
        }
        response = requests.post(
            f"{base_url}/api/families/",
            json=family_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Family creation: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Family ID: {result.get('id', 'unknown')}")
            print(f"   Name: {result.get('name', 'unknown')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Family creation failed: {e}")
    
    # Test 3: CORS headers
    try:
        response = requests.options(f"{base_url}/api/families/")
        print(f"✅ CORS preflight: {response.status_code}")
        cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
        if cors_headers:
            print(f"   CORS headers: {list(cors_headers.keys())}")
    except Exception as e:
        print(f"❌ CORS test failed: {e}")

if __name__ == "__main__":
    test_api_endpoints()
