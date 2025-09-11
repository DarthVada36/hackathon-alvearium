"""
Pinecone service (v3 SDK) with simple CRUD and health reporting.

Configuration via environment variables:
  - PINECONE_API_KEY  (required)
  - PINECONE_INDEX_NAME    (default: "perez")
  - PINECONE_DIMENSION      (default: 1024)
  - PINECONE_METRIC   (default: "cosine")
  - PINECONE_CLOUD    (default: "aws")
  - PINECONE_REGION   (default: "us-east-1")
"""
from __future__ import annotations

import os
import time
import logging
from typing import Any, Dict, Iterable, List, Optional

logger = logging.getLogger(__name__)

class PineconeService:
	def __init__(self) -> None:
		self.api_key = os.getenv("PINECONE_API_KEY")
		self.index_name = os.getenv("PINECONE_INDEX_NAME", "perez")
		self.dimension = int(os.getenv("PINECONE_DIMENSION", "1024"))
		self.metric = os.getenv("PINECONE_METRIC", "cosine")
		self.cloud = os.getenv("PINECONE_CLOUD", "aws")
		self.region = os.getenv("PINECONE_REGION", "us-east-1")

		self._pc = None
		self._index = None
		self._last_error: Optional[str] = None
		self._vector_cache = {}  # Cache de vectores consultados recientemente

		if not self.api_key:
			self._last_error = "PINECONE_API_KEY not set"
			return

		try:
			from pinecone import Pinecone, ServerlessSpec

			self._pc = Pinecone(api_key=self.api_key)
			# Create index if missing
			names = [i["name"] for i in self._pc.list_indexes()] if hasattr(self._pc, "list_indexes") else []
			if self.index_name not in names:
				logger.info(f"Creating Pinecone index: {self.index_name}")
				self._pc.create_index(
					name=self.index_name,
					dimension=self.dimension,
					metric=self.metric,
					spec=ServerlessSpec(cloud=self.cloud, region=self.region),
				)
				# Brief wait until index is ready
				_t0 = time.time()
				while True:
					meta = next((i for i in self._pc.list_indexes() if i.get("name") == self.index_name), None)
					if meta and meta.get("status", {}).get("ready") is True:
						break
					if time.time() - _t0 > 30:
						break
					time.sleep(1)
				logger.info(f"✅ Pinecone index {self.index_name} ready")
			else:
				logger.info(f"✅ Pinecone index {self.index_name} already exists")
			
			self._index = self._pc.Index(self.index_name)
		except Exception as e:
			self._last_error = str(e)
			self._pc = None
			self._index = None
			logger.error(f"❌ Error inicializando Pinecone: {e}")

	# ---------- Basic ops ----------
	def is_available(self) -> bool:
		return self._index is not None

	def upsert_vectors(
		self,
		vectors: Iterable[Dict[str, Any]],
		namespace: Optional[str] = None,
	) -> Any:
		"""vectors: [{id, values, metadata?}]"""
		if not self._index:
			raise RuntimeError(self._last_error or "Pinecone index not available")
		
		vectors_list = list(vectors)
		
		# Actualizar caché local con los vectores que se están subiendo
		for vector in vectors_list:
			vector_id = vector.get("id")
			if vector_id:
				self._vector_cache[vector_id] = {
					"values": vector.get("values"),
					"metadata": vector.get("metadata", {}),
					"timestamp": time.time()
				}
		
		return self._index.upsert(vectors=vectors_list, namespace=namespace)

	def query(
		self,
		vector: List[float],
		top_k: int = 5,
		filter: Optional[Dict[str, Any]] = None,
		include_metadata: bool = True,
		namespace: Optional[str] = None,
	) -> Any:
		if not self._index:
			raise RuntimeError(self._last_error or "Pinecone index not available")
		return self._index.query(
			vector=vector,
			top_k=top_k,
			filter=filter,
			include_metadata=include_metadata,
			namespace=namespace,
		)

	def delete(
		self,
		ids: Optional[List[str]] = None,
		filter: Optional[Dict[str, Any]] = None,
		namespace: Optional[str] = None,
	) -> Any:
		if not self._index:
			raise RuntimeError(self._last_error or "Pinecone index not available")
		
		# Limpiar caché para los IDs eliminados
		if ids:
			for vector_id in ids:
				self._vector_cache.pop(vector_id, None)
		
		return self._index.delete(ids=ids, filter=filter, namespace=namespace)

	def get_index_stats(self) -> Dict[str, Any]:
		if not self._index:
			raise RuntimeError(self._last_error or "Pinecone index not available")
		try:
			stats = self._index.describe_index_stats()
			# Some SDKs return objects; coerce to dict if available
			if hasattr(stats, "to_dict"):
				stats = stats.to_dict()
			return stats
		except Exception as e:
			return {"error": str(e)}

	def vector_exists(self, vector_id: str, namespace: Optional[str] = None) -> bool:
		"""
		Verifica si un vector existe en el índice
		Usa caché local para evitar consultas innecesarias
		"""
		# Verificar caché primero
		if vector_id in self._vector_cache:
			cache_entry = self._vector_cache[vector_id]
			# Cache válido por 1 hora
			if time.time() - cache_entry["timestamp"] < 3600:
				return True
		
		# Si no está en caché, hacer consulta fetch
		try:
			if not self._index:
				return False
			
			# Intentar obtener el vector específico
			result = self._index.fetch(ids=[vector_id], namespace=namespace)
			
			if hasattr(result, 'vectors') and result.vectors:
				exists = vector_id in result.vectors
			elif isinstance(result, dict):
				exists = bool(result.get('vectors', {}).get(vector_id))
			else:
				exists = False
			
			# Actualizar caché si existe
			if exists and hasattr(result, 'vectors') and vector_id in result.vectors:
				vector_data = result.vectors[vector_id]
				self._vector_cache[vector_id] = {
					"values": vector_data.get("values", []),
					"metadata": vector_data.get("metadata", {}),
					"timestamp": time.time()
				}
			
			return exists
			
		except Exception as e:
			logger.error(f"Error verificando existencia del vector {vector_id}: {e}")
			return False

	def batch_vector_exists(self, vector_ids: List[str], namespace: Optional[str] = None) -> Dict[str, bool]:
		"""
		Verifica la existencia de múltiples vectores en batch
		Reduce el número de llamadas a la API
		"""
		results = {}
		ids_to_check = []
		
		# Verificar caché primero
		for vector_id in vector_ids:
			if vector_id in self._vector_cache:
				cache_entry = self._vector_cache[vector_id]
				# Cache válido por 1 hora
				if time.time() - cache_entry["timestamp"] < 3600:
					results[vector_id] = True
				else:
					ids_to_check.append(vector_id)
			else:
				ids_to_check.append(vector_id)
		
		# Consultar los IDs no cacheados
		if ids_to_check:
			try:
				if self._index:
					# Hacer fetch en batch
					result = self._index.fetch(ids=ids_to_check, namespace=namespace)
					
					if hasattr(result, 'vectors'):
						vectors = result.vectors
						for vector_id in ids_to_check:
							exists = vector_id in vectors
							results[vector_id] = exists
							
							# Actualizar caché si existe
							if exists:
								vector_data = vectors[vector_id]
								self._vector_cache[vector_id] = {
									"values": vector_data.get("values", []),
									"metadata": vector_data.get("metadata", {}),
									"timestamp": time.time()
								}
					elif isinstance(result, dict) and 'vectors' in result:
						vectors = result['vectors']
						for vector_id in ids_to_check:
							exists = vector_id in vectors
							results[vector_id] = exists
							
							# Actualizar caché si existe
							if exists and vector_id in vectors:
								vector_data = vectors[vector_id]
								self._vector_cache[vector_id] = {
									"values": vector_data.get("values", []),
									"metadata": vector_data.get("metadata", {}),
									"timestamp": time.time()
								}
				else:
					# Si no hay índice, asumir que no existen
					for vector_id in ids_to_check:
						results[vector_id] = False
						
			except Exception as e:
				logger.error(f"Error verificando existencia de vectores en batch: {e}")
				# En caso de error, asumir que no existen
				for vector_id in ids_to_check:
					results[vector_id] = False
		
		return results

	def clear_cache(self):
		"""Limpia el caché de vectores"""
		self._vector_cache.clear()
		logger.info("🧹 Cache de vectores de Pinecone limpiado")

	def get_cache_stats(self) -> Dict[str, Any]:
		"""Obtiene estadísticas del caché"""
		return {
			"cached_vectors": len(self._vector_cache),
			"cache_size_mb": len(str(self._vector_cache)) / (1024 * 1024)  # Aproximado
		}

	# ---------- Health ----------
	def get_status(self) -> Dict[str, Any]:
		ok = self.is_available()
		status: Dict[str, Any] = {
			"available": ok,
			"index": self.index_name,
			"dimension": self.dimension,
			"metric": self.metric,
			"cloud": self.cloud,
			"region": self.region,
		}
		if not ok:
			status["reason"] = self._last_error or "not ready"
			return status
		try:
			stats = self.get_index_stats()
			status["stats"] = stats
			status["cache"] = self.get_cache_stats()
		except Exception as e:
			status["stats_error"] = str(e)
		return status

	# ---------- Helper methods for Madrid knowledge ----------
	def upsert_madrid_content(self, poi_id: str, content_type: str, text: str, embedding: List[float]) -> bool:
		"""
		Helper específico para subir contenido de Madrid
		OPTIMIZADO: Verifica existencia antes de hacer upsert
		"""
		try:
			vector_id = f"{poi_id}_{content_type}"
			
			# Verificar si ya existe
			if self.vector_exists(vector_id):
				logger.info(f"⏭️ Vector {vector_id} ya existe, saltando upsert")
				return True
			
			metadata = {
				"poi_id": poi_id,
				"content_type": content_type,
				"text": text[:1000],  # Limitamos el texto en metadata
				"source": "wikipedia"
			}
			
			self.upsert_vectors([{
				"id": vector_id,
				"values": embedding,
				"metadata": metadata
			}])
			
			logger.info(f"✅ Vector {vector_id} subido exitosamente")
			return True
		except Exception as e:
			logger.error(f"❌ Error subiendo {poi_id}_{content_type}: {e}")
			return False

	def search_madrid_content(self, query_embedding: List[float], poi_id: str = None, content_type: str = None, top_k: int = 3) -> List[Dict]:
		"""Buscar contenido de Madrid con filtros opcionales"""
		try:
			filter_dict = {}
			if poi_id:
				filter_dict["poi_id"] = poi_id
			if content_type:
				filter_dict["content_type"] = content_type
			
			results = self.query(
				vector=query_embedding,
				top_k=top_k,
				filter=filter_dict if filter_dict else None,
				include_metadata=True
			)
			
			# Extraer resultados según el formato de respuesta de Pinecone
			if hasattr(results, 'matches'):
				return [{"id": match.id, "score": match.score, "metadata": match.metadata} 
				       for match in results.matches]
			elif isinstance(results, dict) and 'matches' in results:
				return results['matches']
			else:
				return []
				
		except Exception as e:
			logger.error(f"❌ Error buscando contenido: {e}")
			return []

	def get_madrid_pois_status(self) -> Dict[str, bool]:
		"""
		Obtiene el estado de todos los POIs de Madrid en el índice
		Usa batch_vector_exists para eficiencia
		"""
		from Server.core.agents.madrid_knowledge import ALL_POIS
		
		poi_vector_ids = [f"{poi['id']}_basic_info" for poi in ALL_POIS]
		return self.batch_vector_exists(poi_vector_ids)


# Exported instance used by the app
pinecone_service = PineconeService()