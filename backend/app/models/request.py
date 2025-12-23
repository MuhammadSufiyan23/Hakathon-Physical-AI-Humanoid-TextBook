"""
Pydantic models for request validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class QueryMode(str, Enum):
    """
    Enum for different query modes
    """
    FULL_BOOK = "full_book"
    SELECTED_TEXT_ONLY = "selected_text_only"


class QueryRequest(BaseModel):
    """
    Model for query requests
    """
    question: str = Field(..., min_length=1, max_length=1000, description="The user's question about the book content")
    selected_text: Optional[str] = Field(None, max_length=5000, description="Optional selected text for context isolation")
    mode: QueryMode = Field(QueryMode.FULL_BOOK, description="Query mode - defaults to full book search")


class IngestionRequest(BaseModel):
    """
    Model for book ingestion requests
    """
    title: str = Field(..., min_length=1, max_length=500, description="Title of the book")
    author: Optional[str] = Field(None, max_length=255, description="Author of the book")
    content: str = Field(..., min_length=1, description="The book content to be ingested")
    chunk_size: int = Field(500, ge=100, le=1000, description="Size of text chunks in tokens")
    overlap: int = Field(50, ge=0, le=200, description="Overlap between chunks in tokens")


class HealthCheckResponse(BaseModel):
    """
    Model for health check response
    """
    status: str = Field(..., description="Health status of the API")
    timestamp: str = Field(..., description="Timestamp of the health check")