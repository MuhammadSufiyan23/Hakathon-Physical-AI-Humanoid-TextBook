"""
Unit tests for PostgreSQL client wrapper
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.postgres_client import PostgresService


class TestPostgresService:
    """
    Unit tests for the PostgresService
    """
    def setup_method(self):
        """
        Set up test fixtures before each test method
        """
        self.service = PostgresService()
        # Mock the connection and cursor
        self.service.connection_string = "mock_connection_string"

    @patch('app.services.postgres_client.psycopg2.connect')
    def test_store_chunk_metadata_success(self, mock_connect):
        """
        Test successful storage of chunk metadata
        """
        # Mock the connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_cursor

        chunk_id = "test_chunk_id"
        book_id = "test_book_id"
        text_content = "Test content"
        page_number = 1
        chapter = "Chapter 1"
        chunk_index = 0
        metadata = {"key": "value"}

        result = self.service.store_chunk_metadata(
            chunk_id, book_id, text_content, page_number, chapter, chunk_index, metadata
        )

        # Verify the result
        assert result is True

        # Verify the cursor execute was called with correct parameters
        mock_cursor.execute.assert_called_once()
        args, kwargs = mock_cursor.execute.call_args
        assert "INSERT INTO content_chunks" in args[0]

    @patch('app.services.postgres_client.psycopg2.connect')
    def test_get_chunk_metadata(self, mock_connect):
        """
        Test retrieval of chunk metadata
        """
        # Mock the connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_cursor

        # Mock the fetchone result
        mock_row = {
            'id': 'test_chunk_id',
            'book_id': 'test_book_id',
            'text_content': 'Test content',
            'page_number': 1,
            'chapter': 'Chapter 1',
            'chunk_index': 0,
            'metadata': '{"key": "value"}'
        }
        mock_cursor.fetchone.return_value = mock_row

        chunk_id = "test_chunk_id"
        result = self.service.get_chunk_metadata(chunk_id)

        # Verify the cursor execute was called with correct parameters
        mock_cursor.execute.assert_called_once()
        args, kwargs = mock_cursor.execute.call_args
        assert "SELECT * FROM content_chunks WHERE id = %s" in args[0]

        # Verify the result
        if result:
            assert result['id'] == 'test_chunk_id'
            assert result['metadata']['key'] == 'value'

    @patch('app.services.postgres_client.psycopg2.connect')
    def test_store_book_metadata_success(self, mock_connect):
        """
        Test successful storage of book metadata
        """
        # Mock the connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_cursor

        book_id = "test_book_id"
        title = "Test Book"
        author = "Test Author"
        total_chunks = 5

        result = self.service.store_book_metadata(book_id, title, author, total_chunks)

        # Verify the result
        assert result is True

        # Verify the cursor execute was called with correct parameters
        mock_cursor.execute.assert_called_once()
        args, kwargs = mock_cursor.execute.call_args
        assert "INSERT INTO books" in args[0]

    @patch('app.services.postgres_client.psycopg2.connect')
    def test_get_book_metadata(self, mock_connect):
        """
        Test retrieval of book metadata
        """
        # Mock the connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_cursor

        # Mock the fetchone result
        mock_row = {
            'id': 'test_book_id',
            'title': 'Test Book',
            'author': 'Test Author',
            'total_chunks': 5
        }
        mock_cursor.fetchone.return_value = mock_row

        book_id = "test_book_id"
        result = self.service.get_book_metadata(book_id)

        # Verify the cursor execute was called with correct parameters
        mock_cursor.execute.assert_called_once()
        args, kwargs = mock_cursor.execute.call_args
        assert "SELECT * FROM books WHERE id = %s" in args[0]

        # Verify the result
        if result:
            assert result['id'] == 'test_book_id'
            assert result['title'] == 'Test Book'