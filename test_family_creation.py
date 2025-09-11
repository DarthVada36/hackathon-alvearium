import requests
import json

def test_family_creation_with_members():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Family Creation with Members")
    print("=" * 50)
    
    family_data = {
        "name": "Familia Prueba Completa",
        "preferred_language": "es",
        "members": [
            {
                "name": "Papa Test",
                "age": 35,
                "member_type": "adult"
            },
            {
                "name": "Mama Test", 
                "age": 32,
                "member_type": "adult"
            },
            {
                "name": "Niño Test",
                "age": 8,
                "member_type": "child"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/families/",
            json=family_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Family created successfully!")
            print(f"   Family ID: {result.get('id')}")
            print(f"   Name: {result.get('name')}")
            print(f"   Language: {result.get('preferred_language')}")
            print(f"   Members: {len(result.get('members', []))}")
            for i, member in enumerate(result.get('members', [])):
                print(f"     {i+1}. {member.get('name')} ({member.get('age')} años, {member.get('member_type')})")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_family_creation_with_members()
