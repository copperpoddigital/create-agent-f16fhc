"""
Core module initialization file for the Freight Price Movement Agent backend.

Provides centralized imports and initialization of core components including
configuration, database, caching, security, logging, and utility functions.
"""

# Import configuration settings
from .config import settings

# Import logging components
from .logging import setup_logging, get_logger

# Import database components
from .db import initialize_db, get_db, Base, db

# Import cache components
from .cache import initialize_cache, cache_manager, cached

# Import exception classes
from .exceptions import (
    ApplicationException,
    ValidationException,
    NotFoundException,
    AuthenticationException,
    AuthorizationException
)

# Set up module logger
logger = get_logger(__name__)

def initialize_core():
    """
    Initializes all core components of the application.
    
    This function sets up logging, initializes the database connection,
    and prepares the cache system for use.
    
    Returns:
        None
    """
    # Set up logging system
    setup_logging()
    
    # Initialize database connection
    initialize_db()
    
    # Initialize cache system
    initialize_cache()
    
    logger.info("Core initialization complete")