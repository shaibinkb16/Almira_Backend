"""
Rate limiting middleware using SlowAPI.
Prevents abuse by limiting request frequency.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.core.config import settings


def get_client_ip(request: Request) -> str:
    """
    Get client IP address, considering proxies.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address string
    """
    # Check for forwarded IP (from reverse proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fall back to direct connection IP
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_client_ip,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
)


class RateLimitMiddleware:
    """
    Rate limiting middleware configuration.
    """

    @staticmethod
    def setup(app):
        """
        Set up rate limiting on the FastAPI app.

        Args:
            app: FastAPI application instance
        """
        app.state.limiter = limiter
        app.add_middleware(SlowAPIMiddleware)

    @staticmethod
    def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
        """
        Handler for rate limit exceeded errors.

        Args:
            request: The request that triggered the limit
            exc: The rate limit exception

        Returns:
            JSON response with error details
        """
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please slow down.",
                    "retry_after": exc.detail,
                },
            },
            headers={"Retry-After": str(exc.detail)},
        )


# Decorator for custom rate limits on specific endpoints
def rate_limit(limit: str):
    """
    Decorator for applying custom rate limits to endpoints.

    Args:
        limit: Rate limit string (e.g., "5/minute", "100/hour")

    Returns:
        Rate limit decorator
    """
    return limiter.limit(limit)
