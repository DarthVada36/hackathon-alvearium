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
    # ✅ Modelo Groq por defecto: openai/gpt-oss-120b (puedes cambiarlo en .env si lo necesitas)
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
    print(f"❌ Error cargando configuración: {e}")
    langchain_settings = None
