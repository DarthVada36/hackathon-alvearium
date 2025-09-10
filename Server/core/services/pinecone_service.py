"""
Pinecone service (v3 SDK) with simple CRUD and health reporting.

Configuration via environment variables:
  - PINECONE_API_KEY  (required)
  - PINECONE_INDEX    (default: "perez")
	- PINECONE_DIM      (default: 1024)
  - PINECONE_METRIC   (default: "cosine")
  - PINECONE_CLOUD    (default: "aws")
  - PINECONE_REGION   (default: "us-east-1")
"""
from __future__ import annotations

import os
import time
import math
import hashlib
from typing import Any, Dict, Iterable, List, Optional, Tuple

# Lazy import cache for embeddings
_EMBED_MODEL = None


class PineconeService:
	def __init__(self) -> None:
		self.api_key = os.getenv("PINECONE_API_KEY")
		self.index_name = os.getenv("PINECONE_INDEX", "perez")
		self.dimension = int(os.getenv("PINECONE_DIM", "1024"))
		self.metric = os.getenv("PINECONE_METRIC", "cosine")
		self.cloud = os.getenv("PINECONE_CLOUD", "aws")
		self.region = os.getenv("PINECONE_REGION", "us-east-1")

		self._pc = None
		self._index = None
		self._last_error: Optional[str] = None
		self._embed_model_error: Optional[str] = None

		# In-memory fallback vector store: {namespace: {id: (values, metadata)}}
		self._mem_store: Dict[str, Dict[str, Tuple[List[float], Optional[Dict[str, Any]]]]] = {}

		if not self.api_key:
			self._last_error = "PINECONE_API_KEY not set"
			return

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
		"""Deterministic hash-based embedding fallback with normalization."""
		# Extend digest to required length
		dim = self.dimension
		buf = bytearray()
		seed = text.encode("utf-8")
		while len(buf) < dim * 4:
			seed = hashlib.sha256(seed).digest()
			buf.extend(seed)
		# Map bytes to floats in [-1, 1]
		vals: List[float] = []
		for i in range(dim):
			# take 4 bytes, convert to int, scale
			chunk = int.from_bytes(buf[i*4:(i+1)*4], byteorder="little", signed=False)
			x = (chunk / 0xFFFFFFFF) * 2.0 - 1.0
			vals.append(x)
		# Normalize
		norm = math.sqrt(sum(v*v for v in vals)) or 1.0
		return [v / norm for v in vals]

	# ---------- Basic ops ----------
	def is_available(self) -> bool:
		return self._index is not None

	# ---------- Embeddings helpers ----------
	def embed_text(self, text: str, is_query: bool = False) -> List[float]:
		model = self._get_embed_model()
		prefix = "query: " if is_query else "passage: "
		if not model:
			# Fallback
			return self._hash_embed(prefix + text)
		vec = model.encode(prefix + text, normalize_embeddings=True)
		return vec.tolist()

	def embed_texts(self, texts: List[str], is_query: bool = False) -> List[List[float]]:
		model = self._get_embed_model()
		prefix = "query: " if is_query else "passage: "
		if not model:
			# Fallback
			return [self._hash_embed(prefix + t) for t in texts]
		vecs = model.encode([prefix + t for t in texts], normalize_embeddings=True)
		return [v.tolist() for v in vecs]

	def upsert_vectors(
		self,
		vectors: Iterable[Dict[str, Any]],
		namespace: Optional[str] = None,
	) -> Any:
		"""vectors: [{id, values, metadata?}]"""
		if not self._index:
			# In-memory upsert
			ns = namespace or "default"
			store = self._mem_store.setdefault(ns, {})
			count = 0
			for v in vectors:
				vid = v["id"]
				vals = v["values"]
				meta = v.get("metadata")
				store[vid] = (list(vals), meta)
				count += 1
			return {"upserted_count": count}
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
			# In-memory query: cosine similarity (vectors normalized already)
			ns = namespace or "default"
			store = self._mem_store.get(ns, {})
			# compute dot product as cosine since vectors normalized
			def dot(a: List[float], b: List[float]) -> float:
				return sum(x*y for x, y in zip(a, b))
			results = []
			for vid, (vals, meta) in store.items():
				score = dot(vector, vals)
				results.append({"id": vid, "score": score, "metadata": meta if include_metadata else None})
			results.sort(key=lambda r: r["score"], reverse=True)
			return results[:top_k]
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
			ns = namespace or "default"
			store = self._mem_store.setdefault(ns, {})
			deleted = 0
			if ids:
				for vid in ids:
					if vid in store:
						store.pop(vid, None)
						deleted += 1
			elif filter:
				# basic filter on metadata equality
				to_del = [vid for vid, (_, meta) in store.items() if meta and all(meta.get(k) == v for k, v in filter.items())]
				for vid in to_del:
					store.pop(vid, None)
				deleted += len(to_del)
			return {"deleted_count": deleted}
		return self._index.delete(ids=ids, filter=filter, namespace=namespace)

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
			"faiss_available": False,  # no FAISS fallback in this build
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


# Exported instance used by the app
pinecone_service = PineconeService()


# ---- Module-level helpers expected by tests ----
def embed_texts(texts: List[str]) -> List[List[float]]:
	return pinecone_service.embed_texts(texts)


def upsert_location_embeddings(items: List[Dict[str, Any]], namespace: Optional[str] = None) -> Any:
	"""items: [{id, embedding, metadata}]"""
	vectors = [
		{"id": it["id"], "values": it["embedding"], "metadata": it.get("metadata")}
		for it in items
	]
	return pinecone_service.upsert_vectors(vectors, namespace=namespace)


def query_location_embedding(embedding: List[float], top_k: int = 2, namespace: Optional[str] = None) -> Any:
	return pinecone_service.query(embedding, top_k=top_k, namespace=namespace)


def delete_location_embeddings(ids: List[str], namespace: Optional[str] = None) -> Any:
	return pinecone_service.delete(ids=ids, namespace=namespace)

