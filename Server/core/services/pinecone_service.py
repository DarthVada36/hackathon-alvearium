"""
Pinecone Service for Semantic Search and Knowledge Retrieval
Integrates with MadridKnowledgeTool and agent workflows for Ratoncito Pérez
"""

from typing import List, Dict, Any, Optional, Union
import os
import sys
import logging

try:
    import pinecone
except ImportError:
    pinecone = None


try:
    import faiss
except ImportError:
    faiss = None


try:
    from sentence_transformers import SentenceTransformer
    _embedder = SentenceTransformer("all-MiniLM-L6-v2")
except ImportError:
    _embedder = None


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    from config import pinecone_settings
except ImportError:
    pinecone_settings = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class PineconeService:
    """
    Service for managing semantic search and vector storage in Pinecone
    Used for historical/cultural context, stories, and dynamic queries
    Falls back to FAISS if Pinecone not available
    """
    def __init__(self):
        self.settings = pinecone_settings
        self.index: Optional[Any] = None
        self._initialized = False
        self._use_faiss = False
        self._faiss_index = None
        self._faiss_metadata = {}
        self.embedding_model = _embedder
        self._init_pinecone()

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string into a vector"""
        if not self.embedding_model:
            raise RuntimeError("Embedding model not loaded")
        return self.embedding_model.encode(text).tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple text strings into vectors"""
        if not self.embedding_model:
            raise RuntimeError("Embedding model not loaded")
        return self.embedding_model.encode(texts).tolist()

    def _init_pinecone(self):
        """Initializes Pinecone client and index or fallback to FAISS"""
        if pinecone is None or self.settings is None:
            logging.warning("⚠️ Pinecone not available or settings missing, using FAISS fallback.")
            self._init_faiss()
            return
        try:
            pinecone.init(api_key=self.settings.api_key, environment=self.settings.environment)
            self.index = pinecone.Index(self.settings.index_name)
            self._initialized = True
            logging.info(f"✅ PineconeService initialized - Index: {self.settings.index_name}")
        except Exception as e:
            logging.error(f"❌ Error initializing Pinecone: {e}")
            self._init_faiss()

    def _init_faiss(self):
        """Initialize FAISS fallback"""
        if faiss is None:
            logging.error("FAISS not available. No vector DB will work.")
            return
        self._use_faiss = True
        self._faiss_index = faiss.IndexFlatL2(384)  # Dimension for all-MiniLM-L6-v2
        self._faiss_metadata = {}
        logging.info("✅ FAISS fallback initialized")

    def is_available(self) -> bool:
        """Checks if Pinecone or FAISS is available"""
        return (self._initialized and self.index is not None) or self._use_faiss

    def upsert_vectors(self, vectors: List[Dict[str, Any]]) -> Union[Dict, None]:
        """
        Upserts a batch of vectors into Pinecone or FAISS
        Each vector: {"id": str, "values": List[float], "metadata": Dict}
        """
        if not self.is_available():
            logging.warning("No vector DB available for upsert.")
            return None
        try:
            if self._use_faiss:
                import numpy as np
                vecs = [v["values"] for v in vectors]
                ids = [v["id"] for v in vectors]
                metas = [v.get("metadata", {}) for v in vectors]
                self._faiss_index.add(np.array(vecs, dtype="float32"))
                for i, idx in enumerate(ids):
                    self._faiss_metadata[idx] = metas[i]
                return {"upserted": len(vectors)}
            else:
                items = [(v["id"], v["values"], v.get("metadata", {})) for v in vectors]
                return self.index.upsert(items)
        except Exception as e:
            logging.error(f"Error upserting vectors: {e}")
            return None

    def query(self, vector: List[float], top_k: int = 5, filter: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Queries Pinecone or FAISS for nearest vectors
        Returns list of matches with metadata
        """
        if not self.is_available():
            logging.warning("No vector DB available for query.")
            return []
        try:
            if self._use_faiss:
                import numpy as np
                vec = np.array([vector], dtype="float32")
                scores, idxs = self._faiss_index.search(vec, top_k)
                results = []
                for score, idx in zip(scores[0], idxs[0]):
                    if idx == -1:
                        continue
                    metadata = list(self._faiss_metadata.values())[idx]
                    results.append({"score": float(score), "metadata": metadata})
                return results
            else:
                result = self.index.query(vector=vector, top_k=top_k, filter=filter or {}, include_metadata=True)
                return result.get("matches", [])
        except Exception as e:
            logging.error(f"Error querying vectors: {e}")
            return []

    def delete(self, ids: List[str]) -> Union[Dict, None]:
        """Deletes vectors by IDs"""
        if not self.is_available():
            return None
        try:
            if self._use_faiss:
                # Not trivial: FAISS doesn't delete by id, only reset
                logging.warning("FAISS delete not supported, resetting index.")
                self._init_faiss()
                return {"deleted": len(ids)}
            return self.index.delete(ids)
        except Exception as e:
            logging.error(f"Error deleting vectors: {e}")
            return None

    def get_index_stats(self) -> Union[Dict, None]:
        """Returns index statistics"""
        if not self.is_available():
            return None
        try:
            if self._use_faiss:
                return {"vectors_stored": self._faiss_index.ntotal}
            return self.index.describe_index_stats()
        except Exception as e:
            logging.error(f"Error getting index stats: {e}")
            return None

    def get_status(self) -> dict:
        """Returns health/status info for Pinecone, FAISS, and embedding model"""
        status = {
            "pinecone_available": self._initialized and self.index is not None,
            "faiss_available": self._use_faiss and self._faiss_index is not None,
            "embedding_model_loaded": self.embedding_model is not None,
        }
        if status["pinecone_available"]:
            try:
                stats = self.get_index_stats()
                status["pinecone_index_stats"] = stats
            except Exception:
                status["pinecone_index_stats"] = None
        if status["faiss_available"]:
            status["faiss_vectors_stored"] = self._faiss_index.ntotal if self._faiss_index else None
        return status

pinecone_service = PineconeService()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generates embeddings for a list of texts"""
    if _embedder is None:
        logging.error("Embedding model not available.")
        return []
    return _embedder.encode(texts).tolist()


def upsert_location_embeddings(locations: List[Dict[str, Any]]) -> Union[Dict, None]:
    """Upserts embeddings for Madrid locations/POIs"""
    vectors = [
        {"id": loc["id"], "values": loc["embedding"], "metadata": loc.get("metadata", {})}
        for loc in locations
    ]
    return pinecone_service.upsert_vectors(vectors)


def query_location_embedding(query_embedding: List[float], top_k: int = 5, filter: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """Queries Pinecone/FAISS for similar locations/POIs"""
    return pinecone_service.query(query_embedding, top_k=top_k, filter=filter)


def delete_location_embeddings(ids: List[str]) -> Union[Dict, None]:
    """Deletes location embeddings by IDs"""
    return pinecone_service.delete(ids)

# Example usage
if __name__ == "__main__":
    sample_texts = ["La Plaza Mayor fue construida en 1619.", "El Palacio Real es la residencia oficial."]
    embeddings = embed_texts(sample_texts)

    upsert_location_embeddings([
        {"id": f"doc_{i}", "embedding": emb, "metadata": {"text": txt}}
        for i, (txt, emb) in enumerate(zip(sample_texts, embeddings))
    ])

    q_emb = embed_texts(["¿Quién construyó la Plaza Mayor?"])[0]
    results = query_location_embedding(q_emb, top_k=2)
    logging.info(f"Query results: {results}")
