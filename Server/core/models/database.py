import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from dotenv import load_dotenv
import logging

load_dotenv()

class Database:
    def __init__(self, use_pooler=False, max_connections=5):
        self.use_pooler = use_pooler
        self.connection = None
        self.connection_pool = None
        self.max_connections = max_connections
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def get_connection_params(self):
        """Get database connection parameters"""
        password = os.getenv('YOUR_PASSWORD')
        
        if not password:
            raise ValueError("YOUR_PASSWORD environment variable is not set")
        
        if self.use_pooler:
            # For ephemeral connections (serverless functions)
            return {
                "host": "aws-1-eu-central-1.pooler.supabase.com",
                "port": 6543,
                "database": "postgres",
                "user": "postgres.ieeqygbbbipyiggqmyoz", 
                "password": password,
                "sslmode": "require",
                "connect_timeout": 10
            }
        else:
            # For persistent connections (traditional servers)
            return {
                "host": "db.ieeqygbbbipyiggqmyoz.supabase.co",
                "port": 5432,
                "database": "postgres",
                "user": "postgres",
                "password": password,
                "sslmode": "require",
                "connect_timeout": 10
            }
    
    def get_connection_url(self):
        """Get database connection URL"""
        password = os.getenv('YOUR_PASSWORD')
        
        if not password:
            raise ValueError("YOUR_PASSWORD environment variable is not set")
            
        if self.use_pooler:
            database_url = os.getenv('POOLER_URL')
        else:
            database_url = os.getenv('DATABASE_URL')
        
        if database_url and password:
            return database_url.replace('[YOUR_PASSWORD]', password)
        else:
            raise ValueError("Database URL not properly configured")
    
    def get_connection(self):
        """Get a database connection"""
        try:
            if self.connection is None or self.connection.closed:
                connection_params = self.get_connection_params()
                
                self.connection = psycopg2.connect(
                    cursor_factory=RealDictCursor,
                    **connection_params
                )
                
                self.logger.info(f"Database connection established ({'pooler' if self.use_pooler else 'direct'})")
                
            return self.connection
            
        except psycopg2.OperationalError as e:
            self.logger.error(f"Database connection failed: {e}")
            # Try alternative connection method
            try:
                connection_url = self.get_connection_url()
                self.connection = psycopg2.connect(
                    connection_url,
                    cursor_factory=RealDictCursor
                )
                self.logger.info("Database connection established using URL method")
                return self.connection
            except Exception as url_error:
                self.logger.error(f"URL connection also failed: {url_error}")
                raise e
        except Exception as e:
            self.logger.error(f"Unexpected database error: {e}")
            raise e
    
    def execute_query(self, query, params=None):
        """Execute a database query"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                conn = self.get_connection()
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    
                    # Handle SELECT queries
                    if query.strip().lower().startswith('select'):
                        result = cur.fetchall()
                        return result
                    
                    # Handle INSERT/UPDATE/DELETE queries
                    conn.commit()
                    
                    # For INSERT with RETURNING clause
                    if query.strip().lower().startswith('insert') and 'returning' in query.lower():
                        result = cur.fetchall()
                        return result
                    
                    # For other queries, return affected row count
                    return cur.rowcount
                    
            except psycopg2.OperationalError as e:
                retry_count += 1
                self.logger.warning(f"Query failed (attempt {retry_count}/{max_retries}): {e}")
                
                # Reset connection on operational errors
                if self.connection and not self.connection.closed:
                    self.connection.close()
                self.connection = None
                
                if retry_count >= max_retries:
                    self.logger.error(f"Query failed after {max_retries} attempts: {e}")
                    raise e
                    
            except Exception as e:
                self.logger.error(f"Query execution error: {e}")
                raise e
    
    def execute_transaction(self, queries_and_params):
        """Execute multiple queries in a transaction"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                results = []
                for query, params in queries_and_params:
                    cur.execute(query, params)
                    
                    if query.strip().lower().startswith('select'):
                        results.append(cur.fetchall())
                    elif 'returning' in query.lower():
                        results.append(cur.fetchall())
                    else:
                        results.append(cur.rowcount)
                
                conn.commit()
                return results
                
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Transaction failed: {e}")
            raise e
    
    def close(self):
        """Close the database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()
            self.logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        
    def health_check(self):
        """Check if database connection is healthy"""
        try:
            result = self.execute_query("SELECT 1 as health_check")
            return result[0]['health_check'] == 1 if result else False
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False