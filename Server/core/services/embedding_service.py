"""
Embedding Service - Servicio singleton para manejar embeddings de forma eficiente
Evita la recarga del modelo en cada request y mantiene caché de embeddings
"""

import os
import logging
import threading
from typing import List, Dict, Optional, Any
from functools import lru_cache
import hashlib
import json

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Servicio singleton para manejar embeddings de forma eficiente"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._model = None
        self._model_name = os.getenv("PINECONE_EMBEDDING_MODEL", "intfloat/e5-large-v2")
        self._embedding_cache = {}  # Cache en memoria para embeddings frecuentes
        self._max_cache_size = 1000
        self._is_loading = False
        
        # Ajustar modelo si es necesario
        if self._model_name == "llama-text-embed-v2":
            self._model_name = "intfloat/e5-large-v2"
        
        logger.info(f"🚀 EmbeddingService inicializado con modelo: {self._model_name}")
    
    def _get_model(self):
        """Carga el modelo de embeddings de forma lazy y thread-safe"""
        if self._model is None:
            with self._lock:
                if self._model is None and not self._is_loading:
                    self._is_loading = True
                    try:
                        from sentence_transformers import SentenceTransformer
                        logger.info(f"📥 Cargando modelo de embeddings: {self._model_name}")
                        self._model = SentenceTransformer(self._model_name)
                        logger.info("✅ Modelo de embeddings cargado exitosamente")
                    except Exception as e:
                        logger.error(f"❌ Error cargando modelo de embeddings: {e}")
                        self._model = None
                        raise
                    finally:
                        self._is_loading = False
        return self._model
    
    def _get_cache_key(self, text: str, text_type: str = "passage") -> str:
        """Genera clave única para el caché basada en el texto y tipo"""
        content = f"{text_type}:{text}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _manage_cache_size(self):
        """Gestiona el tamaño del caché eliminando entradas antiguas si es necesario"""
        if len(self._embedding_cache) > self._max_cache_size:
            # Eliminar 20% de las entradas más antiguas (FIFO simple)
            items_to_remove = len(self._embedding_cache) - int(self._max_cache_size * 0.8)
            keys_to_remove = list(self._embedding_cache.keys())[:items_to_remove]
            for key in keys_to_remove:
                del self._embedding_cache[key]
            logger.info(f"🧹 Cache limpiado: removidas {items_to_remove} entradas")
    
    def generate_embeddings(self, texts: List[str], text_type: str = "passage") -> List[List[float]]:
        """
        Genera embeddings para una lista de textos con caché automático
        
        Args:
            texts: Lista de textos para generar embeddings
            text_type: Tipo de texto ("passage" para documentos, "query" para consultas)
            
        Returns:
            Lista de embeddings (vectores)
        """
        if not texts:
            return []
        
        model = self._get_model()
        if model is None:
            logger.error("❌ Modelo de embeddings no disponible")
            return []
        
        # Verificar caché para textos ya procesados
        embeddings = []
        texts_to_process = []
        indices_to_process = []
        
        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text, text_type)
            if cache_key in self._embedding_cache:
                embeddings.append(self._embedding_cache[cache_key])
            else:
                embeddings.append(None)  # Placeholder
                texts_to_process.append(text)
                indices_to_process.append(i)
        
        # Procesar textos no cacheados
        if texts_to_process:
            try:
                # Preparar textos con prefijo para modelos e5
                if text_type == "query":
                    prepared_texts = [f"query: {text}" for text in texts_to_process]
                else:
                    prepared_texts = [f"passage: {text}" for text in texts_to_process]
                
                # Generar embeddings
                new_embeddings = model.encode(prepared_texts, normalize_embeddings=True)
                new_embeddings_list = new_embeddings.tolist() if hasattr(new_embeddings, "tolist") else new_embeddings
                
                # Actualizar caché y resultado
                for i, (text, embedding) in enumerate(zip(texts_to_process, new_embeddings_list)):
                    cache_key = self._get_cache_key(text, text_type)
                    self._embedding_cache[cache_key] = embedding
                    embeddings[indices_to_process[i]] = embedding
                
                # Gestionar tamaño del caché
                self._manage_cache_size()
                
                logger.info(f"📊 Generados {len(new_embeddings_list)} nuevos embeddings, {len(texts) - len(new_embeddings_list)} desde caché")
                
            except Exception as e:
                logger.error(f"❌ Error generando embeddings: {e}")
                return []
        else:
            logger.info(f"📊 Todos los embeddings ({len(texts)}) obtenidos desde caché")
        
        return embeddings
    
    def generate_single_embedding(self, text: str, text_type: str = "passage") -> List[float]:
        """
        Genera embedding para un solo texto
        
        Args:
            text: Texto para generar embedding
            text_type: Tipo de texto ("passage" o "query")
            
        Returns:
            Vector de embedding
        """
        embeddings = self.generate_embeddings([text], text_type)
        return embeddings[0] if embeddings else []
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """Genera embedding específicamente para consultas"""
        return self.generate_single_embedding(query, "query")
    
    def generate_passage_embeddings(self, passages: List[str]) -> List[List[float]]:
        """Genera embeddings específicamente para pasajes/documentos"""
        return self.generate_embeddings(passages, "passage")
    
    def is_available(self) -> bool:
        """Verifica si el servicio de embeddings está disponible"""
        try:
            return self._get_model() is not None
        except Exception:
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del caché"""
        return {
            "cache_size": len(self._embedding_cache),
            "max_cache_size": self._max_cache_size,
            "model_loaded": self._model is not None,
            "model_name": self._model_name
        }
    
    def clear_cache(self):
        """Limpia el caché de embeddings"""
        with self._lock:
            self._embedding_cache.clear()
        logger.info("🧹 Cache de embeddings limpiado")
    
    def warm_up(self):
        """Pre-carga el modelo para evitar latencia en el primer request"""
        try:
            logger.info("🔥 Warming up embedding service...")
            self._get_model()
            # Generar un embedding de prueba para inicializar completamente
            test_embedding = self.generate_single_embedding("test", "passage")
            if test_embedding:
                logger.info("✅ Embedding service warmed up successfully")
            else:
                logger.warning("⚠️ Embedding service warm up failed")
        except Exception as e:
            logger.error(f"❌ Error during embedding service warm up: {e}")

# Instancia global del servicio
embedding_service = EmbeddingService()