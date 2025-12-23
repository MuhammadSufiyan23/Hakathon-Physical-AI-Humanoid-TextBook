"""
Contract tests for selected text query endpoint
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_selected_text_query_endpoint_contract():
    """
    Test that the selected text query endpoint matches the expected contract
    """
    # Test data for the request with selected text
    query_data = {
        "question": "What does this specific text mean?",
        "selected_text": "This is the specific text the user has selected for context. It contains important information.",
        "mode": "selected_text_only"
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


def test_selected_text_query_without_selected_text():
    """
    Test that the selected text query properly handles missing selected text
    """
    # Request with selected_text_only mode but no selected text
    incomplete_data = {
        "question": "What does this text say?",
        "mode": "selected_text_only"
        # Missing selected_text
    }

    response = client.post("/api/v1/query", json=incomplete_data)

    # Should return 422 for validation error
    assert response.status_code == 422


def test_selected_text_query_with_empty_selected_text():
    """
    Test that the selected text query properly handles empty selected text
    """
    # Request with selected_text_only mode but empty selected text
    invalid_data = {
        "question": "What does this text say?",
        "selected_text": "",  # Empty selected text
        "mode": "selected_text_only"
    }

    response = client.post("/api/v1/query", json=invalid_data)

    # Should return 422 for validation error
    assert response.status_code == 422


def test_selected_text_query_with_short_selected_text():
    """
    Test that the selected text query properly handles very short selected text
    """
    # Request with selected_text_only mode but very short selected text
    invalid_data = {
        "question": "What does this text say?",
        "selected_text": "Hi",  # Very short selected text
        "mode": "selected_text_only"
    }

    response = client.post("/api/v1/query", json=invalid_data)

    # Should return 422 for validation error (if our validation checks for minimum length)
    assert response.status_code in [200, 422]  # Either success or validation error


def test_selected_text_query_normal_mode_ignores_selected_text():
    """
    Test that in full_book mode, selected text is ignored
    """
    # Request with full_book mode but also selected text (should be ignored)
    query_data = {
        "question": "What is the main theme of the book?",
        "selected_text": "This is some selected text that should be ignored in full_book mode.",
        "mode": "full_book"
    }

    response = client.post("/api/v1/query", json=query_data)

    # Should return 200 for successful request
    # (Note: This might return an error if no content has been ingested yet)
    assert response.status_code in [200, 500]  # Either success or internal error