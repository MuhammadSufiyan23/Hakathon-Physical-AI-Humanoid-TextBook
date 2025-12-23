"""
Integration tests for book content query functionality
"""
import pytest
from unittest.mock import patch, MagicMock
import uuid
from app.services.query_service import QueryService
from app.services.retrieval_service import RetrievalService
from app.services.generation_service import GenerationService


def test_full_book_query_integration():
    """
    Test the complete full book query flow from start to finish
    """
    # Create an instance of the query service
    query_service = QueryService()

    # Sample question
    question = "What are the main themes discussed in this book?"

    # Mock the dependencies to avoid actual API calls during testing
    with patch.object(query_service.retrieval_service, 'retrieve_relevant_chunks') as mock_retrieve, \
         patch.object(query_service.generation_service, 'generate_answer') as mock_generate:

        # Configure mock return values
        mock_retrieve.return_value = [
            {
                "id": str(uuid.uuid4()),
                "text": "The main themes include technology, innovation, and societal impact.",
                "metadata": {"page": 15, "chapter": "Introduction"},
                "score": 0.85
            },
            {
                "id": str(uuid.uuid4()),
                "text": "These themes are explored throughout the book with various examples.",
                "metadata": {"page": 22, "chapter": "Chapter 1"},
                "score": 0.78
            }
        ]
        mock_generate.return_value = {
            "answer": "The main themes of the book are technology, innovation, and societal impact.",
            "confidence": 0.92,
            "tokens_used": 15
        }

        # Perform the query
        result = query_service.query_book_content(
            question=question,
            mode="full_book"
        )

        # Verify the result
        assert result is not None
        assert "answer" in result
        assert "sources" in result
        assert "confidence" in result
        assert "tokens_used" in result

        # Verify the answer content
        assert len(result["answer"]) > 0
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["tokens_used"] >= 0

        # Verify that the correct methods were called
        mock_retrieve.assert_called_once_with(question, limit=5)
        mock_generate.assert_called_once()


def test_selected_text_query_integration():
    """
    Test the complete selected text query flow
    """
    # Create an instance of the query service
    query_service = QueryService()

    # Sample question and selected text
    question = "What does this specific text mean?"
    selected_text = "This specific text talks about the importance of context in understanding."

    # Mock the dependencies
    with patch.object(query_service.generation_service, 'generate_answer_from_context') as mock_generate:

        # Configure mock return values
        mock_generate.return_value = {
            "answer": "The text means that context is important for understanding.",
            "confidence": 0.88,
            "tokens_used": 12
        }

        # Perform the query with selected text
        result = query_service.query_book_content(
            question=question,
            selected_text=selected_text,
            mode="selected_text_only"
        )

        # Verify the result
        assert result is not None
        assert "answer" in result
        assert "sources" in result
        assert "confidence" in result
        assert "tokens_used" in result

        # Verify the answer content
        assert len(result["answer"]) > 0
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["tokens_used"] >= 0

        # Verify that the correct method was called
        mock_generate.assert_called_once()


def test_query_with_no_relevant_results():
    """
    Test query behavior when no relevant results are found
    """
    # Create an instance of the query service
    query_service = QueryService()

    # Sample question
    question = "What is the color of the invisible chair in this book?"

    # Mock retrieval to return no results
    with patch.object(query_service.retrieval_service, 'retrieve_relevant_chunks') as mock_retrieve, \
         patch.object(query_service.generation_service, 'generate_answer') as mock_generate:

        # Configure mock to return no results
        mock_retrieve.return_value = []
        mock_generate.return_value = {
            "answer": "The provided context does not contain information about this topic.",
            "confidence": 0.3,
            "tokens_used": 18
        }

        # Perform the query
        result = query_service.query_book_content(
            question=question,
            mode="full_book"
        )

        # Verify the result
        assert result is not None
        assert "answer" in result
        assert len(result["sources"]) == 0  # No sources since no relevant chunks found


def test_query_error_handling():
    """
    Test query error handling when services fail
    """
    # Create an instance of the query service
    query_service = QueryService()

    # Sample question
    question = "What is the main theme?"

    # Mock retrieval to raise an exception
    with patch.object(query_service.retrieval_service, 'retrieve_relevant_chunks') as mock_retrieve:
        mock_retrieve.side_effect = Exception("Retrieval service failed")

        # Perform the query - should handle the exception gracefully
        with pytest.raises(Exception):
            query_service.query_book_content(
                question=question,
                mode="full_book"
            )


def test_query_with_multiple_chunks():
    """
    Test query behavior with multiple relevant chunks
    """
    # Create an instance of the query service
    query_service = QueryService()

    # Sample question
    question = "Summarize the key concepts in this book?"

    # Mock retrieval to return multiple chunks
    mock_chunks = []
    for i in range(10):  # 10 chunks
        mock_chunks.append({
            "id": f"chunk_{i}",
            "text": f"This is content from section {i} discussing concept {i}.",
            "metadata": {"page": i*10, "chapter": f"Chapter {i//3}"},
            "score": 0.9 - (i * 0.05)  # Decreasing relevance
        })

    with patch.object(query_service.retrieval_service, 'retrieve_relevant_chunks') as mock_retrieve, \
         patch.object(query_service.generation_service, 'generate_answer') as mock_generate:

        mock_retrieve.return_value = mock_chunks
        mock_generate.return_value = {
            "answer": "The book discusses multiple concepts across different chapters.",
            "confidence": 0.85,
            "tokens_used": 25
        }

        # Perform the query
        result = query_service.query_book_content(
            question=question,
            mode="full_book"
        )

        # Verify the result
        assert result is not None
        assert len(result["sources"]) <= len(mock_chunks)  # May be limited by retrieval service


def test_query_response_formatting():
    """
    Test that query responses are properly formatted
    """
    # Create an instance of the query service
    query_service = QueryService()

    # Sample question
    question = "What is the main argument?"

    # Mock the dependencies
    with patch.object(query_service.retrieval_service, 'retrieve_relevant_chunks') as mock_retrieve, \
         patch.object(query_service.generation_service, 'generate_answer') as mock_generate:

        mock_retrieve.return_value = [
            {
                "id": "chunk_1",
                "text": "The main argument is that technology drives social change.",
                "metadata": {"page": 45, "chapter": "Conclusion"},
                "score": 0.92
            }
        ]
        mock_generate.return_value = {
            "answer": "The main argument is that technology drives social change.",
            "confidence": 0.89,
            "tokens_used": 14
        }

        # Perform the query
        result = query_service.query_book_content(
            question=question,
            mode="full_book"
        )

        # Verify response structure
        assert "answer" in result
        assert "sources" in result
        assert "confidence" in result
        assert "tokens_used" in result

        # Verify sources format
        assert isinstance(result["sources"], list)
        if result["sources"]:
            source = result["sources"][0]
            assert "chunk_id" in source
            assert "text_snippet" in source
            assert "relevance_score" in source