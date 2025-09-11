"""
Pinecone service (v3 SDK) with simple CRUD and health reporting.

Configuration via environment variables:
- PINECONE_API_KEY      (required for remote)
- PINECONE_INDEX_NAME   (default: "perez")
- PINECONE_DIMENSION    (default: 1024)
- PINECONE_METRIC       (default: "cosine")
- PINECONE_CLOUD        (default: "aws")
- PINECONE_REGION       (default: "us-east-1")
"""
from __future__ import annotations

import hashlib
import math
import os
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple


# Lazy import cache for embeddings
_EMBED_MODEL = None


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
		self._embed_model_error: Optional[str] = None

		# In-memory fallback vector store: {namespace: {id: (values, metadata)}}
		self._mem_store: Dict[str, Dict[str, Tuple[List[float], Optional[Dict[str, Any]]]]] = {}

		# Try to initialize remote Pinecone if API key is present
		if not self.api_key:
			self._last_error = "PINECONE_API_KEY not set"
		else:
			try:
				from pinecone import Pinecone, ServerlessSpec  # type: ignore

				self._pc = Pinecone(api_key=self.api_key)
				# Create index if missing
				names = [i["name"] for i in self._pc.list_indexes()] if hasattr(self._pc, "list_indexes") else []
				if self.index_name not in names:
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
				self._index = self._pc.Index(self.index_name)
			except Exception as e:  # pragma: no cover - environment-specific
				self._last_error = str(e)
				self._pc = None
				self._index = None

	# ---------- Embeddings ----------
	def _get_embed_model(self):
		"""Lazily load the sentence-transformers model."""
		global _EMBED_MODEL
		if _EMBED_MODEL is not None:
			return _EMBED_MODEL
		try:
			from sentence_transformers import SentenceTransformer  # type: ignore
			# E5-large-v2 uses 1024 dims and expects "query:"/"passage:" prefixes
			_EMBED_MODEL = SentenceTransformer("intfloat/e5-large-v2")
			return _EMBED_MODEL
		except Exception as e:  # pragma: no cover
			# Fallback handled by _hash_embed; keep error for status visibility
			self._embed_model_error = str(e)
			return None

	def _hash_embed(self, text: str) -> List[float]:
		"""Deterministic hash-based embedding fallback with L2 normalization."""
		dim = self.dimension
		buf = bytearray()
		seed = text.encode("utf-8")
		while len(buf) < dim * 4:
			seed = hashlib.sha256(seed).digest()
			buf.extend(seed)
		vals: List[float] = []
		for i in range(dim):
			chunk = bytes(buf[i * 4 : (i + 1) * 4])
			v = int.from_bytes(chunk, "little", signed=False)
			# Map to [0,1], then to [-1,1]
			x = (v / 4294967295.0) * 2.0 - 1.0
			vals.append(x)
		# Normalize
		norm = math.sqrt(sum(x * x for x in vals)) or 1.0
		return [x / norm for x in vals]

	def embed_text(self, text: str) -> List[float]:
		model = self._get_embed_model()
		if model is None:
			return self._hash_embed(f"passage: {text}")
		try:
			vec = model.encode([f"passage: {text}"], normalize_embeddings=True)[0]
			return vec.tolist() if hasattr(vec, "tolist") else list(vec)
		except Exception:
			return self._hash_embed(f"passage: {text}")

	def embed_texts(self, texts: List[str]) -> List[List[float]]:
		model = self._get_embed_model()
		if model is None:
			return [self._hash_embed(f"passage: {t}") for t in texts]
		try:
			vecs = model.encode([f"passage: {t}" for t in texts], normalize_embeddings=True)
			out: List[List[float]] = []
			for v in vecs:
				out.append(v.tolist() if hasattr(v, "tolist") else list(v))
			return out
		except Exception:
			return [self._hash_embed(f"passage: {t}") for t in texts]

	# ---------- Basic ops ----------
	def is_available(self) -> bool:
		return self._index is not None

	def upsert_vectors(
		self,
		vectors: Iterable[Dict[str, Any]],
		namespace: Optional[str] = None,
	) -> Any:
		"""vectors: [{id, values, metadata?}]"""
		ns = namespace or ""
		if self._index:
			return self._index.upsert(vectors=list(vectors), namespace=namespace)
		# In-memory fallback
		store = self._mem_store.setdefault(ns, {})
		count = 0
		for item in vectors:
			vid = item.get("id")
			values = item.get("values")
			metadata = item.get("metadata")
			if vid is None or values is None:
				continue
			store[str(vid)] = (list(values), metadata)
			count += 1
		return {"upserted_count": count}

	def query(
		self,
		vector: List[float],
		top_k: int = 5,
		filter: Optional[Dict[str, Any]] = None,
		include_metadata: bool = True,
		namespace: Optional[str] = None,
	) -> Any:
		ns = namespace or ""
		if self._index:
			res = self._index.query(
				vector=vector,
				top_k=top_k,
				filter=filter,
				include_metadata=include_metadata,
				namespace=namespace,
			)
			# Normalize result to list of dicts
			matches: List[Dict[str, Any]] = []
			if hasattr(res, "matches") and res.matches is not None:
				for m in res.matches:
					matches.append({"id": getattr(m, "id", None), "score": getattr(m, "score", None), "metadata": getattr(m, "metadata", None)})
			elif isinstance(res, dict):
				for m in res.get("matches", []) or []:
					if isinstance(m, dict):
						matches.append({"id": m.get("id"), "score": m.get("score"), "metadata": m.get("metadata")})
			return matches
		# In-memory fallback
		store = self._mem_store.get(ns, {})
		scored: List[Tuple[str, float, Optional[Dict[str, Any]]]] = []
		for vid, (vals, meta) in store.items():
			if filter and meta:
				ok = all(meta.get(k) == v for k, v in filter.items())
				if not ok:
					continue
			# Cosine similarity assuming normalized inputs
			score = sum(a * b for a, b in zip(vals, vector))
			scored.append((vid, score, meta))
		scored.sort(key=lambda x: x[1], reverse=True)
		out = [{"id": vid, "score": score, "metadata": meta} for vid, score, meta in scored[: top_k or 5]]
		return out

	def delete(
		self,
		ids: Optional[List[str]] = None,
		filter: Optional[Dict[str, Any]] = None,
		namespace: Optional[str] = None,
	) -> Any:
		ns = namespace or ""
		if self._index:
			return self._index.delete(ids=ids, filter=filter, namespace=namespace)
		# In-memory fallback
		store = self._mem_store.setdefault(ns, {})
		deleted = 0
		if ids:
			for vid in ids:
				if vid in store:
					store.pop(vid, None)
					deleted += 1
		elif filter:
			to_del = [vid for vid, (_, meta) in store.items() if meta and all(meta.get(k) == v for k, v in filter.items())]
			for vid in to_del:
				store.pop(vid, None)
			deleted += len(to_del)
		else:
			deleted = len(store)
			store.clear()
		return {"deleted_count": deleted}

	def get_index_stats(self) -> Dict[str, Any]:
		if not self._index:
			# In-memory stats
			total = sum(len(ns_store) for ns_store in self._mem_store.values())
			return {"vectors_stored": total, "namespaces": list(self._mem_store.keys())}
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
		embed_model_loaded = self._get_embed_model() is not None
		status: Dict[str, Any] = {
			"pinecone_available": ok,
			"faiss_available": False,
			"embedding_model_loaded": embed_model_loaded,
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
				"text": text[:1000],
				"source": "wikipedia",
			}
			self.upsert_vectors(
				[
					{
						"id": vector_id,
						"values": embedding,
						"metadata": metadata,
					}
				]
			)
			return True
		except Exception:
			return False

	def search_madrid_content(
		self, query_embedding: List[float], poi_id: str | None = None, content_type: str | None = None, top_k: int = 3
	) -> List[Dict]:
		"""Buscar contenido de Madrid con filtros opcionales"""
		try:
			filter_dict: Dict[str, Any] = {}
			if poi_id:
				filter_dict["poi_id"] = poi_id
			if content_type:
				filter_dict["content_type"] = content_type

			results = self.query(
				vector=query_embedding,
				top_k=top_k,
				filter=filter_dict if filter_dict else None,
				include_metadata=True,
			)

			# Result already normalized to list[dict]
			return results if isinstance(results, list) else []
		except Exception:
			return []


