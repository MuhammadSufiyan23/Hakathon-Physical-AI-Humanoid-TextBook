"""
Integration tests for selected text query functionality
"""
import pytest
from unittest.mock import patch, MagicMock
import uuid
from app.services.query_service import QueryService
from app.services.retrieval_service import RetrievalService
from app.services.generation_service import GenerationService


def test_selected_text_query_integration():
    """
    Test the complete selected text query flow from start to finish
    """
    # Create an instance of the query service
    query_service = QueryService()

    # Sample question and selected text
    question = "What does this specific text mean?"
    selected_text = "This specific text talks about the importance of context in understanding."

    # Mock the dependencies to avoid actual API calls during testing
    with patch.object(query_service.generation_service, 'generate_answer_from_context') as mock_generate:

        # Configure mock return values
        mock_generate.return_value = {
            "answer": "The text means that context is important for understanding.",
            "confidence": 0.88,
            "tokens_used": 12
        }

        # Perform the query with selected text mode
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

        # Verify that the correct method was called (context-specific generation)
        mock_generate.assert_called_once()


def test_selected_text_context_isolation():
    """
    Test that selected text mode properly isolates context
    """
    # Create an instance of the query service
    query_service = QueryService()

    # Sample question and selected text
    question = "What does this text say?"
    selected_text = "The sky is blue and the grass is green."

    # Mock to check that only the selected text is used
    with patch.object(query_service.retrieval_service, 'retrieve_by_selected_text') as mock_retrieve, \
         patch.object(query_service.generation_service, 'generate_answer_from_context') as mock_generate:

        # Configure mock return values
        mock_retrieve.return_value = [{
            "id": "selected_text_chunk",
            "text": selected_text,
            "metadata": {"source": "selected_text"},
            "score": 1.0,
            "source_metadata": None
        }]
        mock_generate.return_value = {
            "answer": "The text says the sky is blue and the grass is green.",
            "confidence": 0.9,
            "tokens_used": 15
        }

        # Perform the query with selected text mode
        result = query_service.query_book_content(
            question=question,
            selected_text=selected_text,
            mode="selected_text_only"
        )

        # Verify the result
        assert result is not None
        assert "answer" in result
        # The answer should be based only on the selected text, not external knowledge

        # Verify that retrieval used the selected text method
        mock_retrieve.assert_called_once_with(
            selected_text=selected_text,
            question=question
        )


def test_selected_text_with_insufficient_context():
    """
    Test behavior when selected text doesn't contain enough information to answer
    """
    # Create an instance of the query service
    query_service = QueryService()

    # Sample question and selected text that doesn't answer the question
    question = "What is the author's name?"
    selected_text = "This is just a sentence about random topics."

    # Mock the dependencies
    with patch.object(query_service.generation_service, 'generate_answer_from_context') as mock_generate:

        # Configure mock to return an answer indicating insufficient context
        mock_generate.return_value = {
            "answer": "The provided context does not contain information about the author's name.",
            "confidence": 0.4,  # Lower confidence since context doesn't answer the question
            "tokens_used": 18
        }

        # Perform the query with selected text mode
        result = query_service.query_book_content(
            question=question,
            selected_text=selected_text,
            mode="selected_text_only"
        )

        # Verify the result
        assert result is not None
        assert "answer" in result
        # The answer should acknowledge that the context doesn't contain the requested information


def test_selected_text_query_with_long_text():
    """
    Test selected text query with longer text
    """
    # Create an instance of the query service
    query_service = QueryService()

    # Sample question and longer selected text
    question = "What are the main points discussed?"
    selected_text = """
    The first main point is that effective communication requires clarity and precision.
    The second main point is that context is essential for proper understanding.
    The third main point is that feedback helps improve communication effectiveness.
    Additional details include examples of good and bad communication practices.
    """

    # Mock the dependencies
    with patch.object(query_service.generation_service, 'generate_answer_from_context') as mock_generate:

        mock_generate.return_value = {
            "answer": "The main points discussed are clarity in communication, the importance of context, and the role of feedback.",
            "confidence": 0.92,
            "tokens_used": 25
        }

        # Perform the query with selected text mode
        result = query_service.query_book_content(
            question=question,
            selected_text=selected_text,
            mode="selected_text_only"
        )

        # Verify the result
        assert result is not None
        assert len(result["answer"]) > 0
        assert 0.0 <= result["confidence"] <= 1.0


def test_selected_text_query_error_handling():
    """
    Test selected text query error handling
    """
    # Create an instance of the query service
    query_service = QueryService()

    # Sample question and selected text
    question = "What does this mean?"
    selected_text = "This is some text."

    # Mock generation to raise an exception
    with patch.object(query_service.generation_service, 'generate_answer_from_context') as mock_generate:
        mock_generate.side_effect = Exception("Generation service failed")

        # Perform the query - should handle the exception
        with pytest.raises(Exception):
            query_service.query_book_content(
                question=question,
                selected_text=selected_text,
                mode="selected_text_only"
            )


def test_comparison_between_modes():
    """
    Test that full_book and selected_text_only modes produce different results
    """
    # This test would require actual content to be ingested to properly compare
    # For now, we'll test that the service can handle both modes
    query_service = QueryService()

    question = "What is the topic?"
    selected_text = "This text is about machine learning."
    book_id = str(uuid.uuid4())

    # Mock both retrieval paths
    with patch.object(query_service.retrieval_service, 'retrieve_relevant_chunks') as mock_full_retrieve, \
         patch.object(query_service.retrieval_service, 'retrieve_by_selected_text') as mock_selected_retrieve, \
         patch.object(query_service.generation_service, 'generate_answer') as mock_full_generate, \
         patch.object(query_service.generation_service, 'generate_answer_from_context') as mock_selected_generate:

        # Setup mocks for full book mode
        mock_full_retrieve.return_value = [{
            "id": "chunk_1",
            "text": "The book discusses various topics including machine learning.",
            "metadata": {},
            "score": 0.8,
            "source_metadata": None
        }]
        mock_full_generate.return_value = {
            "answer": "The topic is machine learning as discussed in the book.",
            "confidence": 0.85,
            "tokens_used": 16
        }

        # Setup mocks for selected text mode
        mock_selected_retrieve.return_value = [{
            "id": f"selected_text_{hash(selected_text) % 10000}",
            "text": selected_text,
            "metadata": {"source": "selected_text"},
            "score": 1.0,
            "source_metadata": None
        }]
        mock_selected_generate.return_value = {
            "answer": "The topic is machine learning based on the selected text.",
            "confidence": 0.9,
            "tokens_used": 15
        }

        # Test full book mode
        full_result = query_service.query_book_content(
            question=question,
            selected_text=selected_text,
            mode="full_book"
        )

        # Test selected text mode
        selected_result = query_service.query_book_content(
            question=question,
            selected_text=selected_text,
            mode="selected_text_only"
        )

        # Both should return results but potentially with different answers/scores
        assert "answer" in full_result
        assert "answer" in selected_result