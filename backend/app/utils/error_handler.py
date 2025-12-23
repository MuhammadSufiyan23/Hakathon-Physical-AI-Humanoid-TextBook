"""
Error handling and logging infrastructure for the RAG Chatbot Backend
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Callable, Dict, Any
import logging
import traceback
from pydantic import ValidationError
from app.models.response_model import ErrorResponse


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGChatbotError(Exception):
    """
    Base exception class for RAG Chatbot Backend
    """
    def __init__(self, message: str, error_code: str = "GENERAL_ERROR", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class ContentNotFoundError(RAGChatbotError):
    """
    Exception raised when requested content is not found
    """
    def __init__(self, message: str = "Requested content not found"):
        super().__init__(message, "CONTENT_NOT_FOUND", 404)


class EmbeddingError(RAGChatbotError):
    """
    Exception raised when there's an error with embedding operations
    """
    def __init__(self, message: str = "Error occurred during embedding operation"):
        super().__init__(message, "EMBEDDING_ERROR", 500)


class RetrievalError(RAGChatbotError):
    """
    Exception raised when there's an error with content retrieval
    """
    def __init__(self, message: str = "Error occurred during content retrieval"):
        super().__init__(message, "RETRIEVAL_ERROR", 500)


class GenerationError(RAGChatbotError):
    """
    Exception raised when there's an error with text generation
    """
    def __init__(self, message: str = "Error occurred during text generation"):
        super().__init__(message, "GENERATION_ERROR", 500)


class ConfigurationError(RAGChatbotError):
    """
    Exception raised when there's a configuration issue
    """
    def __init__(self, message: str = "Configuration error"):
        super().__init__(message, "CONFIGURATION_ERROR", 500)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for the application
    """
    logger.error(f"Global exception occurred: {exc}")
    logger.error(f"Traceback: {traceback.format_exc()}")

    if isinstance(exc, RAGChatbotError):
        # Handle custom RAG Chatbot errors
        error_response = ErrorResponse(
            error=exc.message,
            error_code=exc.error_code,
            details={"path": str(request.url), "method": request.method}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict()
        )
    elif isinstance(exc, ValidationError):
        # Handle Pydantic validation errors
        error_response = ErrorResponse(
            error="Validation error",
            error_code="VALIDATION_ERROR",
            details={"errors": exc.errors(), "path": str(request.url), "method": request.method}
        )
        return JSONResponse(
            status_code=422,
            content=error_response.dict()
        )
    elif isinstance(exc, HTTPException):
        # Handle FastAPI HTTP exceptions
        error_response = ErrorResponse(
            error=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            details={"path": str(request.url), "method": request.method}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict()
        )
    else:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {exc}")
        error_response = ErrorResponse(
            error="An unexpected error occurred",
            error_code="UNEXPECTED_ERROR",
            details={"path": str(request.url), "method": request.method}
        )
        return JSONResponse(
            status_code=500,
            content=error_response.dict()
        )


def setup_error_handlers(app):
    """
    Setup error handlers for the FastAPI application
    """
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(RAGChatbotError, global_exception_handler)
    app.add_exception_handler(ValidationError, global_exception_handler)
    app.add_exception_handler(HTTPException, global_exception_handler)


def log_api_call(endpoint: str, method: str, status_code: int, duration: float):
    """
    Log API call information
    """
    logger.info(f"API Call: {method} {endpoint} - Status: {status_code} - Duration: {duration:.3f}s")


def log_error(error: Exception, context: str = ""):
    """
    Log error with context
    """
    logger.error(f"Error in {context}: {str(error)}")
    logger.error(f"Traceback: {traceback.format_exc()}")