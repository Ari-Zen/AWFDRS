"""
FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.awfdrs.config import settings
from src.awfdrs.core.logging import setup_logging
from src.awfdrs.core.tracing import CorrelationIDMiddleware, RequestLoggingMiddleware
from src.awfdrs.core.exceptions import AWFDRSException
from src.awfdrs.db.session import close_db

# Import routers
from src.awfdrs.ingestion.api.v1.events import router as events_router
from src.awfdrs.ingestion.api.v1.health import router as health_router
from src.awfdrs.analysis.api.v1.incidents import router as incidents_router
from src.awfdrs.actions.api.v1.actions import router as actions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.

    Handles startup and shutdown tasks.
    """
    # Startup
    setup_logging(settings.log_level, use_json=True)
    yield
    # Shutdown
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Autonomous Workflow Failure Detection & Recovery System",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(RequestLoggingMiddleware)


# Exception handlers
@app.exception_handler(AWFDRSException)
async def awfdrs_exception_handler(request: Request, exc: AWFDRSException):
    """Handle custom AWFDRS exceptions."""
    correlation_id = getattr(request.state, "correlation_id", "unknown")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "correlation_id": correlation_id
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions."""
    correlation_id = getattr(request.state, "correlation_id", "unknown")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "details": {"message": str(exc)},
            "correlation_id": correlation_id
        }
    )


# Include routers
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(events_router, prefix="/api/v1", tags=["events"])
app.include_router(incidents_router, prefix="/api/v1", tags=["incidents"])
app.include_router(actions_router, prefix="/api/v1", tags=["actions"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }
