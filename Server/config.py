import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class LangChainSettings(BaseSettings):
    """Configuración específica para LangChain y Groq"""
    
    # API Key requerida
    groq_api_key: str
    
    # Configuración del agente 
    agent_model: str = "gemma2-9b-it"  # Gemini en Groq
    temperature: float = 0.7
    max_tokens: int = 1500
    
    # Personalidad del Ratoncito Pérez
    agent_name: str = "Ratoncito Pérez"
    agent_language: str = "es"  # Default español
    
    # Configuración de adaptación familiar
    child_age_groups: dict = {
        "pequeños": (3, 7),    # 3-7 años
        "medianos": (8, 12),   # 8-12 años  
        "grandes": (13, 17)    # 13-17 años
    }
    adult_age_threshold: int = 18
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    def validate_groq_key(self) -> bool:
        """Valida que la API key de Groq esté configurada"""
        return bool(self.groq_api_key and len(self.groq_api_key) > 20)


# Instancia global para reutilizar
try:
    langchain_settings = LangChainSettings()
    print(f"✅ Configuración LangChain cargada - Modelo: {langchain_settings.agent_model}")
except Exception as e:
    print(f"❌ Error cargando configuración: {e}")
    langchain_settings = None