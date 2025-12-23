"""
Pydantic models for response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class SourceReference(BaseModel):
    """
    Model for source references in responses
    """
    chunk_id: str = Field(..., description="ID of the content chunk used as source")
    text_snippet: str = Field(..., max_length=500, description="Snippet of the source text")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score of this source")


class QueryResponse(BaseModel):
    """
    Model for query response
    """
    answer: str = Field(..., description="The AI-generated answer to the question")
    sources: List[SourceReference] = Field(default_factory=list, description="List of sources used to generate the answer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the generated answer")
    tokens_used: int = Field(..., ge=0, description="Number of tokens used in the response")


class IngestionResponse(BaseModel):
    """
    Model for ingestion response
    """
    status: str = Field(..., description="Status of the ingestion process")
    chunks_created: int = Field(..., ge=0, description="Number of content chunks created")
    book_id: str = Field(..., description="ID of the book that was ingested")
    message: str = Field(..., description="Additional information about the ingestion")


class HealthStatus(BaseModel):
    """
    Model for health status response
    """
    status: str = Field(..., description="Health status of the API")
    timestamp: str = Field(..., description="Timestamp of the health check")
    services: Dict[str, bool] = Field(default_factory=dict, description="Status of dependent services")


class ErrorResponse(BaseModel):
    """
    Model for error responses
    """
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code if applicable")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")