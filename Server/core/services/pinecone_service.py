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
from typing import Any, Dict, Iterable, List, Optional


class PineconeService:
	def __init__(self) -> None:
		self.api_key = os.getenv("PINECONE_API_KEY")
		self.index_name = os.getenv("PINECONE_INDEX_NAME", "perez")  # Cambiado para usar tu .env
		self.dimension = int(os.getenv("PINECONE_DIMENSION", "1024"))  # Cambiado a 1024
		self.metric = os.getenv("PINECONE_METRIC", "cosine")
		self.cloud = os.getenv("PINECONE_CLOUD", "aws")
		self.region = os.getenv("PINECONE_REGION", "us-east-1")

		self._pc = None
		self._index = None
		self._last_error: Optional[str] = None

		if not self.api_key:
			self._last_error = "PINECONE_API_KEY not set"
			return

		try:
			from pinecone import Pinecone, ServerlessSpec  # type: ignore

			self._pc = Pinecone(api_key=self.api_key)
			# Create index if missing
			names = [i["name"] for i in self._pc.list_indexes()] if hasattr(self._pc, "list_indexes") else []
			if self.index_name not in names:
				print(f"Creating Pinecone index: {self.index_name}")
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
				print(f"✅ Pinecone index {self.index_name} ready")
			else:
				print(f"✅ Pinecone index {self.index_name} already exists")
			
			self._index = self._pc.Index(self.index_name)
		except Exception as e:  # pragma: no cover - environment-specific
			self._last_error = str(e)
			self._pc = None
			self._index = None
			print(f"❌ Error inicializando Pinecone: {e}")

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
		return self._index.upsert(vectors=list(vectors), namespace=namespace)

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
		return self._index.delete(ids=ids, filter=filter, namespace=namespace)

	def get_index_stats(self) -> Dict[str, Any]:
		if not self._index:
			raise RuntimeError(self._last_error or "Pinecone index not available")
		try:
			stats = self._index.describe_index_stats()
			# Some SDKs return objects; coerce to dict if available
			if hasattr(stats, "to_dict"):
				stats = stats.to_dict()
			return stats  # type: ignore
		except Exception as e:  # pragma: no cover
			return {"error": str(e)}

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
		except Exception as e:
			status["stats_error"] = str(e)
		return status

	# ---------- Helper methods for Madrid knowledge ----------
	def upsert_madrid_content(self, poi_id: str, content_type: str, text: str, embedding: List[float]) -> bool:
		"""Helper específico para subir contenido de Madrid"""
		try:
			vector_id = f"{poi_id}_{content_type}"
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
			return True
		except Exception as e:
			print(f"❌ Error subiendo {poi_id}_{content_type}: {e}")
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
			print(f"❌ Error buscando contenido: {e}")
			return []


# Exported instance used by the app
pinecone_service = PineconeService()