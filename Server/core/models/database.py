import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool
import logging
import os
from supabase import create_client, Client
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class Database:
    """Maneja la conexión con Supabase y PostgreSQL."""

    def __init__(self):
        self.supabase: Optional[Client] = None
        # Use a small connection pool for better resilience
        self.pool: Optional[SimpleConnectionPool] = None
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
                try:
                    # create a minimal pool (minconn=1, maxconn=5)
                    self.pool = SimpleConnectionPool(
                        1,
                        5,
                        dsn=service_role,
                        cursor_factory=psycopg2.extras.RealDictCursor,
                    )
                    # verify by briefly acquiring a connection
                    conn = self.pool.getconn()
                    try:
                        with conn.cursor() as cursor:
                            cursor.execute("SELECT 1")
                    finally:
                        self.pool.putconn(conn)
                    logger.info("✅ Connection pool to PostgreSQL established")
                except Exception as e:
                    logger.error(f"❌ Error creating PostgreSQL pool: {e}")
                    self.pool = None
            else:
                logger.warning("⚠️ No se proporcionó SUPABASE_SERVICE_ROLE: solo se usará la API de Supabase")

        except Exception as e:
            logger.error(f"❌ Error conectando a Supabase: {e}")
            raise

    def health_check(self) -> bool:
        try:
            if self.pool:
                conn = self.pool.getconn()
                try:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        return True
                finally:
                    self.pool.putconn(conn)
            if self.supabase:
                self.supabase.table("families").select("*").limit(1).execute()
                return True
            return False
        except Exception as e:
            logger.error(f"Health check fallido: {e}")
            return False

    def execute_query(self, query: str, params: tuple = None):
        # Use pooled connection if available
        if not self.pool:
            raise AttributeError("La conexión directa a PostgreSQL no está habilitada en Database.")

        conn = None
        try:
            conn = self.pool.getconn()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                
                # Always commit the transaction
                conn.commit()
                
                # Return results if available
                if cursor.description:
                    rows = cursor.fetchall()
                    return rows
                return None
        except Exception as e:
            try:
                if conn is not None:
                    conn.rollback()
            except Exception:
                pass
            logger.error(f"Error ejecutando consulta: {e}")
            raise
        finally:
            if conn is not None:
                try:
                    self.pool.putconn(conn)
                except Exception:
                    pass

    def execute_transaction(self, queries: List[tuple]):
        if not self.pool:
            raise AttributeError("La conexión directa a PostgreSQL no está habilitada en Database.")

        conn = None
        try:
            conn = self.pool.getconn()
            with conn.cursor() as cursor:
                for query, params in queries:
                    cursor.execute(query, params)
            conn.commit()
        except Exception as e:
            try:
                if conn is not None:
                    conn.rollback()
            except Exception:
                pass
            logger.error(f"Error en transacción: {e}")
            raise
        finally:
            if conn is not None:
                try:
                    self.pool.putconn(conn)
                except Exception:
                    pass

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
            if self.pool:
                try:
                    self.pool.closeall()
                    logger.info("✅ PostgreSQL connection pool closed")
                except Exception as e:
                    logger.error(f"Error closing pool: {e}")
        except Exception as e:
            logger.error(f"Error cerrando conexión: {e}")


def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()
