"""
Pinecone Service for Semantic Search and Knowledge Retrieval
Integrates with MadridKnowledgeTool and agent workflows for Ratoncito Pérez
"""

from typing import List, Dict, Any, Optional, Union
import os
import sys

try:
    import pinecone
except ImportError:
    pinecone = None  # For environments without pinecone installed

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    from config import pinecone_settings
except ImportError:
    pinecone_settings = None

class PineconeService:
    """
    Service for managing semantic search and vector storage in Pinecone
    Used for historical/cultural context, stories, and dynamic queries
    """
    def __init__(self):
        self.settings = pinecone_settings
        self.index: Optional[Any] = None
        self._initialized = False
        self._init_pinecone()

    def _init_pinecone(self):
        """Initializes Pinecone client and index"""
        if pinecone is None or self.settings is None:
            print("⚠️ Pinecone not available or settings missing.")
            return
        try:
            pinecone.init(api_key=self.settings.api_key, environment=self.settings.environment)
            self.index = pinecone.Index(self.settings.index_name)
            self._initialized = True
            print(f"✅ PineconeService initialized - Index: {self.settings.index_name}")
        except Exception as e:
            print(f"❌ Error initializing Pinecone: {e}")
            self.index = None
            self._initialized = False

    def is_available(self) -> bool:
        """Checks if Pinecone is available and initialized"""
        return self._initialized and self.index is not None

    def upsert_vectors(self, vectors: List[Dict[str, Any]]) -> Union[Dict, None]:
        """
        Upserts a batch of vectors into Pinecone
        Each vector: {"id": str, "values": List[float], "metadata": Dict}
        """
        if not self.is_available():
            print("Pinecone not available for upsert.")
            return None
        try:
            items = [(v["id"], v["values"], v.get("metadata", {})) for v in vectors]
            result = self.index.upsert(items)
            return result
        except Exception as e:
            print(f"Error upserting vectors: {e}")
            return None

    def query(self, vector: List[float], top_k: int = 5, filter: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Queries Pinecone for nearest vectors
        Returns list of matches with metadata
        """
        if not self.is_available():
            print("Pinecone not available for query.")
            return []
        try:
            result = self.index.query(vector=vector, top_k=top_k, filter=filter or {}, include_metadata=True)
            return result.get("matches", [])
        except Exception as e:
            print(f"Error querying Pinecone: {e}")
            return []

    def delete(self, ids: List[str]) -> Union[Dict, None]:
        """
        Deletes vectors by IDs
        """
        if not self.is_available():
            print("Pinecone not available for delete.")
            return None
        try:
            result = self.index.delete(ids)
            return result
        except Exception as e:
            print(f"Error deleting vectors: {e}")
            return None


pinecone_service = PineconeService()