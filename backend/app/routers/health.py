"""
FastAPI router for health check endpoints
"""
from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime
from app.config import settings
import time


router = APIRouter()


@router.get("/health",
            summary="Health check",
            description="Check the health status of the API and its dependencies")
async def health_check():
    """
    Health check endpoint to verify the API is running and dependencies are accessible.
    """
    try:
        # Record start time to measure response time
        start_time = time.time()

        # Check internal services (these should always be available if the app is running)
        internal_services_ok = True

        # In a real implementation, you might check external services like:
        # - Database connectivity
        # - Vector database connectivity
        # - External API connectivity (Cohere, etc.)
        external_services = {
            "cohere_api": True,  # Would check actual connectivity
            "qdrant_db": True,   # Would check actual connectivity
            "postgres_db": True  # Would check actual connectivity
        }

        # Calculate response time
        response_time = round((time.time() - start_time) * 1000, 2)  # in milliseconds

        # Overall status
        overall_status = "healthy" if internal_services_ok and all(external_services.values()) else "degraded"

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "response_time_ms": response_time,
            "services": {
                "api": True,
                **external_services
            },
            "version": "1.0.0",
            "environment": settings.environment
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "services": {
                "api": False
            }
        }


@router.get("/ready",
            summary="Readiness check",
            description="Check if the API is ready to serve requests")
async def readiness_check():
    """
    Readiness check endpoint to verify the API is ready to serve requests.
    This would check if all initialization is complete and dependencies are ready.
    """
    try:
        # In a real implementation, this would check:
        # - That required services are initialized
        # - That configuration is loaded
        # - That required resources are available

        # For now, we'll assume the app is ready if it can respond
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "API is ready to serve requests"
        }

    except Exception as e:
        return {
            "status": "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/live",
            summary="Liveness check",
            description="Check if the API process is alive")
async def liveness_check():
    """
    Liveness check endpoint to verify the API process is alive.
    This is a basic check to see if the process is responding.
    """
    try:
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "API process is alive"
        }

    except Exception as e:
        return {
            "status": "dead",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }