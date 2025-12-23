"""
Pydantic model for Content Chunk entity
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class ContentChunk(BaseModel):
    """
    Model representing a segment of book content that has been processed and embedded
    """
    id: str = Field(..., description="Unique identifier for the content chunk")
    book_id: str = Field(..., description="Foreign key to the Book Content")
    text: str = Field(..., min_length=1, max_length=10000, description="The actual text content")
    embedding: Optional[list] = Field(None, description="Cohere embedding vector (will be set separately)")
    page_number: Optional[int] = Field(None, description="Original page location, if applicable")
    chapter: Optional[str] = Field(None, max_length=255, description="Original chapter title, if applicable")
    chunk_index: int = Field(..., description="Sequence index within the book")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional chunk-specific information")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Timestamp when the chunk was created")

    class Config:
        # Allow arbitrary types for embedding vector handling
        arbitrary_types_allowed = True


class ContentChunkCreate(BaseModel):
    """
    Model for creating a new content chunk
    """
    book_id: str = Field(..., description="Foreign key to the Book Content")
    text: str = Field(..., min_length=1, max_length=10000, description="The actual text content")
    page_number: Optional[int] = Field(None, description="Original page location, if applicable")
    chapter: Optional[str] = Field(None, max_length=255, description="Original chapter title, if applicable")
    chunk_index: int = Field(..., description="Sequence index within the book")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional chunk-specific information")


class ContentChunkUpdate(BaseModel):
    """
    Model for updating an existing content chunk
    """
    text: Optional[str] = Field(None, min_length=1, max_length=10000, description="The actual text content")
    page_number: Optional[int] = Field(None, description="Original page location, if applicable")
    chapter: Optional[str] = Field(None, max_length=255, description="Original chapter title, if applicable")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional chunk-specific information")


class ContentChunkResponse(BaseModel):
    """
    Model for content chunk responses (without sensitive embedding data)
    """
    id: str = Field(..., description="Unique identifier for the content chunk")
    book_id: str = Field(..., description="Foreign key to the Book Content")
    text: str = Field(..., max_length=1000, description="A snippet of the text content")  # Limited for response
    page_number: Optional[int] = Field(None, description="Original page location, if applicable")
    chapter: Optional[str] = Field(None, max_length=255, description="Original chapter title, if applicable")
    chunk_index: int = Field(..., description="Sequence index within the book")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional chunk-specific information")