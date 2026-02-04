"""
Almira Backend - FastAPI Application
A secure, scalable e-commerce backend for fashion & jewelry.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app import __version__
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.cache import cache
from app.middleware.rate_limit import RateLimitMiddleware
from app.api.v1 import api_router

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"🚀 Starting {settings.app_name} v{__version__}")
    logger.info(f"🌍 Environment: {settings.app_env}")
    logger.info(f"🔧 Debug mode: {settings.debug}")

    # Connect to Redis
    await cache.connect()

    yield

    # Shutdown
    logger.info(f"👋 Shutting down {settings.app_name}")

    # Disconnect from Redis
    await cache.disconnect()


# Create FastAPI application
app = FastAPI(
    title=f"{settings.app_name} API",
    description="E-commerce API for fashion and jewelry",
    version=__version__,
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    openapi_url="/api/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)

# ===========================================
# MIDDLEWARE
# ===========================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
RateLimitMiddleware.setup(app)


# ===========================================
# EXCEPTION HANDLERS
# ===========================================

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    return RateLimitMiddleware.rate_limit_exceeded_handler(request, exc)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled error: {exc}", exc_info=True)

    # Don't expose internal errors in production
    if settings.is_production:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                },
            },
        )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(exc),
            },
        },
    )


# ===========================================
# ROUTES
# ===========================================

# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    from datetime import datetime

    return {
        "status": "healthy",
        "version": __version__,
        "environment": settings.app_env,
        "timestamp": datetime.utcnow().isoformat(),
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": settings.app_name,
        "version": __version__,
        "api_docs": f"{settings.api_v1_prefix}/docs" if settings.debug else None,
        "health": "/health",
    }


# ===========================================
# DEVELOPMENT SERVER
# ===========================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
