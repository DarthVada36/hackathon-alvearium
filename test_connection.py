import os
import psycopg2
from dotenv import load_dotenv

def test_connection():
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener URLs de conexión
    direct_url = os.getenv('DATABASE_URL')
    pooler_url = os.getenv('POOLER_URL')
    password = os.getenv('YOUR_PASSWORD')  # Cambiado a YOUR_PASSWORD
    
    if not direct_url:
        print("Error: DATABASE_URL no está definida en el archivo .env")
        return
    if not pooler_url:
        print("Error: POOLER_URL no está definida en el archivo .env")
        return
    
    # Reemplazar [YOUR_PASSWORD] con la contraseña real
    if password:
        direct_url = direct_url.replace('[YOUR_PASSWORD]', password)
        pooler_url = pooler_url.replace('[YOUR_PASSWORD]', password)
    
    # Mostrar URLs (ocultando la contraseña)
    masked_direct = direct_url.replace(password, '***') if password else direct_url
    masked_pooler = pooler_url.replace(password, '***') if password else pooler_url
    
    print("Probando conexión a Supabase PostgreSQL...")
    print(f"Direct URL: {masked_direct}")
    print(f"Pooler URL: {masked_pooler}")
    
    # Probar conexión directa
    try:
        conn_direct = psycopg2.connect(direct_url)
        cursor_direct = conn_direct.cursor()
        cursor_direct.execute("SELECT version();")
        db_version = cursor_direct.fetchone()
        print(f"✓ Conexión directa exitosa. Versión de PostgreSQL: {db_version[0]}")
        conn_direct.close()
    except Exception as e:
        print(f"✗ Error en conexión directa: {e}")
        return
    
    # Probar conexión pooler
    try:
        conn_pooler = psycopg2.connect(pooler_url)
        cursor_pooler = conn_pooler.cursor()
        cursor_pooler.execute("SELECT current_database();")
        db_name = cursor_pooler.fetchone()
        print(f"✓ Conexión pooler exitosa. Base de datos: {db_name[0]}")
        conn_pooler.close()
    except Exception as e:
        print(f"✗ Error en conexión pooler: {e}")
        return
    
    # Probar consulta a tablas
    try:
        conn = psycopg2.connect(direct_url)
        cursor = conn.cursor()
        
        # Verificar tablas existentes
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print("\nTablas encontradas en la base de datos:")
        for table in tables:
            print(f"✓ {table[0]}")
        
        conn.close()
    except Exception as e:
        print(f"✗ Error al consultar tablas: {e}")

if __name__ == "__main__":
    test_connection()