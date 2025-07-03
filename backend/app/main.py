"""Main FastAPI application entry point.

This module sets up the FastAPI app with all routers, middleware, and configurations.
Follows clean architecture principles with clear separation of concerns.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import health, auth, vapi, calendar


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    # Startup
    print(f"🚀 Starting {settings.app_name} in {settings.environment} mode")
    
    # TODO: Initialize database connection
    # TODO: Initialize Redis connection
    # TODO: Verify external service connections
    
    yield
    
    # Shutdown
    print("👋 Shutting down application")
    # TODO: Close database connections
    # TODO: Close Redis connections


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router, tags=["health"])
    app.include_router(
        auth.router,
        prefix=f"{settings.api_v1_prefix}/auth",
        tags=["authentication"]
    )
    app.include_router(
        vapi.router,
        prefix=f"{settings.api_v1_prefix}/vapi",
        tags=["voice"]
    )
    app.include_router(
        calendar.router,
        prefix=f"{settings.api_v1_prefix}/calendar",
        tags=["calendar"]
    )
    
    return app


# Create app instance
app = create_application()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": "0.1.0",
        "docs": "/docs" if settings.debug else None
    }