import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import socket
import dns.resolver

load_dotenv()

def test_dns_resolution(hostname):
    """Test if we can resolve the hostname"""
    try:
        ip = socket.gethostbyname(hostname)
        print(f"✓ Resolución DNS exitosa: {hostname} -> {ip}")
        return True
    except socket.gaierror as e:
        print(f"✗ Error en la resolución DNS para {hostname}: {e}")
        return False

def test_supabase_connection():
    """Test connection to Supabase PostgreSQL"""
    print("Probando conexión a Supabase PostgreSQL...")
    
    # Obtener variables de entorno
    password = os.getenv('YOUR_PASSWORD')
    database_url = os.getenv('DATABASE_URL')
    pooler_url = os.getenv('POOLER_URL')
    
    print(f"Contraseña cargada: {'Sí' if password else 'No'}")
    print(f"DATABASE_URL cargada: {'Sí' if database_url else 'No'}")
    print(f"POOLER_URL cargada: {'Sí' if pooler_url else 'No'}")
    
    if not password:
        print("✗ Error: YOUR_PASSWORD no está definida en el archivo .env")
        return False
    
    # Probar resolución DNS primero
    direct_host = "db.ieeqygbbbipyiggqmyoz.supabase.co"
    pooler_host = "aws-1-eu-central-1.pooler.supabase.com"
    
    print(f"\n--- Probando resolución DNS ---")
    direct_dns_ok = test_dns_resolution(direct_host)
    pooler_dns_ok = test_dns_resolution(pooler_host)
    
    # Métodos alternativos de conexión
    connections_to_test = []
    
    # Método 1: Conexión directa con parámetros explícitos
    connections_to_test.append({
        "name": "Conexión directa (parámetros explícitos)",
        "params": {
            "host": "db.ieeqygbbbipyiggqmyoz.supabase.co",
            "port": 5432,
            "database": "postgres",
            "user": "postgres",
            "password": password,
            "sslmode": "require"
        }
    })
    
    # Método 2: Conexión con pooler con parámetros explícitos
    connections_to_test.append({
        "name": "Conexión con pooler (parámetros explícitos)",
        "params": {
            "host": "aws-1-eu-central-1.pooler.supabase.com",
            "port": 6543,
            "database": "postgres", 
            "user": "postgres.ieeqygbbbipyiggqmyoz",
            "password": password,
            "sslmode": "require"
        }
    })
    
    # Método 3: Usando cadenas de conexión (si están disponibles)
    if database_url:
        final_database_url = database_url.replace('[YOUR_PASSWORD]', password)
        connections_to_test.append({
            "name": "Conexión directa por URL",
            "url": final_database_url
        })
    
    if pooler_url:
        final_pooler_url = pooler_url.replace('[YOUR_PASSWORD]', password)
        connections_to_test.append({
            "name": "Conexión con pooler por URL", 
            "url": final_pooler_url
        })
    
    print(f"\n--- Probando conexiones a la base de datos ---")
    
    successful_connections = []
    
    for i, conn_config in enumerate(connections_to_test, 1):
        print(f"\n{i}. Probando {conn_config['name']}...")
        
        try:
            if 'url' in conn_config:
                # Método con cadena de conexión
                print(f"URL: {conn_config['url'][:50]}...")
                connection = psycopg2.connect(
                    conn_config['url'],
                    cursor_factory=RealDictCursor,
                    connect_timeout=10
                )
            else:
                # Método con parámetros explícitos
                print(f"Host: {conn_config['params']['host']}:{conn_config['params']['port']}")
                connection = psycopg2.connect(
                    cursor_factory=RealDictCursor,
                    connect_timeout=10,
                    **conn_config['params']
                )
            
            # Probar la conexión con una consulta simple
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"✓ ¡Conexión exitosa!")
                print(f"  Versión de la base de datos: {version['version'][:50]}...")
                
                # Probar una consulta simple a una tabla
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 5;")
                tables = cursor.fetchall()
                if tables:
                    print(f"  Se encontraron {len(tables)} tablas públicas")
                else:
                    print("  No se encontraron tablas públicas (esto es normal en bases de datos nuevas)")
            
            connection.close()
            successful_connections.append(conn_config['name'])
            
        except psycopg2.OperationalError as e:
            print(f"✗ Falló la conexión: {e}")
        except Exception as e:
            print(f"✗ Error inesperado: {e}")
    
    print(f"\n--- Resumen ---")
    if successful_connections:
        print(f"✓ Conexiones exitosas: {len(successful_connections)}")
        for conn in successful_connections:
            print(f"  - {conn}")
        return True
    else:
        print("✗ No hubo conexiones exitosas")
        print("\nSugerencias para solucionar problemas:")
        print("1. Verifica tu conexión a internet")
        print("2. Asegúrate de que tu proyecto de Supabase esté activo")
        print("3. Verifica si tu IP está permitida en la configuración de Supabase")
        print("4. Verifica la contraseña en tu archivo .env")
        print("5. Intenta usar una VPN si estás detrás de un firewall restrictivo")
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    if success:
        print(f"\n🎉 ¡La conexión a la base de datos funciona! Ya puedes usar tu aplicación.")
    else:
        print(f"\n❌ Por favor, soluciona los problemas de conexión antes de continuar.")
