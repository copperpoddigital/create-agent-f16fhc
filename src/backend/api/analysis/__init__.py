#!/usr/bin/env python3
# -*- coding: utf-8 -*-\n
"""
Initialization file for the analysis API module of the Freight Price Movement Agent.
This file initializes the router for analysis-related endpoints and registers route handlers for time periods, analysis requests, saved analyses, and analysis schedules.
"""

from fastapi import APIRouter  # version: ^0.95.0
from . import routes
from .routes import register_time_period_routes  # Logging for API initialization
from .routes import register_analysis_request_routes  # Logging for API initialization
from .routes import register_saved_analysis_routes  # Logging for API initialization
from .routes import register_schedule_routes  # Logging for API initialization
from ..core.logging import logger  # Logging for API initialization

# Define API version
__version__ = "0.1.0"

# Create an APIRouter instance with a prefix and tags
router = APIRouter(prefix="/analysis", tags=["Analysis"])


def init_module() -> None:
    """
    Initializes the analysis API module by registering all routes
    """
    logger.info("Initializing analysis API module")

    # Register time period routes
    register_time_period_routes(router)

    # Register analysis request routes
    register_analysis_request_routes(router)

    # Register saved analysis routes
    register_saved_analysis_routes(router)

    # Register schedule routes
    register_schedule_routes(router)

    logger.info("Analysis API module initialized and routes registered")


init_module()