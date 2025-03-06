# Standard library imports
import logging

# Third-party imports
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware  # version: 0.26.x
from starlette.middleware.trustedhost import TrustedHostMiddleware  # version: 0.26.x
from starlette.middleware.gzip import GZipMiddleware  # version: 0.26.x
import uvicorn  # version: 0.21.x

# Local application imports
from .core.config import settings  # Access application configuration settings
from .core.logging import setup_logging, get_logger  # Initialize application logging
from .core.db import initialize_db, create_all_tables, setup_timescaledb  # Initialize database connection
from .core.cache import initialize_cache  # Initialize Redis cache connection
from .api.routes import setup_routes  # Configure API routes
from .schemas.responses import HealthCheckResponse  # Define health check response schema

# Initialize logger for this module
logger = get_logger(__name__)

# Create a global settings object to be imported by other modules
# settings = Settings()

# Initialize the FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure TrustedHost middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# Configure GZip middleware for response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


def create_app() -> FastAPI:
    """
    Application factory function that creates and configures the FastAPI application

    Returns:
        fastapi.FastAPI: Configured FastAPI application instance
    """
    # Set up application logging
    setup_logging()

    # Create FastAPI application with title, version, and debug settings
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG
    )

    # Configure CORS middleware with allowed origins
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Configure TrustedHost middleware with allowed hosts
    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

    # Configure GZip middleware for response compression
    application.add_middleware(GZipMiddleware, minimum_size=1000)

    # Initialize database connection
    initialize_db()

    # Create database tables if they don't exist
    create_all_tables()

    # Set up TimescaleDB extensions
    setup_timescaledb()

    # Initialize Redis cache connection
    initialize_cache()

    # Set up API routes
    setup_routes(application)

    # Add health check endpoint
    @application.get("/health", response_model=HealthCheckResponse, tags=["Health"])
    async def health_check() -> dict:
        """
        Health check endpoint to verify application status

        Returns:
            dict: Health status information
        """
        # Check database connection health
        db_status = initialize_db().connect()

        # Check cache connection health
        cache_status = initialize_cache().ping()

        # Return health status with version information
        return {
            "status": "ok",
            "version": settings.APP_VERSION,
            "components": {
                "database": db_status,
                "cache": cache_status
            },
            "timestamp": datetime.utcnow()
        }

    # Log successful application initialization
    logger.info(f"Application '{settings.APP_NAME}' initialized successfully")

    # Return the configured application instance
    return application


app = create_app()


def main() -> None:
    """
    Entry point for running the application directly
    """
    # Create application using create_app()
    app = create_app()

    # Run application using uvicorn with host, port, and reload settings
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )


if __name__ == "__main__":
    main()