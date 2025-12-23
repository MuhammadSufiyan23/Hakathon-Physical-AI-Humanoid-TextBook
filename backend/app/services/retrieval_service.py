"""
Service for retrieving relevant content chunks based on user queries
"""
from typing import List, Dict, Any, Optional
from app.services.qdrant_client import QdrantService
from app.services.cohere_client import CohereClient
from app.services.postgres_client import PostgresService
from app.config import settings
import logging


class RetrievalService:
    """
    Service class for content retrieval using vector similarity search
    """
    def __init__(self):
        self.qdrant_service = QdrantService()
        self.cohere_client = CohereClient()  # Use Cohere for embeddings
        self.postgres_service = PostgresService()
        self.logger = logging.getLogger(__name__)

    def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings using Cohere.

        Args:
            text: Input text string

        Returns:
            List of floats representing the embedding vector
        """
        try:
            embeddings = self.cohere_client.generate_embeddings([text])
            return embeddings[0]  # Return first embedding
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
            raise e

    def retrieve_relevant_chunks(self, query: str, book_id: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant content chunks based on a query using vector similarity search.
        """
        try:
            # Generate embedding for the query using Cohere
            query_embedding = self.generate_embeddings(query)

            # Search for similar vectors in Qdrant
            similar_chunks = self.qdrant_service.search_similar(
                query_embedding=query_embedding,
                limit=limit
            )

            # Add additional metadata from PostgreSQL if available
            enhanced_chunks = []
            for chunk in similar_chunks:
                chunk_metadata = self.postgres_service.get_chunk_metadata(chunk["id"])
                enhanced_chunk = {
                    "id": chunk["id"],
                    "text": chunk["text"],
                    "metadata": chunk.get("metadata", {}),
                    "score": chunk.get("score", 0),
                    "source_metadata": chunk_metadata
                }
                enhanced_chunks.append(enhanced_chunk)

            return enhanced_chunks

        except Exception as e:
            self.logger.error(f"Error during content retrieval: {str(e)}")
            raise e

    def retrieve_by_selected_text(self, selected_text: str, question: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant content when using selected text mode.
        """
        try:
            chunk = {
                "id": f"selected_text_{hash(selected_text) % 10000}",
                "text": selected_text,
                "metadata": {
                    "source": "selected_text",
                    "original_length": len(selected_text),
                    "question": question
                },
                "score": 1.0,
                "source_metadata": None
            }
            return [chunk]

        except Exception as e:
            self.logger.error(f"Error during selected text retrieval: {str(e)}")
            raise e

    def hybrid_search(self, query: str, book_id: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining vector similarity and keyword matching.
        """
        try:
            return self.retrieve_relevant_chunks(query, book_id, limit)
        except Exception as e:
            self.logger.error(f"Error during hybrid search: {str(e)}")
            raise e

    def rerank_results(self, query: str, chunks: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Rerank retrieved chunks based on relevance to the query.
        """
        try:
            # Currently, no external reranker — just return top_n
            return chunks[:top_n]
        except Exception as e:
            self.logger.error(f"Error during result reranking: {str(e)}")
            return chunks[:top_n]

    def validate_retrieval_params(self, query: str, limit: int) -> bool:
        """
        Validate retrieval parameters.
        """
        if not query or len(query.strip()) < 1:
            return False
        if limit <= 0 or limit > 100:
            return False
        return True


# Singleton instance
retrieval_service = RetrievalService()