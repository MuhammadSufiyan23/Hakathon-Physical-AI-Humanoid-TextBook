"""
PostgreSQL client wrapper for metadata storage using Neon
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, List, Optional
from app.config import settings
import json
import logging


class PostgresService:
    """
    Service class for PostgreSQL database operations
    """
    def __init__(self):
        self.connection_string = settings.database_url
        self._initialize_tables()

    def get_connection(self):
        """
        Get a new database connection
        """
        return psycopg2.connect(self.connection_string)

    def _initialize_tables(self):
        """
        Initialize required tables if they don't exist
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                # Create chunks table for storing chunk metadata
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS content_chunks (
                        id UUID PRIMARY KEY,
                        book_id VARCHAR(255) NOT NULL,
                        text_content TEXT,
                        page_number INTEGER,
                        chapter VARCHAR(255),
                        chunk_index INTEGER,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # Create books table for storing book metadata
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS books (
                        id UUID PRIMARY KEY,
                        title VARCHAR(500) NOT NULL,
                        author VARCHAR(255),
                        total_chunks INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # Create API keys table for authentication
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS api_keys (
                        id SERIAL PRIMARY KEY,
                        key_hash VARCHAR(255) UNIQUE NOT NULL,
                        name VARCHAR(255),
                        rate_limit INTEGER DEFAULT 100,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_used TIMESTAMP
                    );
                """)

                conn.commit()

    def store_chunk_metadata(self, chunk_id: str, book_id: str, text_content: str,
                           page_number: Optional[int] = None, chapter: Optional[str] = None,
                           chunk_index: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store chunk metadata in PostgreSQL

        Args:
            chunk_id: Unique identifier for the chunk
            book_id: ID of the book this chunk belongs to
            text_content: The actual text content
            page_number: Original page number (optional)
            chapter: Chapter name (optional)
            chunk_index: Index of this chunk in the book sequence
            metadata: Additional metadata (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO content_chunks (id, book_id, text_content, page_number, chapter, chunk_index, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (chunk_id, book_id, text_content, page_number, chapter, chunk_index, json.dumps(metadata) if metadata else None))
                    conn.commit()
                    return True
        except Exception as e:
            logging.error(f"Error storing chunk metadata: {e}")
            return False

    def get_chunk_metadata(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve chunk metadata by ID

        Args:
            chunk_id: Unique identifier for the chunk

        Returns:
            Chunk metadata dictionary or None if not found
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM content_chunks WHERE id = %s
                    """, (chunk_id,))
                    result = cursor.fetchone()
                    if result:
                        # Convert RealDictRow to regular dict
                        result = dict(result)
                        # Parse JSON metadata if it exists
                        if result['metadata']:
                            result['metadata'] = json.loads(result['metadata'])
                        return result
        except Exception as e:
            logging.error(f"Error retrieving chunk metadata: {e}")
            return None

    def get_chunks_by_book(self, book_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all chunks for a specific book

        Args:
            book_id: ID of the book

        Returns:
            List of chunk metadata dictionaries
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM content_chunks WHERE book_id = %s
                        ORDER BY chunk_index
                    """, (book_id,))
                    results = cursor.fetchall()
                    chunks = []
                    for result in results:
                        result = dict(result)
                        if result['metadata']:
                            result['metadata'] = json.loads(result['metadata'])
                        chunks.append(result)
                    return chunks
        except Exception as e:
            logging.error(f"Error retrieving chunks by book: {e}")
            return []

    def store_book_metadata(self, book_id: str, title: str, author: Optional[str] = None,
                          total_chunks: int = 0) -> bool:
        """
        Store book metadata in PostgreSQL

        Args:
            book_id: Unique identifier for the book
            title: Book title
            author: Book author (optional)
            total_chunks: Total number of chunks in the book

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO books (id, title, author, total_chunks)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            title = EXCLUDED.title,
                            author = EXCLUDED.author,
                            total_chunks = EXCLUDED.total_chunks
                    """, (book_id, title, author, total_chunks))
                    conn.commit()
                    return True
        except Exception as e:
            logging.error(f"Error storing book metadata: {e}")
            return False

    def get_book_metadata(self, book_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve book metadata by ID

        Args:
            book_id: Unique identifier for the book

        Returns:
            Book metadata dictionary or None if not found
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM books WHERE id = %s
                    """, (book_id,))
                    result = cursor.fetchone()
                    if result:
                        return dict(result)
        except Exception as e:
            logging.error(f"Error retrieving book metadata: {e}")
            return None


# Singleton instance
postgres_service = PostgresService()