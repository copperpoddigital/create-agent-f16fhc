"""
Configuration module for the Freight Price Movement Agent backend.

This module serves as a bridge between the application and the core configuration module,
importing and re-exporting the settings for easier access throughout the application.

It provides utility functions for environment detection and configuration access.
"""

import os
import sys

# Import core configuration components
from .core.config import (
    settings, load_env_file, BASE_DIR
)

# Environment variables are loaded from .env file by core/config.py

# Re-export settings from core/config.py for easier imports

def get_environment() -> str:
    """
    Returns the current environment (development, staging, production).
    
    Returns:
        str: Current environment name
    """
    return settings.ENV or 'development'

def is_development() -> bool:
    """
    Checks if the current environment is development.
    
    Returns:
        bool: True if in development environment, False otherwise
    """
    return get_environment() == 'development'

def is_production() -> bool:
    """
    Checks if the current environment is production.
    
    Returns:
        bool: True if in production environment, False otherwise
    """
    return get_environment() == 'production'

def is_testing() -> bool:
    """
    Checks if the current environment is testing.
    
    Returns:
        bool: True if in testing environment, False otherwise
    """
    return 'pytest' in sys.modules