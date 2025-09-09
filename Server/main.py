from core.models.database import Database

# Para conexiones persistentes (recomendado para servidores)
db = Database(use_pooler=False)

# Para conexiones efímeras (recomendado para serverless functions)
# db = Database(use_pooler=True)

# Ejemplo de consulta
def get_family_by_user_id(user_id):
    query = "SELECT * FROM families WHERE user_id = %s"
    result = db.execute_query(query, (user_id,))
    return result

# Ejemplo de inserción
def create_user(email, hashed_password):
    query = """
        INSERT INTO users (email, hashed_password) 
        VALUES (%s, %s) 
        RETURNING id, email, created_at
    """
    result = db.execute_query(query, (email, hashed_password))
    return result[0] if result else None