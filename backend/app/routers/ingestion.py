"""
FastAPI router for ingestion endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import uuid
from app.models.request import IngestionRequest
from app.models.response_model import IngestionResponse
from app.services.ingestion_service import IngestionService
from app.config import settings


router = APIRouter()
ingestion_service = IngestionService()


@router.post("/ingest",
             response_model=IngestionResponse,
             summary="Ingest book content",
             description="Upload and process book content for RAG queries")
async def ingest_book(request: IngestionRequest):
    """
    Endpoint to ingest book content into the system.

    This endpoint will:
    1. Chunk the provided content
    2. Generate embeddings using Cohere
    3. Store embeddings in Qdrant
    4. Store metadata in PostgreSQL
    """
    try:
        # Additional validation
        if len(request.content) < 10:
            raise HTTPException(status_code=400, detail="Content is too short to process")

        if len(request.content) > 1000000:  # 1MB limit
            raise HTTPException(status_code=400, detail="Content is too large to process (limit: 1MB)")

        # Generate a unique book ID
        book_id = str(uuid.uuid4())

        # Perform the ingestion
        result = ingestion_service.ingest_book(
            book_id=book_id,
            title=request.title,
            content=request.content,
            author=request.author,
            chunk_size=request.chunk_size,
            overlap=request.overlap
        )

        # Return the ingestion response
        return IngestionResponse(
            status=result["status"],
            chunks_created=result["chunks_created"],
            book_id=result["book_id"],
            message=result["message"]
        )

    except ValueError as e:
        # Handle validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle other errors
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/ingest/{book_id}",
            summary="Get ingestion status",
            description="Get the status and statistics for a specific book ingestion")
async def get_ingestion_status(book_id: str):
    """
    Endpoint to get the status and statistics for a specific book ingestion.
    """
    try:
        stats = ingestion_service.get_ingestion_stats(book_id)

        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])

        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ingestion status: {str(e)}")


@router.delete("/ingest/{book_id}",
               summary="Delete ingested book",
               description="Remove a book and all its chunks from the system")
async def delete_ingested_book(book_id: str):
    """
    Endpoint to delete an ingested book and all its associated data.
    """
    try:
        # Note: In a real implementation, you would need to:
        # 1. Remove all chunks from Qdrant
        # 2. Remove all chunk metadata from PostgreSQL
        # 3. Remove book metadata from PostgreSQL

        # For now, this is a placeholder
        return {
            "status": "success",
            "message": f"Book {book_id} deletion functionality would be implemented here"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete book: {str(e)}")


@router.get("/ingest",
            summary="List ingested books",
            description="Get a list of all ingested books")
async def list_ingested_books():
    """
    Endpoint to get a list of all ingested books.
    """
    try:
        # Note: In a real implementation, you would query the PostgreSQL database
        # to get a list of all books

        # For now, this is a placeholder
        return {
            "books": [],
            "total": 0,
            "message": "Book listing functionality would be implemented here"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list books: {str(e)}")