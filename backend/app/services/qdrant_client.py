"""
Qdrant client wrapper for vector storage operations
"""
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from app.config import settings
from typing import List, Dict, Any
import uuid
import logging


class QdrantService:
    """
    Service class for Qdrant vector database operations
    """
    def __init__(self):
        # Initialize Qdrant client
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key if hasattr(settings, 'qdrant_api_key') else None,
            timeout=60
        )
        self.collection_name = "book_content"
        self.embedding_dim = 1024  # Fixed for Cohere embed-english-v3.0
        self.logger = logging.getLogger(__name__)
        self._initialize_collection()

    def _initialize_collection(self):
        """Idempotent collection initialization with fixed 1024 dim"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            current_dim = collection_info.config.params.vectors.size
            if current_dim != self.embedding_dim:
                self.logger.warning(
                    f"Dimension mismatch: expected {self.embedding_dim}, got {current_dim}. Recreating collection..."
                )
                self.client.delete_collection(self.collection_name)
                raise ValueError("Dimension mismatch")
            print(f"Collection '{self.collection_name}' already exists (dim: {current_dim}) – skipping creation.")
        except Exception as e:
            if "not found" in str(e).lower():
                print(f"Collection '{self.collection_name}' not found – creating with dim {self.embedding_dim}...")
            else:
                print(f"Collection issue: {e} – recreating...")
            
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE,
                ),
            )
            print(f"Collection '{self.collection_name}' created successfully with dim {self.embedding_dim}!")

    def store_embedding(self, text: str, embedding: List[float], metadata: Dict[str, Any]) -> str:
        """
        Store a text embedding in Qdrant
        """
        vector_id = str(uuid.uuid4())

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=vector_id,
                    vector=embedding,
                    payload={
                        "text": text,
                        "metadata": metadata
                    }
                )
            ]
        )
        return vector_id

    def search_similar(self, query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar vectors using the new Qdrant API (.query_points)
        """
        try:
            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,        # New parameter name: 'query' instead of 'query_vector'
                limit=limit,
                with_payload=True,            # To get text and metadata
                with_vectors=False,           # We don't need the vector back
            )

            results = []
            for point in search_result.points:
                results.append({
                    "id": point.id,
                    "text": point.payload.get("text", ""),
                    "metadata": point.payload.get("metadata", {}),
                    "score": point.score
                })
            return results

        except Exception as e:
            self.logger.error(f"Search error: {e}")
            print(f"Search error: {e}")
            return []

    def get_all_points(self) -> List[Dict[str, Any]]:
        """
        Get all points (for debugging)
        """
        results = self.client.scroll(
            collection_name=self.collection_name,
            limit=10000,
            with_payload=True,
            with_vectors=False
        )

        points = []
        for point in results[0]:
            points.append({
                "id": point.id,
                "text": point.payload.get("text", ""),
                "metadata": point.payload.get("metadata", {})
            })

        return points

    def delete_collection(self):
        """
        Delete collection for reset
        """
        try:
            self.client.delete_collection(self.collection_name)
            print("Collection deleted!")
        except Exception as e:
            print(f"Error deleting collection: {e}")


# Singleton instance
qdrant_service = QdrantService()