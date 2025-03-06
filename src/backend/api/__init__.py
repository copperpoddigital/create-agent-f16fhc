from fastapi import APIRouter, FastAPI

from .core.logging import logger  # Import logger
from .routes import router as main_router, setup_routes  # Import main API router

__version__ = "1.0.0"


# Create main API router
router = APIRouter()


# Include setup_routes function to configure all API routes
def setup_routes(app: FastAPI) -> None:
    """
    Configures all API routes by including sub-routers from different modules
    """
    # Include the main router in the FastAPI application
    app.include_router(main_router)

    # Log successful route configuration
    logger.info("API routes configured successfully")


# Export the main API router for inclusion in the FastAPI application
__all__ = ["router", "setup_routes", "__version__"]