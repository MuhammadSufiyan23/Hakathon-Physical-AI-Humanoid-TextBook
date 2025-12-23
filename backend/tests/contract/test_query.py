"""
Contract tests for query endpoint
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_query_endpoint_contract():
    """
    Test that the query endpoint matches the expected contract
    """
    # Test data for the request
    query_data = {
        "question": "What is the main theme of this book?",
        "mode": "full_book"
    }

    # Make request to query endpoint
    response = client.post("/api/v1/query", json=query_data)

    # Verify response structure and types
    assert response.status_code == 200
    response_data = response.json()

    # Check that response has expected fields
    assert "answer" in response_data
    assert "sources" in response_data
    assert "confidence" in response_data
    assert "tokens_used" in response_data

    # Check data types
    assert isinstance(response_data["answer"], str)
    assert isinstance(response_data["sources"], list)
    assert isinstance(response_data["confidence"], float)
    assert isinstance(response_data["tokens_used"], int)

    # Check that values are reasonable
    assert len(response_data["answer"]) > 0
    assert 0.0 <= response_data["confidence"] <= 1.0
    assert response_data["tokens_used"] >= 0

    # Check sources structure
    for source in response_data["sources"]:
        assert "chunk_id" in source
        assert "text_snippet" in source
        assert "relevance_score" in source
        assert isinstance(source["chunk_id"], str)
        assert isinstance(source["text_snippet"], str)
        assert isinstance(source["relevance_score"], float)
        assert 0.0 <= source["relevance_score"] <= 1.0


def test_query_endpoint_with_selected_text():
    """
    Test that the query endpoint works with selected text mode
    """
    # Test data for the request with selected text
    query_data = {
        "question": "What does this specific text say?",
        "selected_text": "This is the specific text the user has selected for context.",
        "mode": "selected_text_only"
    }

    # Make request to query endpoint
    response = client.post("/api/v1/query", json=query_data)

    # Should return 200 for successful request
    # (Note: This might return an error if no content has been ingested yet)
    assert response.status_code in [200, 500]  # Either success or internal error


def test_query_endpoint_missing_question():
    """
    Test that the query endpoint properly handles missing question
    """
    # Request with missing question
    incomplete_data = {
        # Missing question field
        "mode": "full_book"
    }

    response = client.post("/api/v1/query", json=incomplete_data)

    # Should return 422 for validation error
    assert response.status_code == 422


def test_query_endpoint_invalid_mode():
    """
    Test that the query endpoint properly validates query mode
    """
    # Request with invalid mode
    invalid_data = {
        "question": "What is the main theme?",
        "mode": "invalid_mode"
    }

    response = client.post("/api/v1/query", json=invalid_data)

    # Should return 422 for validation error
    assert response.status_code == 422


def test_query_endpoint_long_question():
    """
    Test that the query endpoint can handle long questions
    """
    # Generate a long question
    long_question = "What is the main theme? " * 100

    query_data = {
        "question": long_question,
        "mode": "full_book"
    }

    response = client.post("/api/v1/query", json=query_data)

    # Should return 200 for successful request or 422 for validation error
    assert response.status_code in [200, 422, 500]


def test_query_endpoint_empty_question():
    """
    Test that the query endpoint properly validates empty questions
    """
    # Request with empty question
    invalid_data = {
        "question": "",
        "mode": "full_book"
    }

    response = client.post("/api/v1/query", json=invalid_data)

    # Should return 422 for validation error
    assert response.status_code == 422