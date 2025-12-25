from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.db.session import engine
from src.db.base import Base
from src.api.v1.endpoints import trends, analysis
import os
import logging

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables
    logger.info("Sankore Intelligence Layer Starting...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Debug Mode: {os.getenv('DEBUG', 'False')}")

    async with engine.begin() as conn:
        # Warning: fast-and-loose dev mode. Use Alembic for prod migrations.
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database initialized successfully")
    yield

    # Shutdown
    logger.info("Sankore Intelligence Layer Shutting Down...")
    await engine.dispose()

app = FastAPI(
    title="Sankore Intelligence API",
    description="Paid Ads Intelligence Layer for En Garde Platform",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("DEBUG", "False").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("DEBUG", "False").lower() == "true" else None,
)

# CORS configuration with environment-based origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# In development, allow all origins. In production, use specific origins.
if os.getenv("ENVIRONMENT", "development") == "production":
    logger.info(f"Production CORS enabled for origins: {allowed_origins}")
else:
    allowed_origins = ["*"]
    logger.warning("Development mode: CORS allows all origins")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(trends.router, prefix="/api/v1/trends", tags=["trends"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and Railway deployment.

    Returns:
        dict: Service status and version information
    """
    return {
        "status": "healthy",
        "service": "Sankore Intelligence Layer",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/")
async def root():
    """
    Root endpoint with API information.

    Returns:
        dict: API welcome message and documentation links
    """
    return {
        "message": "Sankore Intelligence API",
        "version": "0.1.0",
        "docs": "/docs" if os.getenv("DEBUG", "False").lower() == "true" else "Documentation disabled in production",
        "health": "/health"
    }
