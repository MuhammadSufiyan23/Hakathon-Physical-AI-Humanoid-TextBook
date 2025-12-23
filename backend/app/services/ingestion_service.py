"""
Service for handling book content ingestion, chunking, and storage
"""
from typing import Dict, Any, List
from app.utils.chunking import chunk_text
from app.services.cohere_client import CohereClient
from app.services.qdrant_client import QdrantService
from app.services.postgres_client import PostgresService
from app.models.book_content import BookContentCreate
from app.models.content_chunk import ContentChunkCreate
from app.config import settings
import uuid
import logging


class IngestionService:
    """
    Service class for handling the complete book ingestion workflow
    """
    def __init__(self):
        self.cohere_client = CohereClient()
        self.qdrant_service = QdrantService()
        self.postgres_service = PostgresService()
        self.logger = logging.getLogger(__name__)

    def ingest_book(self, book_id: str, title: str, content: str, author: str = None,
                    chunk_size: int = 500, overlap: int = 50) -> Dict[str, Any]:
        """
        Ingest a book by chunking, embedding, and storing in vector and metadata databases.

        Args:
            book_id: Unique identifier for the book
            title: Title of the book
            content: Full content of the book
            author: Author of the book (optional)
            chunk_size: Size of text chunks in characters
            overlap: Overlap between chunks in characters

        Returns:
            Dictionary with ingestion results
        """
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")

        try:
            # Step 1: Chunk the content
            self.logger.info(f"Starting ingestion for book: {title}")
            chunks = self._chunk_text(content, chunk_size, overlap)
            self.logger.info(f"Content chunked into {len(chunks)} pieces")

            # Step 2: Generate embeddings for all chunks
            self.logger.info("Generating embeddings for content chunks...")
            embeddings = self.cohere_client.generate_embeddings(chunks)
            self.logger.info(f"Generated {len(embeddings)} embeddings")

            # Step 3: Store each chunk in Qdrant and PostgreSQL
            stored_chunk_ids = []
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                # Create chunk ID
                chunk_id = f"{book_id}_chunk_{i}"

                # Store embedding in Qdrant
                qdrant_id = self.qdrant_service.store_embedding(
                    text=chunk_text,
                    embedding=embedding,
                    metadata={
                        "book_id": book_id,
                        "chunk_index": i,
                        "original_length": len(chunk_text)
                    }
                )

                # Store metadata in PostgreSQL
                success = self.postgres_service.store_chunk_metadata(
                    chunk_id=chunk_id,
                    book_id=book_id,
                    text_content=chunk_text,
                    chunk_index=i,
                    metadata={
                        "qdrant_id": qdrant_id,
                        "original_length": len(chunk_text)
                    }
                )

                if success:
                    stored_chunk_ids.append(chunk_id)
                else:
                    self.logger.error(f"Failed to store chunk {chunk_id} in PostgreSQL")

            # Step 4: Store book metadata in PostgreSQL
            book_stored = self.postgres_service.store_book_metadata(
                book_id=book_id,
                title=title,
                author=author,
                total_chunks=len(stored_chunk_ids)
            )

            if not book_stored:
                self.logger.error(f"Failed to store book metadata for {book_id}")

            # Step 5: Return results
            result = {
                "status": "success",
                "book_id": book_id,
                "chunks_created": len(stored_chunk_ids),
                "message": f"Successfully ingested '{title}' with {len(stored_chunk_ids)} chunks"
            }

            self.logger.info(f"Ingestion completed for book: {title}")
            return result

        except Exception as e:
            self.logger.error(f"Error during book ingestion: {str(e)}")
            raise e

    def _chunk_text(self, content: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Internal method to chunk text content.

        Args:
            content: The text content to be chunked
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks

        Returns:
            List of text chunks
        """
        from app.utils.chunking import chunk_text as chunking_util
        return chunking_util(content, chunk_size, overlap)

    def validate_content(self, content: str) -> bool:
        """
        Validate content before ingestion.

        Args:
            content: Content to validate

        Returns:
            True if valid, False otherwise
        """
        if not content or not content.strip():
            return False

        # Check for minimum length
        if len(content.strip()) < 10:
            return False

        return True

    def get_ingestion_stats(self, book_id: str) -> Dict[str, Any]:
        """
        Get statistics about a book's ingestion.

        Args:
            book_id: ID of the book

        Returns:
            Dictionary with ingestion statistics
        """
        book_metadata = self.postgres_service.get_book_metadata(book_id)
        if not book_metadata:
            return {"error": "Book not found"}

        chunks = self.postgres_service.get_chunks_by_book(book_id)

        return {
            "book_id": book_id,
            "title": book_metadata["title"],
            "author": book_metadata["author"],
            "total_chunks": book_metadata["total_chunks"],
            "chunks_stored": len(chunks),
            "status": "complete" if len(chunks) == book_metadata["total_chunks"] else "incomplete"
        }

    def optimize_embeddings(self, embeddings: List[List[float]]) -> List[List[float]]:
        """
        Optimize embeddings to meet resource constraints (e.g., <512 dimensions).

        Args:
            embeddings: List of embedding vectors

        Returns:
            List of optimized embedding vectors
        """
        # Note: Cohere's embed-english-v3.0 returns 1024-dim vectors by default
        # To meet the <512 dim constraint, we could use dimensionality reduction
        # For now, we'll use the model that returns 512-dim vectors when configured properly
        # This is a placeholder for future optimization
        return embeddings


# Singleton instance
ingestion_service = IngestionService()