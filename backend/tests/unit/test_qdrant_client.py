"""
Unit tests for Qdrant client wrapper
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.qdrant_client import QdrantService


class TestQdrantService:
    """
    Unit tests for the QdrantService
    """
    def setup_method(self):
        """
        Set up test fixtures before each test method
        """
        # Temporarily disable actual initialization to avoid connection issues
        with patch('qdrant_client.QdrantClient'):
            self.service = QdrantService()
            # Manually set the client to a mock
            self.service.client = Mock()
            self.service.collection_name = "test_collection"

    def test_store_embedding(self):
        """
        Test storing an embedding in Qdrant
        """
        # Mock the client's upsert method
        self.service.client.upsert = Mock(return_value=True)

        text = "Test text"
        embedding = [0.1, 0.2, 0.3]
        metadata = {"test": "value"}

        result_id = self.service.store_embedding(text, embedding, metadata)

        # Verify the upsert was called with correct parameters
        self.service.client.upsert.assert_called_once()
        call_args = self.service.client.upsert.call_args
        assert call_args[1]["collection_name"] == "test_collection"

        # Verify that points were passed correctly
        points = call_args[1]["points"]
        assert len(points) == 1
        point = points[0]
        assert point.id is not None  # Should be a UUID
        assert point.vector == embedding
        assert point.payload["text"] == text
        assert point.payload["metadata"]["test"] == "value"

    def test_search_similar(self):
        """
        Test searching for similar vectors
        """
        # Mock search results
        mock_result = Mock()
        mock_result.id = "test_id"
        mock_result.payload = {"text": "Test text", "metadata": {"test": "value"}}
        mock_result.score = 0.8
        mock_search_result = [mock_result]

        self.service.client.search = Mock(return_value=mock_search_result)

        query_embedding = [0.1, 0.2, 0.3]
        results = self.service.search_similar(query_embedding, limit=5)

        # Verify the search was called with correct parameters
        self.service.client.search.assert_called_once_with(
            collection_name="test_collection",
            query_vector=query_embedding,
            limit=5,
            with_payload=True
        )

        # Verify the result structure
        assert len(results) == 1
        assert results[0]["id"] == "test_id"
        assert results[0]["text"] == "Test text"
        assert results[0]["metadata"]["test"] == "value"
        assert results[0]["score"] == 0.8