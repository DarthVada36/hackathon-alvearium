import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self, use_pooler=False):
        self.use_pooler = use_pooler
        self.connection = None
        
    def get_connection(self):
        if self.connection is None or self.connection.closed:
            password = os.getenv('YOUR_PASSWORD')  # Obtener la contraseña
            
            if self.use_pooler:
                # Para conexiones efímeras (serverless functions)
                database_url = os.getenv('POOLER_URL')
            else:
                # Para conexiones persistentes (servidores tradicionales)
                database_url = os.getenv('DATABASE_URL')
            
            # Reemplazar [YOUR_PASSWORD] con la contraseña real
            if password and database_url:
                database_url = database_url.replace('[YOUR_PASSWORD]', password)
            
            self.connection = psycopg2.connect(
                database_url,
                cursor_factory=RealDictCursor
            )
        return self.connection
    
    def execute_query(self, query, params=None):
        conn = self.get_connection()
        with conn.cursor() as cur:
            cur.execute(query, params)
            if query.strip().lower().startswith('select'):
                return cur.fetchall()
            conn.commit()
            return cur.rowcount
    
    def close(self):
        if self.connection and not self.connection.closed:
            self.connection.close()