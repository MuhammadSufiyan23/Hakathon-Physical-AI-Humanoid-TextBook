"""
Integration tests for book ingestion functionality
"""
import pytest
from unittest.mock import patch, MagicMock
import uuid
from app.services.ingestion_service import IngestionService
from app.services.cohere_client import CohereClient
from app.services.qdrant_client import QdrantService
from app.services.postgres_client import PostgresService


def test_book_ingestion_full_flow():
    """
    Test the complete book ingestion flow from start to finish
    """
    # Create an instance of the ingestion service
    ingestion_service = IngestionService()

    # Sample book content
    book_content = """
    Chapter 1: Introduction
    This is the beginning of our test book. It contains multiple sections that will be chunked and processed.

    The first paragraph introduces the main concepts that will be explored throughout the book.
    These concepts are fundamental to understanding the material that follows.

    Chapter 2: Advanced Topics
    In this chapter, we'll explore more complex ideas that build upon the foundation established earlier.
    These advanced topics require a solid understanding of the basics.

    Chapter 3: Conclusion
    In conclusion, we summarize the key points covered in this book and provide recommendations
    for further study and practical application of the concepts discussed.
    """

    book_title = "Test Book for Integration"
    book_author = "Integration Test Author"
    book_id = str(uuid.uuid4())

    # Mock the dependencies to avoid actual API calls during testing
    with patch.object(ingestion_service.cohere_client, 'generate_embeddings') as mock_embeddings, \
         patch.object(ingestion_service.qdrant_service, 'store_embedding') as mock_store_embedding, \
         patch.object(ingestion_service.postgres_service, 'store_chunk_metadata') as mock_store_chunk, \
         patch.object(ingestion_service.postgres_service, 'store_book_metadata') as mock_store_book:

        # Configure mock return values
        mock_embeddings.return_value = [[0.1, 0.2, 0.3, 0.4]]  # Mock embedding vector
        mock_store_embedding.return_value = str(uuid.uuid4())
        mock_store_chunk.return_value = True
        mock_store_book.return_value = True

        # Perform the ingestion
        result = ingestion_service.ingest_book(
            book_id=book_id,
            title=book_title,
            author=book_author,
            content=book_content,
            chunk_size=300,
            overlap=50
        )

        # Verify the result
        assert result is not None
        assert "chunks_created" in result
        assert result["status"] == "success"
        assert result["book_id"] == book_id

        # Verify that the correct number of calls were made
        # The content should be split into multiple chunks
        assert mock_embeddings.call_count > 0
        assert mock_store_embedding.call_count > 0
        assert mock_store_chunk.call_count > 0
        assert mock_store_book.call_count == 1


def test_text_chunking_logic():
    """
    Test the text chunking logic specifically
    """
    ingestion_service = IngestionService()

    # Long text that should be split into multiple chunks
    long_text = "Sentence. " * 100  # 100 sentences

    # Test chunking with different sizes
    chunks = ingestion_service._chunk_text(long_text, chunk_size=50, overlap=10)

    # Verify that we got multiple chunks
    assert len(chunks) > 1

    # Verify that chunks are not empty
    for chunk in chunks:
        assert len(chunk.strip()) > 0

    # Verify that the total content is preserved (approximately)
    combined_chunks = " ".join(chunks)
    assert len(combined_chunks) >= len(long_text) * 0.9  # Allow for some splitting artifacts


def test_ingestion_with_special_characters():
    """
    Test ingestion with special characters and edge cases
    """
    ingestion_service = IngestionService()

    # Text with special characters
    special_content = """
    Chapter 1: Introduction
    This chapter contains special characters: àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ
    It also has numbers: 1234567890
    And symbols: !@#$%^&*()_+-=[]{}|;':",./<>?
    """

    book_id = str(uuid.uuid4())
    book_title = "Special Characters Test"

    with patch.object(ingestion_service.cohere_client, 'generate_embeddings') as mock_embeddings, \
         patch.object(ingestion_service.qdrant_service, 'store_embedding') as mock_store_embedding, \
         patch.object(ingestion_service.postgres_service, 'store_chunk_metadata') as mock_store_chunk, \
         patch.object(ingestion_service.postgres_service, 'store_book_metadata') as mock_store_book:

        mock_embeddings.return_value = [[0.1, 0.2, 0.3, 0.4]]
        mock_store_embedding.return_value = str(uuid.uuid4())
        mock_store_chunk.return_value = True
        mock_store_book.return_value = True

        result = ingestion_service.ingest_book(
            book_id=book_id,
            title=book_title,
            content=special_content
        )

        assert result is not None
        assert result["status"] == "success"


def test_empty_content_ingestion():
    """
    Test ingestion with empty content
    """
    ingestion_service = IngestionService()

    with pytest.raises(ValueError, match="Content cannot be empty"):
        ingestion_service.ingest_book(
            book_id=str(uuid.uuid4()),
            title="Empty Content Test",
            content=""
        )


def test_single_chunk_ingestion():
    """
    Test ingestion with content that fits in a single chunk
    """
    ingestion_service = IngestionService()

    short_content = "This is a short piece of content that fits in a single chunk."

    book_id = str(uuid.uuid4())
    book_title = "Short Content Test"

    with patch.object(ingestion_service.cohere_client, 'generate_embeddings') as mock_embeddings, \
         patch.object(ingestion_service.qdrant_service, 'store_embedding') as mock_store_embedding, \
         patch.object(ingestion_service.postgres_service, 'store_chunk_metadata') as mock_store_chunk, \
         patch.object(ingestion_service.postgres_service, 'store_book_metadata') as mock_store_book:

        mock_embeddings.return_value = [[0.1, 0.2, 0.3, 0.4]]
        mock_store_embedding.return_value = str(uuid.uuid4())
        mock_store_chunk.return_value = True
        mock_store_book.return_value = True

        result = ingestion_service.ingest_book(
            book_id=book_id,
            title=book_title,
            content=short_content,
            chunk_size=1000  # Large chunk size to ensure single chunk
        )

        assert result is not None
        assert result["status"] == "success"
        assert result["chunks_created"] == 1