# Lazy getter for exported instance used by the app. This avoids import-time
# initialization races (useful when running uvicorn reloaders).
_pinecone_service_instance: Optional[PineconeService] = None


def get_pinecone_service() -> PineconeService:
	global _pinecone_service_instance
	if _pinecone_service_instance is None:
		_pinecone_service_instance = PineconeService()
	return _pinecone_service_instance


# ---- Module-level helpers expected by tests (use getter) ----
def embed_texts(texts: List[str]) -> List[List[float]]:
	return get_pinecone_service().embed_texts(texts)


def upsert_location_embeddings(items: List[Dict[str, Any]], namespace: Optional[str] = None) -> Any:
	"""items: [{id, embedding, metadata}]"""
	vectors = [
		{"id": it["id"], "values": it["embedding"], "metadata": it.get("metadata")}
		for it in items
	]
	return get_pinecone_service().upsert_vectors(vectors, namespace=namespace)


def query_location_embedding(embedding: List[float], top_k: int = 2, namespace: Optional[str] = None) -> Any:
	return get_pinecone_service().query(embedding, top_k=top_k, namespace=namespace)


def delete_location_embeddings(ids: List[str], namespace: Optional[str] = None) -> Any:
	return get_pinecone_service().delete(ids=ids, namespace=namespace)

