from core.models.database import Database
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Para conexiones persistentes (recomendado para servidores)
db = Database(use_pooler=False)

# Para conexiones efímeras (recomendado para funciones serverless)
# db = Database(use_pooler=True)

def probar_conexion_base_de_datos():
    """Probar la conexión a la base de datos y operaciones básicas"""
    try:
        print("Probando la conexión a la base de datos...")
        
        # Prueba de salud
        if db.health_check():
            print("✓ La conexión a la base de datos es saludable")
        else:
            print("✗ Falló la prueba de salud de la base de datos")
            return False
        
        # Prueba de consulta básica
        resultado = db.execute_query("SELECT current_timestamp as now, version() as version")
        if resultado:
            print(f"✓ Timestamp actual: {resultado[0]['now']}")
            print(f"✓ Versión de la base de datos: {resultado[0]['version'][:50]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"Falló la prueba de conexión a la base de datos: {e}")
        return False

# Ejemplo de consulta
def obtener_familia_por_id_usuario(user_id):
    """Obtener información de la familia para un usuario específico"""
    try:
        consulta = "SELECT * FROM families WHERE user_id = %s"
        resultado = db.execute_query(consulta, (user_id,))
        return resultado
    except Exception as e:
        logger.error(f"Error al obtener la familia para el usuario {user_id}: {e}")
        return None

# Ejemplo de inserción
def crear_usuario(email, hashed_password):
    """Crear un nuevo usuario en la base de datos"""
    try:
        consulta = """
            INSERT INTO users (email, hashed_password) 
            VALUES (%s, %s) 
            RETURNING id, email, created_at
        """
        resultado = db.execute_query(consulta, (email, hashed_password))
        return resultado[0] if resultado else None
    except Exception as e:
        logger.error(f"Error al crear el usuario {email}: {e}")
        return None

# Ejemplo de múltiples operaciones en una transacción
def crear_usuario_con_familia(email, hashed_password, nombre_familia):
    """Crear usuario y familia en una sola transacción"""
    try:
        consultas_y_parametros = [
            (
                "INSERT INTO users (email, hashed_password) VALUES (%s, %s) RETURNING id",
                (email, hashed_password)
            ),
            (
                "INSERT INTO families (user_id, name) VALUES (%s, %s) RETURNING id",
                None  # Se completará con el user_id del resultado anterior
            )
        ]
        
        # Nota: para transacciones más complejas, podrías querer manejarlas manualmente
        # Este es un ejemplo simplificado
        with db:
            resultado_usuario = db.execute_query(
                consultas_y_parametros[0][0], consultas_y_parametros[0][1]
            )
            if resultado_usuario:
                user_id = resultado_usuario[0]['id']
                resultado_familia = db.execute_query(
                    consultas_y_parametros[1][0], (user_id, nombre_familia)
                )
                return {
                    'usuario': resultado_usuario[0],
                    'familia': resultado_familia[0] if resultado_familia else None
                }
        return None
    except Exception as e:
        logger.error(f"Error al crear el usuario con familia: {e}")
        return None

# Función para verificar que las tablas necesarias existen
def verificar_esquema_base_de_datos():
    """Verifica si existen las tablas requeridas"""
    try:
        tablas_requeridas = ['users', 'families']
        
        consulta = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = ANY(%s)
        """
        
        resultado = db.execute_query(consulta, (tablas_requeridas,))
        tablas_existentes = [fila['table_name'] for fila in resultado] if resultado else []
        
        print(f"Tablas existentes: {tablas_existentes}")
        
        tablas_faltantes = set(tablas_requeridas) - set(tablas_existentes)
        if tablas_faltantes:
            print(f"⚠️  Tablas faltantes: {list(tablas_faltantes)}")
            print("Es posible que debas ejecutar las migraciones de base de datos")
        else:
            print("✓ Todas las tablas requeridas existen")
            
        return len(tablas_faltantes) == 0
        
    except Exception as e:
        logger.error(f"Error al verificar el esquema de la base de datos: {e}")
        return False

if __name__ == "__main__":
    print("=== Prueba de Conexión a la Base de Datos ===")
    
    # Probar la conexión
    if probar_conexion_base_de_datos():
        print("\n=== Verificación del Esquema de la Base de Datos ===")
        verificar_esquema_base_de_datos()
        
        print("\n=== ¡Listo para usar! ===")
        print("La conexión con tu base de datos está funcionando correctamente.")
    else:
        print("\n❌ Primero corrige los problemas de conexión a la base de datos.")
        print("Ejecuta el script test_connection_fixed.py para diagnósticos detallados.")
