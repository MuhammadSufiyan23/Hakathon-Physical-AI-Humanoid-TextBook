"""
FastAPI router for query endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import uuid
from app.models.request import QueryRequest, QueryMode
from app.models.response_model import QueryResponse, SourceReference
from app.services.query_service import QueryService
from app.config import settings


router = APIRouter()
query_service = QueryService()


@router.post("/query",
             response_model=QueryResponse,
             summary="Query book content",
             description="Ask questions about ingested book content using RAG methodology")
async def query_book(request: QueryRequest):
    """
    Endpoint to query book content using RAG methodology.

    This endpoint will:
    1. Take the user's question
    2. Depending on mode, either search in ingested content or use provided selected text
    3. Generate an answer based on the retrieved context
    4. Return the answer with sources and confidence score
    """
    try:
        # Additional validation beyond Pydantic
        if len(request.question.strip()) < 3:
            raise HTTPException(status_code=400, detail="Question must be at least 3 characters long")

        if len(request.question) > 1000:
            raise HTTPException(status_code=400, detail="Question is too long (max 1000 characters)")

        if request.selected_text and len(request.selected_text) > 5000:
            raise HTTPException(status_code=400, detail="Selected text is too long (max 5000 characters)")

        # Additional validation for selected text mode
        if request.mode == QueryMode.SELECTED_TEXT_ONLY:
            if not request.selected_text or len(request.selected_text.strip()) < 5:
                raise HTTPException(status_code=400, detail="Selected text must be provided and at least 5 characters long for selected_text_only mode")

        # Validate the request
        if not query_service.validate_query_params(
            question=request.question,
            mode=request.mode,
            selected_text=request.selected_text
        ):
            raise HTTPException(status_code=400, detail="Invalid query parameters")

        # Check query limits
        if not query_service.check_query_limits():
            raise HTTPException(status_code=429, detail="Query limit exceeded")

        # Process the query based on mode
        result = query_service.query_book_content(
            question=request.question,
            selected_text=request.selected_text,
            mode=request.mode
        )

        # Additional validation for selected text mode to ensure context isolation
        if request.mode == QueryMode.SELECTED_TEXT_ONLY and request.selected_text:
            # Log for monitoring context isolation
            if result.get("confidence", 0) < 0.5:
                # Lower confidence might indicate the model couldn't answer from the limited context
                pass  # In a real system, you might want to log this for analysis

        # Format the response
        sources = []
        for source in result["sources"]:
            try:
                source_ref = SourceReference(
                    chunk_id=source["chunk_id"],
                    text_snippet=source["text_snippet"],
                    relevance_score=source["relevance_score"]
                )
                sources.append(source_ref)
            except Exception:
                # If there's an issue with a specific source, skip it but continue
                continue

        # # Ensure we don't exceed response time limits
        # if result.get("response_time", 0) > settings.max_response_time:
        #     raise HTTPException(status_code=504, detail="Query timeout - response took too long")

        return QueryResponse(
            answer=result["answer"],
            sources=sources,
            confidence=result["confidence"],
            tokens_used=result["tokens_used"]
        )

    except ValueError as e:
        # Handle validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle other errors
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/query/capabilities",
            summary="Get query capabilities",
            description="Get information about query capabilities and limits")
async def get_query_capabilities():
    """
    Endpoint to get information about query capabilities and limits.
    """
    try:
        capabilities = {
            "modes": [mode.value for mode in QueryMode],
            "max_question_length": 1000,
            "max_selected_text_length": 5000,
            "max_sources_returned": 5,
            "response_time_limit": 2.0,  # seconds
            "description": "RAG-based query system for book content"
        }

        return capabilities
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get capabilities: {str(e)}")


@router.get("/query/stats",
            summary="Get query statistics",
            description="Get statistics about query performance")
async def get_query_stats():
    """
    Endpoint to get statistics about query performance.
    """
    try:
        stats = query_service.get_query_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get query stats: {str(e)}")


# Additional endpoint for testing purposes
@router.post("/query/debug",
             summary="Debug query processing",
             description="Debug endpoint to test query processing without full validation")
async def debug_query(request: QueryRequest):
    """
    Debug endpoint for testing query processing.
    This endpoint provides detailed information about the query process.
    """
    try:
        # For debugging, we'll return more detailed information
        result = query_service.query_book_content(
            question=request.question,
            selected_text=request.selected_text,
            mode=request.mode
        )

        debug_info = {
            "input": {
                "question": request.question,
                "selected_text": request.selected_text,
                "mode": request.mode.value
            },
            "result": result,
            "processed_at": "server_timestamp"
        }

        return debug_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug query failed: {str(e)}")