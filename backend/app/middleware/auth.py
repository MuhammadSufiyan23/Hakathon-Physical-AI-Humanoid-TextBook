"""
Authentication middleware for API key validation
"""
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os
import hashlib
import time
from app.services.postgres_client import PostgresService
from app.config import settings


class APIKeyAuth:
    """
    API Key authentication middleware
    """
    def __init__(self):
        self.postgres_service = PostgresService()
        # For development/testing, allow bypassing auth with environment variable
        self.bypass_auth = settings.environment == "development" and os.getenv("BYPASS_API_AUTH", "false").lower() == "true"
        # Rate limiting storage (in production, use Redis or similar)
        self.request_times = {}

    async def authenticate(self, request: Request) -> bool:
        """
        Authenticate the request using API key from header
        """
        if self.bypass_auth:
            return True

        # Get API key from header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key is missing or invalid. Use Bearer token format."
            )

        api_key = auth_header[7:]  # Remove "Bearer " prefix
        return self._validate_api_key(api_key)

    def _validate_api_key(self, api_key: str) -> bool:
        """
        Validate the API key against stored keys
        """
        if not api_key:
            return False

        # Hash the API key for comparison (in a real system, keys would be stored hashed)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # In a real implementation, you would check against the database
        # For now, we'll allow any non-empty key in development
        if settings.environment == "development":
            # For development, just check if it's a reasonable length
            return len(api_key) >= 10

        # In production, check against database
        # This is a simplified check - in reality you'd query the database
        # to see if the hashed key exists and is active
        return len(api_key) >= 10  # Placeholder for actual validation

    def check_rate_limit(self, api_key: str) -> bool:
        """
        Check if the API key has exceeded its rate limit
        """
        if settings.environment == "development":
            # No rate limiting in development
            return True

        # Get rate limit from database (simplified)
        # In a real implementation, you'd fetch this from the database
        rate_limit = 100  # Default rate limit

        # Track requests per API key
        current_time = time.time()
        key_requests = self.request_times.get(api_key, [])

        # Remove requests older than 1 minute
        key_requests = [req_time for req_time in key_requests if current_time - req_time < 60]

        # Check if rate limit is exceeded
        if len(key_requests) >= rate_limit:
            return False

        # Add current request
        key_requests.append(current_time)
        self.request_times[api_key] = key_requests

        return True


# Initialize the auth instance
api_key_auth = APIKeyAuth()
security = HTTPBearer(auto_error=False)


async def api_key_auth_middleware(request: Request, credentials: HTTPAuthorizationCredentials = security):
    """
    Middleware function to authenticate requests
    """
    # Skip auth for health checks and docs
    if request.url.path in ["/api/v1/health", "/health", "/docs", "/redoc", "/openapi.json"]:
        return

    # Authenticate the request
    is_authenticated = await api_key_auth.authenticate(request)
    if not is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    # Check rate limiting
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        api_key = auth_header[7:]
        if not api_key_auth.check_rate_limit(api_key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )

    # Continue with the request
    return