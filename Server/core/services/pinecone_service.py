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
    pinecone = None  # For environments without pinecone installed

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

try:
    import faiss
except ImportError:
    faiss = None

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
    """
    def __init__(self):
        self.settings = pinecone_settings
        self.index: Optional[Any] = None
        self._initialized = False
        self._use_faiss = False
        self._faiss_index = None
        self._faiss_metadata = {}
        self.embedding_model = None
        self._init_pinecone()
        self._init_embedding_model()

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

    def _init_embedding_model(self):
        """Initializes the sentence-transformers embedding model"""
        if SentenceTransformer is None:
            logging.error("sentence-transformers not installed. Embedding unavailable.")
            self.embedding_model = None
            return
        try:
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            logging.info("✅ Embedding model loaded: all-MiniLM-L6-v2")
        except Exception as e:
            logging.error(f"Error loading embedding model: {e}")
            self.embedding_model = None

    def is_available(self) -> bool:
        """Checks if Pinecone or FAISS is available"""
        return (self._initialized and self.index is not None) or self._use_faiss

    def embed_text(self, text: str) -> Optional[list]:
        """Returns embedding vector for input text using the loaded model"""
        if self.embedding_model is None:
            logging.warning("Embedding model not available.")
            return None
        return self.embedding_model.encode(text).tolist()

    def embed_texts(self, texts: list) -> Optional[list]:
        """Returns embedding vectors for a list of texts using the loaded model"""
        if self.embedding_model is None:
            logging.warning("Embedding model not available.")
            return None
        return self.embedding_model.encode(texts).tolist()

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

    def retrieve_similar(self, text: str, top_k: int = 5, filter: Optional[dict] = None) -> list:
        """Embeds text and queries for similar items"""
        vector = self.embed_text(text)
        if vector is None:
            return []
        return self.query(vector, top_k=top_k, filter=filter)

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

pinecone_service = PineconeService()

# Example usage:
# from Server.core.services.pinecone_service import pinecone_service
#
# # Embed and upsert a single document
# text = "Madrid is the capital of Spain."
# vector = pinecone_service.embed_text(text)
# pinecone_service.upsert_vectors([
#     {"id": "doc1", "values": vector, "metadata": {"text": text}}
# ])
#
# # Embed and upsert multiple documents
# texts = ["Madrid is the capital of Spain.", "Barcelona is a city in Spain."]
# vectors = pinecone_service.embed_texts(texts)
# pinecone_service.upsert_vectors([
#     {"id": f"doc{i}", "values": vec, "metadata": {"text": t}}
#     for i, (vec, t) in enumerate(zip(vectors, texts))
# ])
#
# # Retrieve similar documents
# results = pinecone_service.retrieve_similar("What is the capital of Spain?", top_k=3)
# for r in results:
#     print(r)
