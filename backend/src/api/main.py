"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .routes import router
from ..core.config import settings
from ..core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Nepal Government RAG Assistant API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    
    # Startup: Initialize components
    from .dependencies import (
        get_embedding_model,
        get_vector_store,
        get_llm_provider,
    )
    
    try:
        # Warm up models
        get_embedding_model()
        get_vector_store()
        get_llm_provider()
        logger.info("All components initialized successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Nepal Government RAG Assistant API")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="RAG-based assistant for Nepal Government Services",
    lifespan=lifespan,
)

# CORS middleware
allowed_origins = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1", tags=["rag"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }
