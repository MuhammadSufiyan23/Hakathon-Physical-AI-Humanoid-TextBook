"""
Unit tests for Cohere client wrapper
"""
import pytest
from unittest.mock import Mock, patch
from app.services.cohere_client import CohereClient


class TestCohereClient:
    """
    Unit tests for the CohereClient service
    """
    def setup_method(self):
        """
        Set up test fixtures before each test method
        """
        self.client = CohereClient()

    @patch('app.services.cohere_client.cohere.Client')
    def test_generate_embeddings(self, mock_cohere_class):
        """
        Test that embeddings are generated correctly
        """
        # Mock the Cohere client response
        mock_client_instance = Mock()
        mock_client_instance.embed.return_value = Mock()
        mock_client_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3, 0.4]]
        mock_cohere_class.return_value = mock_client_instance

        texts = ["Hello world", "Test text"]
        result = self.client.generate_embeddings(texts)

        # Verify the result
        assert len(result) == 2
        assert result[0] == [0.1, 0.2, 0.3, 0.4]
        assert result[1] == [0.1, 0.2, 0.3, 0.4]

        # Verify the method was called with correct parameters
        mock_client_instance.embed.assert_called_once_with(
            texts=texts,
            model="embed-english-v3.0",
            input_type="search_document"
        )

    @patch('app.services.cohere_client.cohere.Client')
    def test_generate_text(self, mock_cohere_class):
        """
        Test that text generation works correctly
        """
        # Mock the Cohere client response
        mock_client_instance = Mock()
        mock_generation = Mock()
        mock_generation.text = "Generated response"
        mock_generations_result = Mock()
        mock_generations_result.generations = [mock_generation]
        mock_client_instance.generate.return_value = mock_generations_result
        mock_cohere_class.return_value = mock_client_instance

        prompt = "Test prompt"
        result = self.client.generate_text(prompt)

        # Verify the result
        assert result == "Generated response"

        # Verify the method was called with correct parameters
        mock_client_instance.generate.assert_called_once_with(
            model="command-r-plus",
            prompt=prompt,
            max_tokens=500,
            temperature=0.3,
        )

    @patch('app.services.cohere_client.cohere.Client')
    def test_rerank(self, mock_cohere_class):
        """
        Test that reranking works correctly
        """
        # Mock the Cohere client response
        mock_client_instance = Mock()
        mock_result = Mock()
        mock_result.index = 0
        mock_result.relevance_score = 0.9
        mock_result.document = "Test document"
        mock_rerank_result = Mock()
        mock_rerank_result.results = [mock_result]
        mock_client_instance.rerank.return_value = mock_rerank_result
        mock_cohere_class.return_value = mock_client_instance

        query = "Test query"
        documents = ["Doc 1", "Doc 2"]
        result = self.client.rerank(query, documents, top_n=1)

        # Verify the result structure
        assert len(result) == 1
        assert result[0]["index"] == 0
        assert result[0]["relevance_score"] == 0.9
        assert result[0]["document"] == "Test document"