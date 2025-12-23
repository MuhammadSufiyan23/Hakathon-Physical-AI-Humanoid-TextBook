"""
Pydantic model for Book Content entity
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class BookContent(BaseModel):
    """
    Model representing a digital book and its metadata
    """
    id: str = Field(..., description="Unique identifier for the book")
    title: str = Field(..., min_length=1, max_length=500, description="Title of the book")
    author: Optional[str] = Field(None, max_length=255, description="Author of the book")
    content_chunks: Optional[List[str]] = Field(default_factory=list, description="List of content chunk IDs")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional book metadata")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Timestamp when the book was created")
    total_chunks: int = Field(default=0, description="Total number of content chunks in the book")
    total_pages: Optional[int] = Field(None, description="Total number of pages in the book (if applicable)")

    class Config:
        # Allow arbitrary types for UUID handling if needed
        arbitrary_types_allowed = True


class BookContentCreate(BaseModel):
    """
    Model for creating a new book content entry
    """
    title: str = Field(..., min_length=1, max_length=500, description="Title of the book")
    author: Optional[str] = Field(None, max_length=255, description="Author of the book")
    content: str = Field(..., min_length=1, description="The full content of the book")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional book metadata")
    chunk_size: int = Field(500, ge=100, le=1000, description="Size of text chunks in tokens")
    overlap: int = Field(50, ge=0, le=200, description="Overlap between chunks in tokens")


class BookContentUpdate(BaseModel):
    """
    Model for updating an existing book content entry
    """
    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Title of the book")
    author: Optional[str] = Field(None, max_length=255, description="Author of the book")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional book metadata")