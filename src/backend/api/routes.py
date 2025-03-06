from fastapi import APIRouter, FastAPI

from .core.config import settings
from .core.logging import logger
from .auth import routes as auth_router
from .analysis import routes as analysis_router
from .data_sources import routes as data_sources_router
from .reports import routes as reports_router
from .admin import routes as admin_router


router = APIRouter(prefix=settings.API_PREFIX)


def setup_routes(app: FastAPI) -> None:
    """
    Configures all API routes by including sub-routers from different modules
    """
    # Include auth_router under the main router
    router.include_router(auth_router.router)

    # Include analysis_router under the main router
    router.include_router(analysis_router.router)

    # Include data_sources_router under the main router
    router.include_router(data_sources_router.router)

    # Include reports_router under the main router
    router.include_router(reports_router.router)

    # Include admin_router under the main router
    router.include_router(admin_router.admin_bp)

    # Include the main router in the FastAPI application
    app.include_router(router)

    # Log successful route configuration
    logger.info("API routes configured successfully")