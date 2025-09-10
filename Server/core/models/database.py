import psycopg2
import psycopg2.extras
import logging
import os
from supabase import create_client, Client
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class Database:
    """Maneja la conexión con Supabase y PostgreSQL."""

    def __init__(self):
        self.supabase: Optional[Client] = None
        self.connection: Optional[psycopg2.extensions.connection] = None
        self.connect()

    def connect(self):
        """Establece conexión con Supabase API y opcionalmente PostgreSQL."""
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_PUBLIC_KEY")
            service_role = os.getenv("SUPABASE_SERVICE_ROLE")  # cadena Postgres pooler

            if not supabase_url or not supabase_key:
                raise ValueError("Faltan SUPABASE_URL o SUPABASE_PUBLIC_KEY en las variables de entorno")

            self.supabase = create_client(supabase_url, supabase_key)
            logger.info("✅ Conexión a Supabase establecida mediante API")

            if service_role:
                self.connection = psycopg2.connect(
                    service_role,
                    cursor_factory=psycopg2.extras.RealDictCursor
                )
                logger.info("✅ Conexión directa a PostgreSQL establecida")
            else:
                logger.warning("⚠️ No se proporcionó SUPABASE_SERVICE_ROLE: solo se usará la API de Supabase")

        except Exception as e:
            logger.error(f"❌ Error conectando a Supabase: {e}")
            raise

    def health_check(self) -> bool:
        try:
            if self.connection and not self.connection.closed:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return True
            if self.supabase:
                self.supabase.table("families").select("*").limit(1).execute()
                return True
            return False
        except Exception as e:
            logger.error(f"Health check fallido: {e}")
            return False

    def execute_query(self, query: str, params: tuple = None):
        if not self.connection:
            raise AttributeError("La conexión directa a PostgreSQL no está habilitada en Database.")
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:
                    return cursor.fetchall()
                self.connection.commit()
                return None
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error ejecutando consulta: {e}")
            raise

    def execute_transaction(self, queries: List[tuple]):
        if not self.connection:
            raise AttributeError("La conexión directa a PostgreSQL no está habilitada en Database.")
        try:
            with self.connection.cursor() as cursor:
                for query, params in queries:
                    cursor.execute(query, params)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error en transacción: {e}")
            raise

    def supabase_select(self, table: str, query: dict = None):
        try:
            if query:
                return self.supabase.table(table).select("*").eq(query['column'], query['value']).execute()
            else:
                return self.supabase.table(table).select("*").execute()
        except Exception as e:
            logger.error(f"Error en supabase_select: {e}")
            raise

    def supabase_insert(self, table: str, data: dict):
        try:
            return self.supabase.table(table).insert(data).execute()
        except Exception as e:
            logger.error(f"Error en supabase_insert: {e}")
            raise

    def close(self):
        try:
            if self.connection and not self.connection.closed:
                self.connection.close()
                logger.info("✅ Conexión a PostgreSQL cerrada")
        except Exception as e:
            logger.error(f"Error cerrando conexión: {e}")


def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()
