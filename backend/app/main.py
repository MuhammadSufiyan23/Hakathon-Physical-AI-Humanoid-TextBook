"""
Main FastAPI application for RAG Chatbot Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import query, health, ingestion
from app.config import settings
from app.middleware.auth import api_key_auth_middleware
import uvicorn
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app instance with increased timeout
app = FastAPI(
    title=settings.app_name,
    description="RAG Chatbot Backend API for querying book content",
    version="1.0.0",
    debug=settings.debug,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    # Increase default timeout to 120 seconds to avoid 504 Gateway Timeout
    # This helps when Cohere generation or Qdrant search takes longer
    default_timeout=120,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins like "http://localhost:3000" or your deployed frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware (if needed globally)
# Note: Currently applied per-route via dependencies

# Include routers
app.include_router(query.router, prefix="/api/v1", tags=["query"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(ingestion.router, prefix="/api/v1", tags=["ingestion"])

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint for the API
    """
    return {"message": "RAG Chatbot Backend API", "version": "1.0.0"}


if __name__ == "__main__":
    # Run with increased timeouts for development
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        timeout_keep_alive=120,        # Keep connections alive longer
        timeout_graceful_shutdown=120, # Allow longer shutdown
    )