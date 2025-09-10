import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class LangChainSettings(BaseSettings):
    """Configuración específica para LangChain, Groq, Supabase y Pinecone.

    Nota: Muchos campos son opcionales para permitir ejecutar tests y el servidor
    sin depender de todos los servicios externos durante el desarrollo.
    """

    # === Claves y URLs ===
    groq_api_key: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_public_key: Optional[str] = None
    supabase_secret_key: Optional[str] = None

    # Pinecone (v3 serverless) – hacer opcionales para no romper en local
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: Optional[str] = None
    pinecone_dimension: Optional[int] = None
    pinecone_metric: Optional[str] = None
    pinecone_embedding_model: Optional[str] = None
    pinecone_host: Optional[str] = None

    # Otros
    madrid_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # === Configuración del agente ===
    # ✅ Usamos un modelo Groq más potente que geemma (por ejemplo LLaMA 3 de 70B)
    agent_model: str = "gemma2-9b-it"  
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

    class Config:
        env_file = ".env"
        case_sensitive = False  # No distinguir mayúsculas/minúsculas en variables
        extra = "ignore"        # Ignorar variables no declaradas para evitar errores

    def validate_groq_key(self) -> bool:
        """Valida que la API key de Groq esté configurada correctamente"""
        return bool(self.groq_api_key and len(self.groq_api_key) > 20)

# Instancia global para reutilizar configuración
try:
    langchain_settings = LangChainSettings()
    print(f"✅ Configuración LangChain cargada - Modelo: {langchain_settings.agent_model}")
except Exception as e:
    # No fallar al importar en entornos de test/desarrollo si faltan variables
    print(f"⚠️  Config por defecto (faltan variables opcionales): {e}")
    langchain_settings = LangChainSettings()  # instancia con defaults
