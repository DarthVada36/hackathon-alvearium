import os
from typing import Optional

# Fix para problemas de memoria MPS en Mac
os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class LangChainSettings(BaseSettings):
    """Configuración específica para LangChain, Groq, Supabase y Pinecone"""
    
    # === Claves y URLs ===
    groq_api_key: str
    supabase_url: str
    supabase_public_key: str
    supabase_secret_key: str
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str
    pinecone_dimension: int
    pinecone_metric: str
    pinecone_embedding_model: str
    pinecone_host: str
    madrid_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # === Configuración del agente ===
    agent_model: str = "openai/gpt-oss-120b"
    temperature: float = 0.7
    max_tokens: int = 1500

    # Personalidad del Ratoncito Pérez
    agent_name: str = "Ratoncito Pérez"
    agent_language: str = "es"

    # Configuración de adaptación familiar
    child_age_groups: dict = {
        "pequeños": (3, 7),
        "medianos": (8, 12),
        "grandes": (13, 17)
    }
    adult_age_threshold: int = 18
    
    # Configuración de embeddings
    embedding_cache_size: int = 1000
    embedding_model_warm_up: bool = True
    embedding_batch_size: int = 32
    
    # Configuración de Pinecone optimizado
    pinecone_cache_enabled: bool = True
    pinecone_cache_ttl: int = 3600  # 1 hora
    pinecone_batch_upsert_size: int = 100
    
    # Configuración de inicialización background
    background_init_enabled: bool = True
    background_init_timeout: int = 300  # 5 minutos
    knowledge_base_preload: bool = True
    
    # Configuración de rendimiento
    max_concurrent_embeddings: int = 5
    vector_search_timeout: int = 10  # segundos
    fallback_mode_enabled: bool = True
    
    # Configuración de logging para servicios optimizados
    embedding_service_log_level: str = "INFO"
    pinecone_service_log_level: str = "INFO"
    performance_monitoring: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    def validate_groq_key(self) -> bool:
        """Valida que la API key de Groq esté configurada correctamente"""
        return bool(self.groq_api_key and len(self.groq_api_key) > 20)
    
    def validate_pinecone_config(self) -> bool:
        """Valida que la configuración de Pinecone esté completa"""
        required_fields = [
            self.pinecone_api_key,
            self.pinecone_index_name,
            self.pinecone_embedding_model
        ]
        return all(field for field in required_fields)
    
    def get_embedding_config(self) -> dict:
        """Obtiene configuración específica para el servicio de embeddings"""
        return {
            "model_name": self.pinecone_embedding_model,
            "cache_size": self.embedding_cache_size,
            "warm_up": self.embedding_model_warm_up,
            "batch_size": self.embedding_batch_size,
            "max_concurrent": self.max_concurrent_embeddings,
            "log_level": self.embedding_service_log_level
        }
    
    def get_pinecone_config(self) -> dict:
        """Obtiene configuración específica para el servicio de Pinecone"""
        return {
            "api_key": self.pinecone_api_key,
            "index_name": self.pinecone_index_name,
            "dimension": self.pinecone_dimension,
            "metric": self.pinecone_metric,
            "cache_enabled": self.pinecone_cache_enabled,
            "cache_ttl": self.pinecone_cache_ttl,
            "batch_size": self.pinecone_batch_upsert_size,
            "timeout": self.vector_search_timeout,
            "log_level": self.pinecone_service_log_level
        }
    
    def get_performance_config(self) -> dict:
        """Obtiene configuración de rendimiento y optimización"""
        return {
            "background_init": self.background_init_enabled,
            "background_timeout": self.background_init_timeout,
            "knowledge_preload": self.knowledge_base_preload,
            "fallback_mode": self.fallback_mode_enabled,
            "monitoring": self.performance_monitoring,
            "max_concurrent_embeddings": self.max_concurrent_embeddings
        }
    
    def is_optimized_mode_enabled(self) -> bool:
        """Verifica si el modo optimizado está habilitado"""
        return (
            self.validate_groq_key() and 
            self.validate_pinecone_config() and
            self.embedding_model_warm_up
        )

# Instancia global para reutilizar configuración
try:
    langchain_settings = LangChainSettings()
    
    # Validaciones al inicio
    if langchain_settings.validate_groq_key():
        print(f"✅ Configuración Groq válida - Modelo: {langchain_settings.agent_model}")
    else:
        print("⚠️ Configuración Groq inválida o faltante")
    
    if langchain_settings.validate_pinecone_config():
        print(f"✅ Configuración Pinecone válida - Índice: {langchain_settings.pinecone_index_name}")
    else:
        print("⚠️ Configuración Pinecone inválida o faltante")
    
    if langchain_settings.is_optimized_mode_enabled():
        print("🚀 MODO OPTIMIZADO HABILITADO")
        print(f"   - Embeddings: {langchain_settings.pinecone_embedding_model}")
        print(f"   - Cache embeddings: {langchain_settings.embedding_cache_size}")
        print(f"   - Cache Pinecone: {langchain_settings.pinecone_cache_enabled}")
        print(f"   - Inicialización background: {langchain_settings.background_init_enabled}")
    else:
        print("⚠️ Modo optimizado no disponible - verificar configuración")
        
except Exception as e:
    print(f"❌ Error cargando configuración: {e}")
    langchain_settings = None