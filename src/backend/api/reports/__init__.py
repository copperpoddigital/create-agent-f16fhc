#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initialization file for the reports API module of the Freight Price Movement Agent.
This file initializes the router for report-related endpoints and exports it for inclusion in the main API router.
It handles reports, report templates, scheduled reports, report sharing, and report executions.
"""

from fastapi import APIRouter  # version: 0.108.0

from .routes import router  # Import the reports router with all defined endpoints
from ..core.logging import logger  # Logging for API initialization

__version__ = "0.1.0"


def init_module() -> None:
    """
    Initializes the reports API module.
    """
    logger.info(f"Initializing reports API module version {__version__}")


init_module()
# Export the reports router for inclusion in the main API router
# Export the reports API version information
__all__ = ["router", "__version__"]